#!/usr/bin/env python3
"""
SDN Traffic Monitoring and Flow Analysis Mini-Project
File: topo.py
Description: Custom Mininet topology containing 1 OpenFlow switch (s1)
             and 4 hosts (h1, h2, h3, h4) connected to a Remote POX Controller.
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class CustomSDNTopo(Topo):
    """
    Custom SDN Topology:
         h1 ---\
         h2 ----\
                 [ s1 (Switch) ] <=======> [ POX Controller (Remote) ]
         h3 ----/
         h4 ---/
    """
    def build(self):
        # 1. Add the OpenFlow switch with a fixed Datapath ID (dpid)
        info("*** Creating OpenFlow Switch: s1\n")
        switch = self.addSwitch('s1', dpid='0000000000000001')

        # 2. Add 4 hosts with custom IP addresses (10.0.0.1 to 10.0.0.4)
        info("*** Creating 4 Hosts (h1, h2, h3, h4)...\n")
        hosts = []
        for i in range(1, 5):
            host = self.addHost(f'h{i}', ip=f'10.0.0.{i}/24')
            hosts.append(host)

        # 3. Connect hosts to the switch
        info("*** Creating Links connecting hosts to the switch...\n")
        for host in hosts:
            self.addLink(host, switch)

def run_network():
    """
    Initializes and starts the Mininet network with the custom topology.
    It links Mininet to the remote POX controller and starts the interactive CLI.
    """
    # Instantiate the topology
    topo = CustomSDNTopo()
    
    # Configure and start Mininet
    # We use OVSKernelSwitch (Open vSwitch) and target POX running on localhost (127.0.0.1:6633)
    info("*** Initializing Mininet and connecting to POX Controller...\n")
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6633),
        waitConnected=True
    )
    
    # Start the network switches and controllers
    info("*** Starting the Network...\n")
    net.start()
    
    # Open the Mininet Command Line Interface (CLI) for manual traffic generation
    info("\n*** SDN Network Active. Use the CLI below to run tests (e.g., 'pingall', 'h1 iperf -s & h2 iperf -c h1').\n")
    CLI(net)
    
    # Clean up and stop the network after exiting CLI
    info("*** Shutting down Mininet network...\n")
    net.stop()

if __name__ == '__main__':
    # Set logging level to 'info' to output clear progress statements
    setLogLevel('info')
    run_network()
