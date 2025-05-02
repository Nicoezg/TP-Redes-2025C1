from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.term import makeTerm

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

    makeTerm(h2, title="server", cmd= 'python3 ../src/start-server.py -H 192.168.0.2 -p 8081 -s ../demo/srv -v; exec bash')
    
    while True:
        operacion = input('What do you want to do? (upload/download): ')
        if operacion == 'upload':
            makeTerm(h1, title="client", cmd= 'python3 ../src/upload.py -H 192.168.0.2 -p 8081 -s media/5mb.jpeg -n 5mb.jpeg -r gbn -v; exec bash')
        elif operacion == 'download':
            makeTerm(h1, title="client", cmd= 'python3 ../src/download.py -H 192.168.0.2 -p 8081 -d ../demo/media/5mb.jpeg -n 5mb.jpeg -r gbn -v; exec bash')
        
        done = input("¿Terminaste? (y/n): ").strip().lower()
        if done == 'y':
            break

    # Upload:
    #(en h2) python3 ../src/start-server.py -H 192.168.0.2 -p 8081 -s ../demo/srv -v
    #(en h1) python3 ../src/upload.py -H 192.168.0.2 -p 8081 -s /media/4mb.pdf -n 4mb.pdf -r gbn -v

    # Download:
    # (en h1) python3 ../src/download.py -H 192.168.0.2 -p 8081 -d ../demo/clnt/4mb.pdf -n 4mb.pdf -r gbn -v
   
    
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()

