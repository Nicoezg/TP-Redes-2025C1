# TP-Redes-2025C1

## Guia para ejecutar el proyecto:

### Requisitos previos:

- Tener instalado Python3
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


``` bash
python3 download.py [-h] [-v | -q] -H HOST -p PORT -d DST -n NAME [-r PROTOCOL]
```

6. Para probar el cliente y el servidor con mininet, ejecutar el siguiente comando:

``` bash
cd demo
sudo python3 test.py
```

Aqui se le preguntará si desea hacer un upload o download. Se debe escribir por consola una de las opciones. Notemos que el archivo que se prueba es el que se llama `5mb.jpg`, que se encuentra en la carpeta `media`. El cliente almacenará las descargas en la carpeta `clnt` mientras que el servidor lo hará en la carpeta `srv`. Es importante aclarar que para realizar una descarga, el archivo tiene que estar presente en la carpeta `srv` (tiene que estar previamente subido haciendo upload).
