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



log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ[ 'HOME' ]

''' Add your global variables here ... '''



class Firewall (EventMixin):

    def __init__ (self):
        self.listenTo(core.openflow)
        log.debug("Enabling Firewall Module")

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

"""     def _handle_PacketIn(self, event):
        packet = event.parsed
        if packet and packet.type == packet.IP_TYPE:
            ip_packet = packet.payload

            if ip_packet.protocol == ip_packet.TCP_PROTOCOL:
                tcp_packet = ip_packet.payload
                
                if tcp_packet.dstport == 80:
                    # Drop packet by not sending any actions
                    msg = of.ofp_flow_mod()
                    msg.actions = []           # No actions = drop
                    event.connection.send(msg)
                    return
      
            elif ip_packet.protocol == ip_packet.UDP_PROTOCOL:
                udp_packet = ip_packet.payload

                if udp_packet.dstport == 80:
                    # Drop packet by not sending any actions
                    msg = of.ofp_flow_mod()
                    msg.actions = []  # No actions = drop
                    event.connection.send(msg)
                    return

                if udp_packet.dstport == 5001 and ip_packet.srcip == EthAddr("00:00:00:00:00:01"):
                    # Drop packet by not sending any actions
                    msg = of.ofp_flow_mod()
                    msg.actions = []
                    event.connection.send(msg)
                    return
            
            if (
                    (ip_packet.srcip == EthAddr("00:00:00:00:00:01") and ip_packet.dstip == EthAddr("00:00:00:00:00:02")) or
                    (ip_packet.srcip == EthAddr("00:00:00:00:00:02") and ip_packet.dstip == EthAddr("00:00:00:00:00:01"))
                ):
                    # Drop packet by not sending any actions
                    msg = of.ofp_flow_mod()
                    msg.match.dl_type = 0x800
                    msg.actions = []
                    return 
        return """
                
        

def launch ():
    '''
    Starting the Firewall module
    '''
    core.registerNew(Firewall)