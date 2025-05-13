from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.term import makeTerm
from mininet.link import TCLink


def run():
    net = Mininet(controller=None)
    h1 = net.addHost('h1', ip='192.168.0.1/28')
    h2 = net.addHost('h2', ip='192.168.0.2/28')
    s1 = net.addSwitch('s1', failMode='standalone')
    net.addLink(h1, s1, cls=TCLink, loss=10)
    net.addLink(h2, s1)
    net.start()

    h1, h2 = net.get('h1', 'h2')

    makeTerm(
        h2,
        title="server",
        cmd=(
            'python3 ../start-server.py '
            '-H 192.168.0.2 -p 8081 -s ../demo/srv -r saw; exec bash'
        )
    )

    while True:
        while input("¿Quieres iniciar el cliente? (y/n): ").strip().lower() != 'y':
            print("Esperando a que inicies el cliente...")

        makeTerm(
                h1,
                title="client",
                cmd=(
                    'time python3 ../upload.py -H 192.168.0.2 -p 8081 '
                    '-s ../demo/media/5mb.jpg -n 5mbu1.jpg -r saw; exec bash'
                )
            )
        makeTerm(
                h1,
                title="client",
                cmd=(
                    'time python3 ../upload.py -H 192.168.0.2 -p 8081 '
                    '-s ../demo/media/5mb1.jpg -n 5mbu2.jpg -r gbn; exec bash'
                )
            )
        makeTerm(
                h1,
                title="client",
                cmd=(
                    'time python3 ../download.py -H 192.168.0.2 -p 8081 '
                    '-d ../demo/clnt/5mbd1.jpg -n 5mb.jpg -r gbn; exec bash'
                )
            )
        makeTerm(
                h1,
                title="client",
                cmd=(
                    'time python3 ../download.py -H 192.168.0.2 -p 8081 '
                    '-d ../demo/clnt/5mbd2.jpg -n 5mb1.jpg -r saw; exec bash'
                )
            )

        done = input("¿Terminaste? (y/n): ").strip().lower()
        if done == 'y':
            break

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
