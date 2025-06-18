from mininet.topo import Topo

DEFAULT_SWITCHES = 1

# n siendo la cantidad de switches (por defecto 1)
# sudo mn --custom ./switch-topo.py --topo switch-topo,n --controller remote

class SwitchTopo(Topo):
    """ Topología con 4 hosts unidos por una linea de n switches """

    def __init__(self, n=DEFAULT_SWITCHES):
        Topo.__init__(self)

        switch = self.addSwitch("s1")

        self.addLink(switch, self.addHost("h1"))
        self.addLink(switch, self.addHost("h2"))

        for i in range(DEFAULT_SWITCHES + 1, n + 1):
            next_switch = self.addSwitch(f"s{i}")
            self.addLink(switch, next_switch)
            switch = next_switch

        self.addLink(switch, self.addHost("h3"))
        self.addLink(switch, self.addHost("h4"))

topos = {
    "switch-topo": (
        lambda switch_number=DEFAULT_SWITCHES: SwitchTopo(switch_number)
    )
}