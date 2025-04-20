from mininet.topo import Topo

class MyTopo( Topo ):
    "Topología lineal formada por dos hosts conectados a traves de 3 switches."

    def build( self ):

        leftHost = self.addHost( 'h1' )
        rightHost = self.addHost( 'h2' )
        firstSwitch = self.addSwitch( 's1' )
        secondSwitch = self.addSwitch( 's2' )
        thirdSwitch = self.addSwitch( 's3' )

        self.addLink( leftHost, firstSwitch )
        self.addLink( firstSwitch, secondSwitch )
        self.addLink( secondSwitch, thirdSwitch )
        self.addLink( thirdSwitch, rightHost )


topos = { 'mytopo': ( lambda: MyTopo() ) }