#!/usr/bin/env python3
from mininet.node import Node
from mininet.topo import Topo

DEFAULT_CLIENT_NUMBER = 1
DO_NOT_MODIFY_MTU = -1
DEFAULT_GATEWAY_CLIENTS_SIDE = "10.0.1.254"
DEFAULT_GATEWAY_SERVER_SIDE = "10.0.0.254"


class Router(Node):
    def config(self, **params):
        super(Router, self).config(**params)

        self.cmd("sysctl -w net.ipv4.ip_forward=1")
        self.cmd(f"ifconfig {self.name}-eth0 {DEFAULT_GATEWAY_SERVER_SIDE}/24")
        self.cmd(f"ifconfig {self.name}-eth1 {DEFAULT_GATEWAY_CLIENTS_SIDE}/24")

        if params.get("mtu", DO_NOT_MODIFY_MTU) != DO_NOT_MODIFY_MTU:
            self.cmd(f"ifconfig {self.name}-eth0 mtu {params.get('mtu')}")

        # allow all ICMP messages
        self.cmd("iptables -A INPUT -p icmp -j ACCEPT")
        self.cmd("iptables -A OUTPUT -p icmp -j ACCEPT")
        self.cmd("iptables -A FORWARD -p icmp -j ACCEPT")
        self.cmd(
            "iptables -I OUTPUT -p icmp --icmp-type fragmentation-needed -j ACCEPT"
        )

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super(Router, self).terminate()


class Host(Node):
    def config(self, **params):
        super(Host, self).config(**params)

        # Disable PMTU discovery on hosts to allow fragmentation
        self.cmd("sysctl -w net.ipv4.ip_no_pmtu_disc=1")
        self.cmd("ip route flush cache")

    def terminate(self):
        super(Host, self).terminate()


class LinearEndsTopo(Topo):
    def build(
        self,
        client_number=DEFAULT_CLIENT_NUMBER,
        mtu=DO_NOT_MODIFY_MTU,
    ):
        # add switches & router
        s1 = self.addSwitch("s1")
        s2 = self.addNode(
            "s2",
            ip=f"{DEFAULT_GATEWAY_SERVER_SIDE}/24",
            cls=Router,
            client_number=client_number,
            mtu=mtu,
        )
        s3 = self.addSwitch("s3")

        # set links between switches & router
        self.addLink(s1, s2)
        self.addLink(s2, s3, loss=10)

        h1_server = self.addHost(
            "h1",
            ip="10.0.0.1/24",
            defaultRoute=f"via {DEFAULT_GATEWAY_SERVER_SIDE}",
            cls=Host,
        )

        # set link server-s1
        self.addLink(h1_server, s1)

        # set links for each client and the s3
        # 1 is added because the server is taken into account
        for i in range(1, client_number + 1):
            host_client_i = self.addHost(
                f"h{i + 1}",
                ip=f"10.0.1.{i}/24",
                defaultRoute=f"via {DEFAULT_GATEWAY_CLIENTS_SIDE}",  # router's eth1 interface
                cls=Host,
            )
            self.addLink(host_client_i, s3)


topos = {
    "linends": (
        lambda client_number=DEFAULT_CLIENT_NUMBER,
        mtu=DO_NOT_MODIFY_MTU: LinearEndsTopo(client_number, mtu)
    )
}
