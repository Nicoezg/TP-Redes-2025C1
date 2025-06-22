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
from pox.lib.addresses import IPAddr
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4
from rule import Rule
import json


log = core.getLogger()
policyFile = "ext/firewall-policies.json"
protocol_dict = {
    'tcp': ipv4.TCP_PROTOCOL,
    'udp': ipv4.UDP_PROTOCOL,
    'icmp': ipv4.ICMP_PROTOCOL
}

class Firewall (object):
    """
    A Firewall object is created for each switch that connects.
    An Event object for that connection is passed to the __init__ function.
    """

    def __init__ (self, event, rules):
        # Keep track of connection to switch.
        self.connection = event.connection

        # Bind PacketIn event listener.
        event.connection.addListeners(self)

        for rule in rules:
            self.install_flow(rule)
        log.debug("Installed rules on switch %s", str(event.connection.dpid))

    def install_flow(self, rule):
        log.info("Installing packet dropping rules: %s", rule)

        msg = of.ofp_flow_mod()
        match = of.ofp_match()
        is_ip = False # Flag if rule is for IP packet

        if rule.ip_src is not None:
            match.nw_src = IPAddr(rule.ip_src)
            is_ip = True
        if rule.ip_dst is not None:
            match.nw_dst = IPAddr(rule.ip_dst)
            is_ip = True
        if rule.protocol is not None:
            match.nw_proto = protocol_dict[rule.protocol]
            is_ip = True
            if rule.port_src is not None:
                match.tp_src = rule.port_src
            if rule.port_dst is not None:
                match.tp_dst = rule.port_dst

        if is_ip:
            match.dl_type = ethernet.IP_TYPE

        msg.match = match
        msg.priority = 49152
        self.connection.send(msg)

def launch():
    '''
    Starting the Firewall module
    '''
    log.debug("Opening policy file with rules to install: %s", policyFile)
    with open(policyFile) as f:
        data = json.load(f)

        switch_id = data["switch_id"]
        rules = []

        for rule in data["rules"]:
            new_rule = dict(rule)
            rules.append(Rule(new_rule))

    def on_switch_up(event):
        dpid = event.connection.dpid
        if dpid == switch_id:
            log.info("Switch %d connected (firewall)", dpid)
            Firewall(event, rules)
        else:
            log.info("Switch %d connected", dpid)

    # Automagically calls Firewall(event).
    core.openflow.addListenerByName("ConnectionUp", on_switch_up)
