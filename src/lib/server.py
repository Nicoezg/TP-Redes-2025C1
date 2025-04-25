from logging import Logger
import socket
import threading
from lib import common as c

BUFFER_SIZE = 1024


class Server:
    def __init__(self, ip, port, storage, logger: Logger):
        self.ip = ip
        self.port = int(port)
        self.storage = storage
        self.logger = logger

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
                if client_addr in self.clients:
                    self.clients[client_addr].push(data)
                else: 
                    self.logger.info(f"New client connected: {client_addr}")
                    pass
                    #self.new_client(data, client_addr)

            except Exception as e:
                self.logger.error(f"Error receiving data: {e}")
                break

    def new_client(self, data, addr):
        #manejar un nuevo cliente segun el protocolo que elija
        pass

    def stop_server(self):
        for client in self.clients.values():
            client.close()
        for thread in self.threads.values():
            thread.join()
        self.sock.close()
        self.logger.info("Server stopped")