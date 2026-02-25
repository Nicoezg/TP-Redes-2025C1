# TP-Redes-2025C1

Trabajos prácticos de la materia **Redes** (código 9560 / TA048) de la [Facultad de Ingeniería de la Universidad de Buenos Aires (FIUBA)](https://fi.uba.ar/), correspondientes al primer cuatrimestre de 2025.

---

## Contenido del repositorio

El repositorio está organizado en ramas separadas, una por cada trabajo práctico:

| Rama  | Trabajo Práctico | Tema |
|-------|-----------------|------|
| [`tp1`](../../tree/tp1) | TP1 | Transferencia de archivos confiable sobre UDP |
| [`tp2`](../../tree/tp2) | TP2 | Redes definidas por software (SDN) con POX y Mininet |

---

## TP1 — Transferencia de archivos confiable sobre UDP

**Rama:** [`tp1`](../../tree/tp1)

Implementación de un sistema de transferencia de archivos cliente-servidor sobre UDP, con un protocolo de transferencia confiable (RDT) desarrollado desde cero en Python. Se utiliza **Mininet** para simular la red y evaluar el comportamiento ante pérdida de paquetes.

### Estructura

```
src/
├── start-server.py      # Script para iniciar el servidor
├── upload.py            # Script cliente para subir archivos
├── download.py          # Script cliente para descargar archivos
├── lib/
│   ├── server.py        # Lógica del servidor
│   ├── client.py        # Lógica del cliente
│   ├── rdt_protocol.py  # Protocolo de transferencia confiable (RDT)
│   ├── file_protocol.py # Protocolo de transferencia de archivos
│   ├── packet.py        # Definición de paquetes
│   └── common.py        # Utilidades comunes
├── mininet/             # Configuración de topología para Mininet
└── demo/                # Scripts de prueba con Mininet
```

### Requisitos

- Python 3
- Mininet

### Ejecución

```bash
# Iniciar el servidor
cd src
python3 start-server.py -H <HOST> -p <PORT> -s <STORAGE> [-r <PROTOCOL>]

# Subir un archivo
python3 upload.py -H <HOST> -p <PORT> -s <SRC> -n <NAME> [-r <PROTOCOL>]

# Descargar un archivo
python3 download.py -H <HOST> -p <PORT> -d <DST> -n <NAME> [-r <PROTOCOL>]

# Prueba con Mininet
cd demo
sudo python3 test.py
```

---

## TP2 — Redes definidas por software (SDN)

**Rama:** [`tp2`](../../tree/tp2)

Implementación de un firewall sobre un switch L2 con aprendizaje automático de direcciones MAC, utilizando el controlador SDN **POX** y **Mininet**. Se definen reglas de filtrado de tráfico por host de origen, protocolo de transporte y puerto destino.

El informe completo se encuentra en [`Informe_Redes_TP2.pdf`](../../blob/tp2/Informe_Redes_TP2.pdf).

### Estructura

```
pox/
├── pox.py               # Script principal del controlador POX
├── switch-topo.py       # Definición de topología de red para Mininet
├── ext/                 # Módulos de extensión (firewall, forwarding)
└── ...
```

### Requisitos

- Python 3
- POX (incluido en el repositorio)
- Mininet
- Open vSwitch

### Ejecución

```bash
# Levantar el controlador POX con firewall
cd pox
./pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning firewall

# Levantar la topología en Mininet (en otra terminal)
sudo mn --custom ./switch-topo.py --topo switch-topo,2 --mac --arp --switch ovsk --controller remote
```

### Reglas de firewall implementadas

- Bloqueo de tráfico entre h1 y h2.
- Bloqueo de tráfico UDP con puerto destino 5001 originado en h1.
- Bloqueo de tráfico con puerto destino 80.

---

## Autor

**Nicolás Grüner** — [@Nicoezg](https://github.com/Nicoezg)

---

## Materia

- **Materia:** Redes (9560 / TA048)
- **Institución:** FIUBA — Facultad de Ingeniería, Universidad de Buenos Aires
- **Cuatrimestre:** 1C 2025