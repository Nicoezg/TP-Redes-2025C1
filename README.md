# TP-Redes-2025C1

## Instrucciones

Levantar POX primero:

```
./pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning firewall
```

Para levantar mininet:

```
sudo mn --custom ./switch-topo.py --topo switch-topo,2 --mac --arp --switch ovsk --controller remote
```

