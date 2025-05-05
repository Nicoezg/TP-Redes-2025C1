from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import Topo
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel
import subprocess
import signal

DO_NOT_MODIFY_MTU = -1
DEFAULT_GATEWAY_CLIENTS_SIDE = "10.0.1.254"
DEFAULT_GATEWAY_SERVER_SIDE = "10.0.0.254"

def start_capture(interface, outfile):
    cmd = [
        'sudo', 'tshark',
        '-i', interface,
        '-f', 'not port 22 and not port 123 and not port 6633 and not port 6653',
        '-w', outfile
    ]
    return subprocess.Popen(cmd)

class Router(Node):
    def config(self, **params):
        super(Router, self).config(**params)

        self.cmd("sysctl -w net.ipv4.ip_forward=1")
        self.cmd(f"ifconfig {self.name}-eth0 {DEFAULT_GATEWAY_SERVER_SIDE}/24")
        self.cmd(
            f"ifconfig {self.name}-eth1 {DEFAULT_GATEWAY_CLIENTS_SIDE}/24"
        )

        if params.get("mtu", DO_NOT_MODIFY_MTU) != DO_NOT_MODIFY_MTU:
            self.cmd(f"ifconfig {self.name}-eth0 mtu {params.get('mtu')}")

        # allow all ICMP messages
        self.cmd("iptables -A INPUT -p icmp -j ACCEPT")
        self.cmd("iptables -A OUTPUT -p icmp -j ACCEPT")
        self.cmd("iptables -A FORWARD -p icmp -j ACCEPT")
        self.cmd(
            (
                "iptables -I OUTPUT -p icmp "
                "--icmp-type fragmentation-needed -j ACCEPT"
            )
        )

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super(Router, self).terminate()


class Host(Node):
    def config(self, **params):
        super(Host, self).config(**params)

        # Disable PMTU discovery on hosts to allow fragmentation
        self.cmd("sysctl -w net.ipv4.ip_no_pmtu_disc=1")
        # Disable TCP MTU probing
        self.cmd("sysctl -w net.ipv4.tcp_mtu_probing=0")
        self.cmd("ip route flush cache")

    def terminate(self):
        super(Host, self).terminate()


class LinearEndsTopo(Topo):
    def build(self):
        # add switches & router
        s1 = self.addSwitch("s1")
        s2 = self.addNode(
            "s2",
            ip=f"{DEFAULT_GATEWAY_SERVER_SIDE}/24",
            cls=Router,
            client_number=1,
            mtu=1000,
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

        h2_client = self.addHost("h2", ip="10.0.1.1/24", defaultRoute=f"via {DEFAULT_GATEWAY_CLIENTS_SIDE}", cls=Host)
        self.addLink(h2_client, s3)

def run():
    topo = LinearEndsTopo()
    net = Mininet(topo=topo, link=TCLink, switch=OVSSwitch)
    net.start()

    tshark_proc1 = start_capture('s1-eth2', '/tmp/1-tcp.pcapng')
    tshark_proc2 = start_capture('s3-eth1', '/tmp/2-tcp.pcapng')

    h1, h2 = net.get('h1'), net.get('h2')

    h1.cmd('iperf -s &')
    h2.cmd(f'iperf -c {h1.IP()} -l 1400 -n 10K -t 1')

    tshark_proc1.send_signal(signal.SIGKILL)
    tshark_proc2.send_signal(signal.SIGKILL)
    tshark_proc1.wait(timeout=10)
    tshark_proc2.wait(timeout=10)

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
