#!/usr/bin/env python3
"""
SDN Traffic Monitoring and Flow Analysis Mini-Project
File: sdn_monitor.py
Description: Custom POX controller module that periodically requests flow statistics
             from all connected OpenFlow switches and displays traffic details (source IP,
             destination IP, protocol type, packet counts, and byte counts).
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.recoco import Timer
from pox.lib.addresses import IPAddr

# Initialize POX logger
log = core.getLogger()

class SDNTrafficMonitor(object):
    """
    Monitors traffic by sending periodic flow statistics queries to OpenFlow switches.
    Parses responses and outputs a formatted table.
    """
    def __init__(self, interval=5):
        # Register for OpenFlow events (like ConnectionUp, FlowStatsReceived)
        core.openflow.addListeners(self)
        self.interval = interval
        
        # Schedule the stats collector to run every 'interval' seconds
        # Using POX's cooperative scheduler (recoco) Timer
        Timer(self.interval, self.request_stats, recurring=True)
        log.info("SDN Traffic Monitor initialized. Query interval: %d seconds.", self.interval)

    def _handle_ConnectionUp(self, event):
        """
        Triggered when a switch connects to the POX controller.
        """
        log.info("Switch s1 (DPID: %s) has successfully connected to the controller.", event.dpid)

    def request_stats(self):
        """
        Periodically requests statistics from all active switches.
        """
        connections = core.openflow._connections.values()
        if not connections:
            log.debug("No switches connected. Waiting for switch connection...")
            return

        for connection in connections:
            log.info("Requesting flow statistics from Switch DPID: %s...", connection.dpid)
            
            # Create standard OpenFlow 1.0 flow statistics request.
            # When the switch receives this, it collects stats for all active flows
            # and replies with a FlowStatsReceived event.
            req = of.ofp_stats_request(body=of.ofp_flow_stats_request())
            connection.send(req)

    def _handle_FlowStatsReceived(self, event):
        """
        Triggered when flow statistics are received from the switch.
        Parses flows and formats them into a readable report.
        """
        stats = event.stats
        dpid = event.dpid
        
        # Initialize summary metrics
        total_packets = 0
        total_bytes = 0
        active_flows = 0

        # Calculate totals
        for flow in stats:
            total_packets += flow.packet_count
            total_bytes += flow.byte_count
            active_flows += 1

        # Print the reporting header
        print("\n" + "=" * 85)
        print(" MONITORING REPORT - SWITCH DPID: {:016x}".format(dpid))
        print("=" * 85)
        print("Summary statistics:")
        print("  - Active Flow Rules : {}".format(active_flows))
        print("  - Total Packets      : {}".format(total_packets))
        print("  - Total Bytes        : {} bytes ({:.2f} KB)".format(total_bytes, total_bytes / 1024.0))
        print("=" * 85)

        if active_flows == 0:
            print(" No active flow entries in switch flow table. (Send some traffic to see stats!)")
            print("=" * 85 + "\n")
            return

        # Print detailed flow table headers
        # Formatted spacing: Src IP, Dst IP, Proto, Packets, Bytes, Duration(s)
        header_fmt = "| {:<18} | {:<18} | {:<8} | {:<10} | {:<10} | {:<8} |"
        row_fmt    = "| {:<18} | {:<18} | {:<8} | {:<10} | {:<10} | {:<8} |"
        
        print(header_fmt.format("Source IP", "Destination IP", "Protocol", "Packets", "Bytes", "Age (s)"))
        print("-" * 85)

        for flow in stats:
            match = flow.match
            
            # Resolve Source and Destination IP addresses
            src_ip = str(match.nw_src) if match.nw_src is not None else "Any"
            dst_ip = str(match.nw_dst) if match.nw_dst is not None else "Any"
            
            # Resolve Network Protocol (TCP, UDP, ICMP, ARP, etc.)
            proto = "Any"
            if match.dl_type == 0x0806:
                proto = "ARP"
            elif match.nw_proto == 1:
                proto = "ICMP"
            elif match.nw_proto == 6:
                proto = "TCP"
            elif match.nw_proto == 17:
                proto = "UDP"
            elif match.nw_proto is not None:
                proto = "IP (Proto:{})".format(match.nw_proto)
            elif match.dl_type == 0x0800:
                proto = "IPv4"

            # Calculate total flow age in seconds (seconds + nanoseconds fraction)
            duration = flow.duration_sec + (flow.duration_nsec / 1e9)
            
            print(row_fmt.format(
                src_ip,
                dst_ip,
                proto,
                flow.packet_count,
                flow.byte_count,
                "{:.2f}".format(duration)
            ))
            
        print("=" * 85 + "\n")

def launch(interval=5):
    """
    Launches the POX monitoring component.
    This function is automatically called by POX when loading the module.
    Usage: python3 pox.py forwarding.l2_learning sdn_monitor --interval=5
    """
    # Register the monitoring module with core POX system
    core.registerNew(SDNTrafficMonitor, interval=int(interval))
