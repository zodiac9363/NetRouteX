import ipaddress
import time
import pandas as pd
import streamlit as st


ROUTING_TABLE = [
    {"network": "10.0.0.0/24", "next_hop": "192.168.2.1", "interface": "eth0"},
    {"network": "10.0.0.0/16", "next_hop": "192.168.2.254", "interface": "eth2"},
    {"network": "172.16.0.0/16", "next_hop": "192.168.3.1", "interface": "eth1"},
    {"network": "192.168.1.0/24", "next_hop": "192.168.4.1", "interface": "eth3"},
]


def validate_ipv4(value: str) -> tuple[ipaddress.IPv4Address | None, str | None]:
    """Return parsed IPv4Address and optional error."""
    try:
        parsed = ipaddress.ip_address(value.strip())
    except ValueError:
        return None, "Invalid IPv4 format"

    if parsed.version != 4:
        return None, "Only IPv4 supported"

    return parsed, None


def build_lookup_results(destination_ip: ipaddress.IPv4Address) -> list[dict]:
    """Evaluate destination against each route."""
    results = []
    for row in ROUTING_TABLE:
        network = ipaddress.ip_network(row["network"], strict=False)
        results.append(
            {
                "network": row["network"],
                "next_hop": row["next_hop"],
                "interface": row["interface"],
                "network_obj": network,
                "prefix_len": network.prefixlen,
                "match": destination_ip in network,
            }
        )
    return results


def select_best_route(results: list[dict]) -> dict | None:
    """Longest Prefix Match selection."""
    matched = [item for item in results if item["match"]]
    if not matched:
        return None
    return max(matched, key=lambda item: item["prefix_len"])


def table_rows() -> list[dict]:
    """Create routing table rows for dataframe rendering."""
    return [
        {"Network": r["network"], "Next Hop": r["next_hop"], "Interface": r["interface"]}
        for r in ROUTING_TABLE
    ]


def build_lookup_dataframe(results: list[dict], current_idx: int | None) -> pd.DataFrame:
    """Create lookup dataframe with progressive status updates."""
    rows = []
    for idx, row in enumerate(results):
        if current_idx is None or idx < current_idx:
            status = "MATCH" if row["match"] else "NO MATCH"
        elif idx == current_idx:
            status = "CHECKING"
        else:
            status = "PENDING"
        rows.append(
            {
                "Network": row["network"],
                "Next Hop": row["next_hop"],
                "Interface": row["interface"],
                "Status": status,
                "_active": idx == current_idx,
            }
        )
    return pd.DataFrame(rows)


def style_lookup_dataframe(df: pd.DataFrame):
    """Apply row and status highlighting for live lookup panel."""
    active_map = df["_active"].to_dict()

    def style_row(row):
        active_row = active_map.get(row.name, False)
        status = row["Status"]
        base = [""] * len(row)
        if active_row:
            # Dark highlight keeps text readable in dark theme.
            base = ["background-color: #1b2a41; color: #f5f7fa"] * len(row)

        status_col = row.index.get_loc("Status")
        if status == "MATCH":
            base[status_col] = f"{base[status_col]}; color: #1b5e20; font-weight: 700"
        elif status == "NO MATCH":
            base[status_col] = f"{base[status_col]}; color: #b71c1c; font-weight: 700"
        elif status == "CHECKING":
            base[status_col] = f"{base[status_col]}; color: #0d47a1; font-weight: 700"
        return base

    visible_df = df.drop(columns=["_active"])
    return visible_df.style.apply(style_row, axis=1)


def run_live_lookup(
    results: list[dict], logs: list[str], lookup_placeholder, delay: float = 0.5
) -> None:
    """Render route checks one-by-one with highlighted active row."""
    for idx, row in enumerate(results):
        live_df = build_lookup_dataframe(results, idx)
        lookup_placeholder.dataframe(
            style_lookup_dataframe(live_df),
            use_container_width=True,
            hide_index=True,
        )
        logs.append(f"RT_LOOKUP route={row['network']} result={'MATCH' if row['match'] else 'NO_MATCH'}")
        time.sleep(delay)

    # Final frame: all rows resolved, no active CHECKING row.
    final_df = build_lookup_dataframe(results, None)
    lookup_placeholder.dataframe(
        style_lookup_dataframe(final_df),
        use_container_width=True,
        hide_index=True,
    )


def render_route_selection(results: list[dict], selected: dict | None) -> None:
    """Display all matches and selected route by prefix length."""
    st.markdown("**Route Selection**")
    matched = [r for r in results if r["match"]]
    if not matched:
        st.markdown(
            "<div style='border:1px solid #3a3d46;border-radius:8px;padding:8px;'>No matching routes</div>",
            unsafe_allow_html=True,
        )
        return

    rows = []
    for row in sorted(matched, key=lambda x: x["prefix_len"], reverse=True):
        selected_tag = "SELECTED" if selected and row["network"] == selected["network"] else ""
        selected_style = "color:#0ea5e9;font-weight:700;" if selected_tag else "color:#c7c9d1;"
        rows.append(
            {
                "Network": row["network"],
                "Prefix": f"/{row['prefix_len']}",
                "Next Hop": row["next_hop"],
                "Interface": row["interface"],
                "State": selected_tag,
            }
        )
        if selected_tag:
            st.markdown(
                f"<div style='margin-bottom:6px;{selected_style}'>Best Prefix: {row['network']} ({row['prefix_len']})</div>",
                unsafe_allow_html=True,
            )

    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_flow_state(
    step: int, source_ip: str, destination_ip: str, selected: dict | None
) -> str:
    """Return flow layout using real IP and route data."""
    forwarded = selected is not None
    next_hop = selected["next_hop"] if selected else "NO_ROUTE"
    router_label = f"Router ({selected['interface']})" if selected else "Router (Drop)"

    nodes = [
        ("Source IP", source_ip),
        ("Router", router_label),
        ("Next Hop", next_hop),
        ("Destination IP", destination_ip),
    ]

    def node_style(index: int) -> str:
        if index == step:
            return "background:#11324d;border:1px solid #1d8fff;color:#f5f7fa;"
        if not forwarded and index >= 2 and step >= 2:
            return "background:#3a1212;border:1px solid #a63a3a;color:#f5d0d0;"
        if index < step:
            return "background:#132a1b;border:1px solid #2f855a;color:#d7ffe8;"
        return "background:#171a21;border:1px solid #2a2d34;color:#d9dde5;"

    def box(index: int, title: str, value: str) -> str:
        return (
            f"<div style='flex:1;border-radius:10px;padding:10px;{node_style(index)}'>"
            f"<div style='font-size:11px;opacity:0.85;margin-bottom:3px;'>{title}</div>"
            f"<div style='font-size:14px;font-weight:600;'>{value}</div>"
            "</div>"
        )

    return f"""
    <div style="display:flex;align-items:center;gap:8px;">
        {box(0, nodes[0][0], nodes[0][1])}
        <div style="font-size:16px;color:#8b95a7;">-></div>
        {box(1, nodes[1][0], nodes[1][1])}
        <div style="font-size:16px;color:#8b95a7;">-></div>
        {box(2, nodes[2][0], nodes[2][1])}
        <div style="font-size:16px;color:#8b95a7;">-></div>
        {box(3, nodes[3][0], nodes[3][1])}
    </div>
    """


def run_packet_flow(
    source_ip: str, destination_ip: str, selected: dict | None, logs: list[str]
) -> None:
    """Animate packet flow with route-mapped labels."""
    flow_placeholder = st.empty()
    forwarded = selected is not None

    steps = [
        "FLOW source_ready",
        "FLOW source_to_router",
        "FLOW routing_decision",
        "FLOW forward" if forwarded else "FLOW drop",
    ]

    for index, log_line in enumerate(steps):
        flow_placeholder.markdown(
            render_flow_state(index, source_ip, destination_ip, selected), unsafe_allow_html=True
        )
        logs.append(log_line)
        time.sleep(0.45)


def render_decision(selected: dict | None) -> None:
    """Show final forwarding decision."""
    if selected:
        st.markdown(
            """
            <div style="border:1px solid #1f8b4c;border-radius:8px;padding:10px;">
                <b>Status:</b> FORWARDED
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(
            [
                {
                    "Selected Network": selected["network"],
                    "Next Hop": selected["next_hop"],
                    "Interface": selected["interface"],
                    "Prefix": f"/{selected['prefix_len']}",
                }
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.markdown(
            """
            <div style="border:1px solid #b42318;border-radius:8px;padding:10px;">
                <b>Status:</b> DROPPED | Reason: NO_ROUTE
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(page_title="Packet Forwarding Simulator", layout="wide")
    st.title("Packet Forwarding Simulator")

    with st.container(border=True):
        st.subheader("Input Panel")
        col_src, col_dst = st.columns(2)
        with col_src:
            src_text = st.text_input("Source IP", placeholder="192.168.1.10", label_visibility="visible")
            src_error_slot = st.empty()
        with col_dst:
            dst_text = st.text_input("Destination IP", placeholder="10.0.0.25", label_visibility="visible")
            dst_error_slot = st.empty()
        send = st.button("Send Packet", type="primary", use_container_width=False)

    st.divider()

    left, right = st.columns([1.25, 1], gap="medium")
    with left:
        with st.container(border=True):
            st.subheader("Routing Table")
            st.dataframe(table_rows(), use_container_width=True, hide_index=True)

    with right:
        with st.container(border=True):
            st.subheader("Live Lookup Panel")
            lookup_idle_placeholder = st.empty()
            lookup_idle_placeholder.caption("Idle")

    if not send:
        return

    logs: list[str] = []
    src_error_slot.empty()
    dst_error_slot.empty()

    src_ip, src_err = validate_ipv4(src_text)
    dst_ip, dst_err = validate_ipv4(dst_text)

    has_error = False
    if src_err:
        src_error_slot.error(src_err, icon=None)
        has_error = True
    if dst_err:
        dst_error_slot.error(dst_err, icon=None)
        has_error = True
    if has_error:
        return

    logs.append(f"RX src={src_ip} dst={dst_ip}")
    logs.append("RT_LOOKUP start")

    results = build_lookup_results(dst_ip)
    run_live_lookup(results, logs, lookup_idle_placeholder)

    selected = select_best_route(results)
    logs.append(f"RT_SELECT {'found' if selected else 'none'}")

    st.divider()

    with st.container(border=True):
        st.subheader("Flow Simulation")
        run_packet_flow(str(src_ip), str(dst_ip), selected, logs)

    with st.container(border=True):
        render_route_selection(results, selected)

    with st.container(border=True):
        st.subheader("Forwarding Decision")
        render_decision(selected)

    with st.expander("Logs", expanded=False):
        for line in logs:
            st.code(line, language="text")


if __name__ == "__main__":
    main()
