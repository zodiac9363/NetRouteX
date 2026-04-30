# NetRouteX - Packet Forwarding Smiulator


NetRouteX is a real-time network simulation tool that visualizes how routers forward packets using Longest Prefix Match (LPM).

It transforms complex routing logic into an interactive and intuitive experience, making it ideal for learning and demonstration.

# Features
 * IPv4 Packet Forwarding Simulation
 * Live Routing Table Lookup Visualization
 * Longest Prefix Match (LPM) Selection
 * Step-by-Step Packet Flow Animation
 * Status Indicators (MATCH / NO MATCH / CHECKING)
 * Execution Logs for Debugging & Learning
 * Concepts Demonstrated
 * Routing Tables
 * Longest Prefix Match (LPM)
 * Packet Switching
 * Next Hop Resolution
 * Interface-Based Routing
# Tech Stack
  * Python
  * Streamlit
  * Pandas
  * ipaddress
# Installation
git clone https://github.com/zodiac9363/NetRouteX
cd netroutex
pip install -r requirements.txt

# Run the Application
streamlit run app.py

#How It Works
Enter Source and Destination IP addresses
System validates the input
Routing table is scanned in real-time
Matching routes are identified
Best route selected using LPM
Packet forwarding is animated step-by-step
Final decision (FORWARDED / DROPPED) is displayed

# Visual Representation
https://github.com/zodiac9363/NetRouteX/blob/main/netroute%20x.gif

# Example
Destination IP	Result
10.0.0.25	Matches 10.0.0.0/24 (Best Route)

# Project Structure
netroutex/
│── app.py
│── requirements.txt
│── README.md

# Use Cases
Computer Networks learning
Academic demonstrations
Interview project showcase
Concept visualization for LPM

# Future Enhancements
Editable routing tables
IPv6 support
Multi-router simulation
Graph-based network topology
Performance metrics dashboard

