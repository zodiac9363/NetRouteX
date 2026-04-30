# NetRouteX – Packet Forwarding Simulator

NetRouteX is a real-time network simulation tool that visualizes how routers forward packets using Longest Prefix Match (LPM).
It provides an interactive way to understand routing decisions and packet flow in modern networks.

---

## Visual Demo

![Visual Demo](https://raw.githubusercontent.com/zodiac9363/NetRouteX/main/netroute%20x.gif)

---

## Features

* IPv4 packet forwarding simulation
* Real-time routing table lookup visualization
* Longest Prefix Match (LPM) based route selection
* Step-by-step packet flow animation
* Status indicators (MATCH / NO MATCH / CHECKING)
* Execution logs for debugging and learning

---

## Concepts Demonstrated

* Routing tables
* Longest Prefix Match (LPM)
* Packet switching
* Next hop resolution
* Interface-based routing

---

## Tech Stack

* Python
* Streamlit
* Pandas
* ipaddress

---

## Installation

```bash
git clone https://github.com/zodiac9363/NetRouteX
cd netroutex
pip install -r requirements.txt
```

---

## Run the Application

```bash
streamlit run app.py
```

---

## How It Works

1. Enter source and destination IP addresses
2. The system validates the input
3. The routing table is scanned in real time
4. Matching routes are identified
5. The best route is selected using LPM
6. Packet forwarding is animated step by step
7. Final decision (FORWARDED or DROPPED) is displayed

---

## Example

| Destination IP | Result                           |
| -------------- | -------------------------------- |
| 10.0.0.25      | Matches 10.0.0.0/24 (Best Route) |

---

## Project Structure

```
netroutex/
│── app.py
│── requirements.txt
│── README.md
```

---

## Use Cases

* Computer networks learning
* Academic demonstrations
* Interview project showcase
* Concept visualization for routing logic

---

## Future Enhancements

* Editable routing tables
* IPv6 support
* Multi-router simulation
* Graph-based network topology
* Performance metrics dashboard
