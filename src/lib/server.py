from logging import Logger
import socket
import threading
from lib import common as c
from lib import file_protocol
from lib import rdt_protocol

UPLOAD = 0
DOWNLOAD = 1
BUFFER_SIZE = 1024

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
        op, file_name, proto = file_protocol.decode_request(data)

        if op == UPLOAD:
            self.logger.info(f"Client {addr} requested upload of {file_name}")

            if proto == 0:
                peer = rdt_protocol.GBNPeer((self.ip, 0), rdt_protocol.READ_MODE, 0)  
            else:
                peer = rdt_protocol.GBNPeer((self.ip, 0), rdt_protocol.READ_MODE)

            _, upload_port = peer.sock.getsockname()

            self.logger.info(f"Assigned port {upload_port} for upload from {addr}")

            response = f"OK|{upload_port}".encode()
            self.sock.sendto(response, addr)

            thread = threading.Thread(target=self.handle_upload, args=(peer, file_name, addr))
            self.threads[addr] = thread
            self.clients[addr] = peer

    def handle_upload(self, peer, file_name, client_addr):
        total_size = None
        received_size = 0

        with open(f"{self.storage}/{file_name}", "wb") as f:
            while True:
                try:
                    data = peer.recv(timeout=5)
                    print(f"Received data: {data} from {client_addr}") 
                    if not data:
                        break
                    if total_size is None:
                        total_size, data = file_protocol.decode_file_size(data)
                    f.write(data)
                    received_size += len(data)
                    if received_size >= total_size:
                        break
            
                except Exception as e:
                    self.logger.warning(f"Error receiving file: {e}")
                    break
        peer.stop()

    def stop_server(self):
        for client in self.clients.values():
            client.close()
        for thread in self.threads.values():
            thread.join()
        self.sock.close()
        self.logger.info("Server stopped")