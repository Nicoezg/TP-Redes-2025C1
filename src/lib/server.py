from logging import Logger
import os
import socket
import threading
from lib import common as c
from lib import file_protocol
from lib import rdt_protocol

UPLOAD = 0
DOWNLOAD = 1
BUFFER_SIZE = 1500

class Server:
    def __init__(self, ip, port, storage, logger: Logger, protocol):
        self.ip = ip
        self.port = int(port)
        self.storage = storage
        self.logger = logger
        self.protocol = protocol

        self.clients = {}
        self.threads = {}

    def run_server(self):
        try:
            c.validate_addr(self.ip, self.port)
            c.validate_storage(self.storage)

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.ip, self.port))
      
            self.logger.info(f"Server listening on {self.ip} : {self.port}")
            self.logger.info("Server run successful!")

            self.listen_client(self.port)

        except Exception as e:
            self.logger.error(f"Server error: {e}")

    def listen_client(self, addr):
        while True:
            try:
                data, client_addr = self.sock.recvfrom(BUFFER_SIZE)
                if not data:
                    break
                self.logger.info(f"Received data from {client_addr}: {data}")
                if client_addr not in self.clients:
                    self.logger.info(f"New client connected: {client_addr}")
                    self.new_client(data, client_addr)
                    self.threads[client_addr].start()

            except Exception as e:
                self.logger.error(f"Error receiving data: {e}")
                break

    def new_client(self, data, addr):
        op, file_name, proto, file_size = file_protocol.decode_request(data)
        error_code = 0

        if op == UPLOAD:
            self.logger.info(f"Client {addr} requested upload of {file_name}")

            if proto == 0:
                peer = rdt_protocol.GBNPeer((self.ip, 0), rdt_protocol.READ_MODE, win_size=1)
            else:
                peer = rdt_protocol.GBNPeer((self.ip, 0), rdt_protocol.READ_MODE)

            _, upload_port = peer.sock.getsockname()

            self.logger.info(f"Assigned port {upload_port} for upload from {addr}")

            # Acá chequear por errores (si hay error settear error_code a un valor != 0)
            response = file_protocol.encode_response(error_code, upload_port)
            self.sock.sendto(response, addr)

            thread = threading.Thread(target=self.handle_upload, args=(peer, file_name, addr, file_size))
            self.threads[addr] = thread
            self.clients[addr] = peer
        elif op == DOWNLOAD:
            # Fijarse que exista el path y demas (si hay error settear error_code a un valor != 0)
            try:
                file_size = os.path.getsize(self.storage+"/"+file_name)
                response = file_protocol.encode_response(error_code, 0, file_size)
                self.sock.sendto(response, addr)

                self.logger.info(f"Client {addr} requested download of {file_name}")
                if proto == 0:
                    peer = rdt_protocol.GBNPeer(addr, rdt_protocol.WRITE_MODE, win_size=1)
                else:
                    peer = rdt_protocol.GBNPeer(addr, rdt_protocol.WRITE_MODE)
                _, download_port = peer.sock.getsockname()
                self.logger.info(f"Assigned port {download_port} for download to {addr}")
                self.threads[addr] = threading.Thread(target=self.handle_download, args=(peer, file_name, addr))
                self.clients[addr] = peer
            except FileNotFoundError:
                self.logger.error(f"File {file_name} not found")
                error_code = 1
                response = file_protocol.encode_response(error_code,0,0)
                self.sock.sendto(response, addr)
            

    def handle_upload(self, peer, file_name, client_addr, file_size):
        received_size = 0

        with open(f"{self.storage}/{file_name}", "wb") as f:
            while True:
                try:
                    data = peer.recv(timeout=5)
                    if not data:
                        break
                    f.write(data)
                    received_size += len(data)
                    if received_size >= file_size:
                        break
            
                except Exception as e:
                    self.logger.warning(f"Error receiving file: {e}")
                    break

    def handle_download(self, peer, file_name, client_addr):
        try:
            with open(f"{self.storage}/{file_name}", "rb") as f:
                while True:
                    data = f.read(1496)
                    if not data:
                        break
                    peer.send(data)
                    self.logger.info(f"Sent data: {data} to {client_addr}")
        except Exception as e:
            self.logger.error(f"Error sending file: {e}")

    def stop_server(self):
        for client in self.clients.values():
            client.stop()
        for thread in self.threads.values():
            thread.join()
        self.sock.close()
        self.logger.info("Server stopped")
