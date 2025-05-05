from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel
from time import sleep
import subprocess
import signal
import os
import select

class TestTopo(Topo):
    def build(self):

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        s1 = self.addSwitch('s1')

        self.addLink(h1, s1, loss=10)
        self.addLink(s1, h2)

def start_capture(interface, outfile):
    cmd = [
        'sudo', 'tshark',
        '-i', interface,
        '-f', 'udp and not port 22 and not port 123 and not port 6633 and not port 6653',
        '-w', outfile
    ]
    return subprocess.Popen(cmd)

def run():
    topo = TestTopo()
    net = Mininet(topo=topo, link=TCLink, switch=OVSSwitch)
    net.start()

    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'

    tshark_proc = start_capture('s1-eth2', '/tmp/uptest.pcapng')
    sleep(2)

    h1, h2 = net.get('h1'), net.get('h2')

    print("*** Starting server")
    srv_cmd = "python3 ../src/start-server.py -H 0.0.0.0 -p 8081 -s ../demo/srv -v"
    server = h2.popen(srv_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, env=env)
    sleep(3)
    print("*** Server output:")
    timeout = 5
    for _ in range(10):  # Read up to 10 lines to see if it starts
        ready, _, _ = select.select([server.stdout], [], [], timeout)
        if not ready:
            break
        print(server.stdout.readline().strip())

    print("*** Starting client")
    client_cmd = f'python3 ../src/upload.py -H {h2.IP()} -p 8081 -s media/5mb.jpg -n 5mb.jpg -r gbn -v'
    client_log = '/tmp/uplog.txt'
    with open(client_log, 'w') as log:
        client = h1.popen(client_cmd, stdout=log, stderr=log, universal_newlines=True, env=env)
    timeout = 10
    while True:
        ready, _, _ = select.select([server.stdout], [], [], timeout)
        if not ready:
            break
        print(server.stdout.readline().strip())

    client.wait(timeout=60)

    print("*** Terminating server...")
    server.terminate()

    tshark_proc.send_signal(signal.SIGKILL)
    tshark_proc.wait(timeout=10)

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
