from mininet.net import Mininet
from mininet.log import setLogLevel



def run():
    
    net = Mininet(controller=None )
    h1 = net.addHost(  'h1', ip='192.168.0.1/28')
    h2 = net.addHost(  'h2', ip= '192.168.0.2/28')
    s1 = net.addSwitch( 's1', failMode='standalone' )
    net.addLink(h1, s1, loss=10)
    net.addLink( h2, s1)
    net.start()
      
    h1, h2 = net.get('h1', 'h2')
    #TODO: Hacer que las xterm tengan nombres distintos (h1 y h2)
    h1.cmd('xterm &')
    h2.cmd('xterm &')
    # Upload:
    #(en h2) python3 ../src/start-server.py -H 192.168.0.2 -p 8081 -s ../demo/srv -v
    #(en h1) python3 ../src/upload.py -H 192.168.0.2 -p 8081 -s /media/4mb.pdf -n 4mb.pdf -r gbn -v

    # Download:
    # (en h1) python3 ../src/download.py -H 192.168.0.2 -p 8081 -d ../demo/clnt/4mb.pdf -n 4mb.pdf -r gbn -v
    while input('Done? (y/n): ') != 'y':
        pass
    
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()