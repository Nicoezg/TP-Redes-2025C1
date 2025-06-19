'''
Coursera:
- Software Defined Networking (SDN) course
-- Programming Assignment: Layer-2 Firewall Application

Professor: Nick Feamster
Teaching Assistant: Arpit Gupta
'''

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os
from pox.lib.addresses import IPAddr
''' Add your imports here ... '''
# Constants for Ethernet header values
from pox.lib.packet.ethernet import ethernet
# Constants for IPv4 header values
from pox.lib.packet.ipv4 import ipv4


log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ[ 'HOME' ]

''' Add your global variables here ... '''
RULES_BY_DPID = {
    1: [
        {"nw_proto": 6, "tp_dst": 80, "action": "deny"},
        {"nw_proto": 17, "tp_dst": 80, "action": "deny"},
        {"nw_proto": 17, "nw_src": IPAddr("10.0.0.1"), "tp_dst": 5001, "action": "deny"},
    ],
}



class Firewall (object):
    """
    A Firewall object is created for each switch that connects.
    An Event object for that connection is passed to the __init__ function.
    """

    def __init__ (self, event):
        log.debug("Starting firewall instance for connection %s (switch ID: %s)",\
                event.connection,\
                dpidToStr(event.dpid))

        # Keep track of connection to switch.
        self.connection = event.connection

        # Bind PacketIn event listener
        # (and eventually others?).
        event.connection.addListeners(self)


    def _handle_PacketIn(self, event):
        in_port = event.port
        dpid = event.connection.dpid # Unique ID for the switch.
        packet = event.parsed

        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        log.debug("Processing packet for connection %s (switch ID: %s)",\
                self.connection,\
                str(dpid))

        fields = self.extract_fields(packet)

        rules = RULES_BY_DPID.get(dpid)
        if rules:
            #log.debug("%s rules for dpid %s", str(len(rules)), str(dpid))
            for rule in rules:
                if self.check_matches(rule, fields):
                    log.debug("Packet matched rule: %s", rule)
                    if rule["action"] == "deny":
                        self.drop_packet(event.ofp, in_port)
                        self.install_flow(rule)
                        return


        # Default: allow/flood
        #log.debug("Packet allowed through firewall")
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        msg.in_port = in_port
        self.connection.send(msg)


    def extract_fields(self, packet):
        # Basic fields
        fields = {
            "eth_type": packet.type,
            "nw_proto": None, # Transport protocol
            "nw_src": None, # IP src
            "nw_dst": None, # IP dst
            "tp_src": None, # src port
            "tp_dst": None, # dst port
        }

        if fields["eth_type"] == ethernet.IP_TYPE:
            ip_pkt = packet.payload
            fields["nw_proto"] = ip_pkt.protocol
            fields["nw_src"] = ip_pkt.srcip
            fields["nw_dst"] = ip_pkt.dstip

            if fields["nw_proto"] == ipv4.TCP_PROTOCOL\
            or fields["nw_proto"] == ipv4.UDP_PROTOCOL:
                transport_pkt = ip_pkt.payload
                fields["tp_src"] = transport_pkt.srcport
                fields["tp_dst"] = transport_pkt.dstport

        return fields


    def check_matches(self, rule, fields):
        for field, val in rule.items():
            if field == "action": # Don't compare action
                continue
            if val == "any":
                continue
            if val != fields.get(field):
                return False
        return True


    def drop_packet(self, data, port):
        msg = of.ofp_packet_out()
        msg.data = data
        msg.in_port = port
        # No actions = drop
        self.connection.send(msg)


    def install_flow(self, rule):
        if rule.get("action") != "deny":
            log.warning("Non-deny actions not implemented")
            return

        msg = of.ofp_flow_mod()
        match = of.ofp_match()
        is_ip = False # Flag if rule is for IP packet

        if "nw_src" in rule:
            match.nw_src = rule["nw_src"]
            is_ip = True
        if "nw_dst" in rule:
            match.nw_dst = rule["nw_dst"]
            is_ip = True
        if "nw_proto" in rule:
            match.nw_proto = rule["nw_proto"]
            is_ip = True
            if "tp_src" in rule:
                match.tp_src = rule["tp_src"]
            if "tp_dst" in rule:
                match.tp_dst = rule["tp_dst"]

        if is_ip:
            match.dl_type = ethernet.IP_TYPE

        msg.match = match
        msg.priority = 49152 # No idea how this field works
        self.connection.send(msg)

    """
    def _handle_ConnectionUp (self, event):

        # Drop all TCP traffic to port 80
        msg = of.ofp_flow_mod()
        msg.match.dl_type = 0x800
        msg.match.nw_proto = 6  # TCP
        msg.match.tp_dst = 80
        msg.actions = []
        event.connection.send(msg)

        # Drop all UDP traffic to port 80
        msg = of.ofp_flow_mod()
        msg.match.dl_type = 0x800
        msg.match.nw_proto = 17  # UDP
        msg.match.tp_dst = 80
        msg.actions = []
        event.connection.send(msg)

        # Drop UDP port 5001 traffic from 10.0.0.1 (h1 in mininet)
        msg = of.ofp_flow_mod()
        msg.match.dl_type = 0x800
        msg.match.nw_proto = 17  # UDP
        msg.match.nw_src = IPAddr("10.0.0.1")
        msg.match.tp_dst = 5001
        msg.actions = []
        event.connection.send(msg)
    """

def launch ():
    '''
    Starting the Firewall module
    '''
    # Automagically calls Firewall(event).
    core.openflow.addListenerByName("ConnectionUp", Firewall)
