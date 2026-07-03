# Traffic Monitoring and Flow Analysis in Software Defined Networks (SDN)

A beginner-friendly mini-project utilizing **Mininet** (for network emulation), the **POX Controller** (for network intelligence), the **OpenFlow 1.0 protocol** (for communication), and **Python** on Ubuntu.

---

## 1. Project Overview & Objectives

In traditional networks, the control plane (deciding where traffic goes) and the data plane (forwarding packets) are bundled together inside proprietary hardware switches. Software Defined Networking (SDN) breaks this paradigm by decoupling them:
- **Control Plane**: Handled by a centralized software controller (e.g., POX).
- **Data Plane**: Handled by programmable switches (e.g., Open vSwitch).
- **Communication Protocol**: OpenFlow.

### Objectives of this Mini-Project:
1. Build a custom network topology (1 OpenFlow switch connected to 4 hosts) using Mininet.
2. Configure a centralized **POX Controller** that runs a Layer-2 learning switch application.
3. Write a custom **POX Monitoring Module** (`sdn_monitor.py`) to periodically query the switch, collect flow statistics (packet count, byte count, active flows), and display traffic stats.
4. Test and verify network traffic using standard utilities like `ping` and `iperf`.

---

## 2. System Architecture

```mermaid
graph TD
    subgraph Control Plane (Centralized Software)
        POX[POX Controller]
        Monitor[Traffic Monitor Module sdn_monitor.py]
        Forwarding[L2 Learning Switch Component]
        POX --- Monitor
        POX --- Forwarding
    end

    subgraph Data Plane (Network Emulation)
        s1[OpenFlow Switch s1]
        h1[Host h1 - 10.0.0.1]
        h2[Host h2 - 10.0.0.2]
        h3[Host h3 - 10.0.0.3]
        h4[Host h4 - 10.0.0.4]

        s1 --- h1
        s1 --- h2
        s1 --- h3
        s1 --- h4
    end

    POX <== OpenFlow 1.0 Protocol / Port 6633 ==> s1
```

---

## 3. System Requirements & Installation

This project is built and tested on **Ubuntu Linux (20.04 LTS / 22.04 LTS / 24.04 LTS)**.

### Step 1: Install Mininet and Open vSwitch
Open a terminal in Ubuntu and run:
```bash
sudo apt-get update
sudo apt-get install -y mininet openvswitch-switch
```
Verify the installation by checking version numbers:
```bash
mn --version
```

### Step 2: Clone the POX Controller Repository
POX runs on Python. Clone the official repository to your home directory:
```bash
cd ~
git clone https://github.com/noxrepo/pox.git
```
*Note: The official POX repository contains a `pox` directory where you run commands.*

---

## 4. Project File Structure
Place the two Python scripts provided in this repository as follows:
1. **`topo.py`**: Save it in any directory (e.g., `~/sdn_project/topo.py`).
2. **`sdn_monitor.py`**: Save it inside the **`pox/ext/`** directory (e.g., `~/pox/ext/sdn_monitor.py`). The `ext/` directory is POX's custom extensions directory where POX looks for user components.

```text
~/
├── pox/
│   ├── pox.py
│   └── ext/
│       └── sdn_monitor.py    <-- Place monitoring script here
│
└── sdn_project/
    └── topo.py               <-- Place topology script here
```

---

## 5. Step-by-Step Execution Guide

To run the project, you need **two terminal windows** open in Ubuntu.

### Step 1: Start the POX Controller (Terminal 1)
First, run the POX controller with both the custom monitoring module (`sdn_monitor.py`) and the standard `l2_learning` forwarding application (so the switch knows how to forward packets).

Navigate to the `pox` directory and launch it:
```bash
cd ~/pox
python3 pox.py forwarding.l2_learning sdn_monitor --interval=5
```
*Parameters:*
- `forwarding.l2_learning`: Tells POX to act as a self-learning Ethernet switch.
- `sdn_monitor`: Loads our custom monitoring component.
- `--interval=5`: Sets the traffic monitoring table update interval to 5 seconds.

### Step 2: Start the Mininet Network (Terminal 2)
In a separate terminal window, launch our custom topology script. Since Mininet creates virtual network interfaces, it must be run with `sudo` privileges.

Navigate to your project directory and run:
```bash
cd ~/sdn_project
sudo python3 topo.py
```
This will start Mininet, configure switch `s1`, connect it to the POX controller at `127.0.0.1:6633`, create hosts `h1`-`h4`, and launch the interactive **Mininet CLI** (`mininet>`).

---

## 6. Traffic Testing & Monitoring

Once both scripts are running, you will observe the traffic monitoring output in **Terminal 1 (POX)**.

### Test 1: Generate Ping Traffic
In the Mininet CLI (Terminal 2), check that all hosts can talk to each other:
```bash
mininet> pingall
```
You will see hosts sending ARP and ICMP packets. In Terminal 1, the controller will print statistics showing how rules are created for routing.

To run a specific ping test between host 1 and host 2:
```bash
mininet> h1 ping -c 4 h2
```
Look at **Terminal 1 (POX)**. You will see a detailed flow report appearing:
```text
=====================================================================================
 MONITORING REPORT - SWITCH DPID: 0000000000000001
=====================================================================================
Summary statistics:
  - Active Flow Rules : 2
  - Total Packets      : 8
  - Total Bytes        : 784 bytes (0.77 KB)
=====================================================================================
| Source IP          | Destination IP     | Protocol | Packets    | Bytes      | Age (s)  |
-------------------------------------------------------------------------------------
| 10.0.0.1           | 10.0.0.2           | ICMP     | 4          | 392        | 3.20     |
| 10.0.0.2           | 10.0.0.1           | ICMP     | 4          | 392        | 3.20     |
=====================================================================================
```

### Test 2: High Traffic Testing with iperf
To simulate file transfer or video stream bandwidth, generate TCP traffic between `h1` (acting as server) and `h3` (acting as client).
In the Mininet CLI:
```bash
mininet> iperf h1 h3
```
This runs a 10-second TCP bandwidth test. Watch the output in **Terminal 1 (POX)**. You will see a large packet and byte count representing the TCP transfer!
```text
=====================================================================================
 MONITORING REPORT - SWITCH DPID: 0000000000000001
=====================================================================================
Summary statistics:
  - Active Flow Rules : 2
  - Total Packets      : 45120
  - Total Bytes        : 68131200 bytes (65000.00 KB)
=====================================================================================
| Source IP          | Destination IP     | Protocol | Packets    | Bytes      | Age (s)  |
-------------------------------------------------------------------------------------
| 10.0.0.1           | 10.0.0.3           | TCP      | 15040      | 22710400   | 8.40     |
| 10.0.0.3           | 10.0.0.1           | TCP      | 30080      | 45420800   | 8.40     |
=====================================================================================
```

---

## 7. How the Code Works (Explanation)

### A. Mininet Custom Topology (`topo.py`)
- **`Topo` Class**: Represents the structure of the network. We override its `build()` method.
- **`self.addSwitch('s1')`**: Spawns an Open vSwitch instance named `s1`.
- **`self.addHost('hX')`**: Configures virtual host namespaces with specific IPs.
- **`RemoteController`**: Directs the switch `s1` to look for an out-of-band controller listening on IP `127.0.0.1` and Port `6633` (the POX default).
- **`CLI(net)`**: Drops the user into an interactive command shell to trigger network events.

### B. POX Traffic Monitor (`sdn_monitor.py`)
- **`core.openflow.addListeners(self)`**: Registers this module to listen to OpenFlow events triggered by connected switches.
- **`Timer(self.interval, self.request_stats, recurring=True)`**: Sets up a background thread that executes `request_stats()` every 5 seconds.
- **`ofp_stats_request`**: Creates an OpenFlow statistics request. Sending it to the switch asks: *"Give me metadata on all entries currently in your flow table."*
- **`_handle_FlowStatsReceived(self, event)`**: Callback function that fires when the switch replies. The event contains `event.stats`, which is a list of flows. We iterate through them, parse fields (matching IP headers, protocol types), increment totals, and print the output in an ASCII table.

---

## 8. Common Errors & Troubleshooting

### Error 1: `Exception: Error creating interface...` or Switch Fails to Start
- **Reason**: Mininet didn't shut down cleanly in a previous run, leaving stale interfaces or dead switch processes.
- **Fix**: Run the Mininet clean command:
  ```bash
  sudo mn -c
  ```

### Error 2: `Address already in use` (Cannot start POX Controller)
- **Reason**: Another controller process or POX instance is already running and using port `6633`.
- **Fix**: Identify and kill the process using port 6633:
  ```bash
  sudo killall python3 python
  ```
  *(Alternative)*: Run `sudo lsof -i :6633` to find the exact Process ID (PID) and execute `sudo kill -9 <PID>`.

### Error 3: No flows showing up in the table after pinging
- **Reason**: OpenFlow rules expire quickly if inactive (idle timeout). Alternatively, POX's learning switch is running but no traffic is being sent.
- **Fix**: Run `h1 ping -t h2` (continuous ping) in Mininet CLI, and then watch the POX console.

---

## 9. Viva Voce Preparation Guide (Q&A)

Here are the most common questions college examiners ask during project reviews:

1. **Q: What is a controller in SDN?**
   - **A**: The controller is the "brain" of the network. It runs application logic, maintains a global view of the network topology, and programs switches by installing flow rules in their tables.

2. **Q: What is the purpose of OpenFlow?**
   - **A**: OpenFlow is the standardized Southbound API/protocol used by the controller to communicate with network switches. It allows the controller to add, update, and delete packet-forwarding rules in the switch flow table.

3. **Q: How does a switch handle a packet when its flow table is empty?**
   - **A**: When a packet arrives and matches no existing rules, it triggers a **Packet-In** event. The switch encapsulates the packet header and sends it to the POX controller. The controller decides how to route it, installs a new flow entry in the switch, and tells the switch to forward the packet.

4. **Q: What is the difference between `packet_count` and `byte_count`?**
   - **A**: `packet_count` tracks the total number of network packets matching a rule, while `byte_count` measures the cumulative volume of data in bytes. These are useful for traffic monitoring, billing, and detecting Denial of Service (DoS) attacks.
