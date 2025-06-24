# TP-Redes-2025C1

## Instrucciones

Dentro de la carpeta pox:

Levantar POX primero:

```
./pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning firewall
```

Para levantar mininet:

```
sudo mn --custom ./switch-topo.py --topo switch-topo,2 --mac --arp --switch ovsk --controller remote
```

Con esto, levantaremos mininet y abrirá la CLI.

Dentro de ella, podemos probar las distintas reglas corriendo los siguientes comandos:

### Conexión bloqueada entre h1 y h2
```
h2 iperf -s -u&

h1 iperf -c h2 -u 
```
En wireshark, si capturamos el tráfico en s1-eth1, deberíamos ver como los paquetes se mandan. Si capturamos en s1-eth2, no deberíamos ver tráfico de h1.

### Si es UDP, puerto destino 5001 y sale de h1, se bloquean los paquetes
```
h3 iperf -s -p 5001 -u&

h1 iperf -c h3 -p 5001 -u
```
En wireshark, si capturamos el tráfico en s1-eth1, deberíamos ver como los paquetes se mandan. Si capturamos en s1-eth3, no deberíamos ver tráfico de h1.

### Si se cambia a puerto 5000 si llegan los paquetes
```
h3 iperf -s -p 5000 -u&

h1 iperf -c h3 -p 5000 -u
```

### Si el puerto destino es 80 no pasan los paquetes
```
h1 iperf -s -p 80&

h3 iperf -c h1 -p 80
``` 
En wireshark, si capturamos el tráfico en s1-eth1, deberíamos ver como los paquetes se mandan. Si capturamos en s1-eth3, no deberíamos ver tráfico de h1.


