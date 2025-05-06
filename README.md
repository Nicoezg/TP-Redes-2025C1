# TP-Redes-2025C1

## Guia para ejecutar el proyecto:

### Requisitos previos:

- Tener instalado Python 3
- Tener instalado mininet

### Comandos para ejecutar el proyecto:

1. Estar parados en la carpeta del proyecto

``` bash
cd path_to_tp
cd src
```

2. Para ver los argumentos que se pueden pasar al script de inicio del servidor, ejecutar el siguiente comando:

``` bash

python3 start-server.py -h
```

3. Para iniciar el servidor, ejecutar el siguiente comando:

``` bash
python3 start-server.py [-h] [-v | -q] -H HOST -p PORT -s STORAGE [-r PROTOCOL]
```

4. Para ver los argumentos que se pueden pasar al script de inicio del cliente, ejecutar el siguiente comando:

``` bash
python3 upload.py -h
```
o

``` bash
python3 download.py -h
```

5. Para iniciar el cliente, ejecutar el siguiente comando:

``` bash
python3 upload.py [-h] [-v | -q] -H HOST -p PORT -s SRC -n NAME [-r PROTOCOL]
```
o

``` bash
python3 download.py [-h] [-v | -q] -H HOST -p PORT -d DST -n NAME [-r PROTOCOL]
```

6. Para probar el cliente y el servidor con mininet, ejecutar el siguiente comando:

``` bash
cd ..
cd demo
python3 test.py
```

Aqui se le preguntara si se desea hacer un uploado o un download. Se debe escribir por la consola correspondiente que se desea elegir. Notemos que el archivo que se prueba es el que se llama 5mb.jpg, que se encuentra en la carpeta media. Para asegurarse que funcione el test. Si quiere hacer un upload, copie el archivo 5mb.jpg en la carpeta clnt y se subira a la carpeta srv. Si quiere hacer un download, copie el archivo 5mb.jpg en la carpeta srv y se bajara a la carpeta clnt.
