import logging as logger
import os
import socket
import threading
from lib import common as c
from lib import file_protocol
from lib import rdt_protocol

BUFFER_SIZE = 1400
DATA_SIZE = 1396
SIX_MB = 6291456


class Server:
    def __init__(self, ip, port, storage, protocol):
        self.ip = ip
        self.port = int(port)
        self.storage = storage
        self.protocol = protocol

        self.clients = {}
        self.threads = {}

    def run_server(self):
        try:
            c.validate_addr(self.port)
            c.validate_storage(self.storage)

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.ip, self.port))

            logger.info(f"Server listening on {self.ip} : {self.port}")
            logger.info("Server run successful!")

            self.listen_client()

        except Exception as e:
            logger.error(f"Server error: {e}")

    def listen_client(self):
        while True:
            try:
                data, client_addr = self.sock.recvfrom(BUFFER_SIZE)
                if not data:
                    break
                logger.info(f"Received data from {client_addr}: {data}")

                if client_addr not in self.clients:
                    logger.info(f"New client connected: {client_addr}")
                    self.new_client(data, client_addr)
                    if client_addr in self.threads:
                        self.threads[client_addr].start()

            except Exception as e:
                logger.error(f"Error receiving data: {e}")
                break

    def new_client(self, data, addr):
        op, file_name, proto, file_size = file_protocol.decode_request(data)
        error_code = 0

        if op == file_protocol.UPLOAD:
            logger.info(f"Client {addr} requested upload of {file_name}")

            if proto == 0:
                peer = rdt_protocol.GBNPeer(
                    (self.ip, 0), rdt_protocol.READ_MODE, win_size=1
                )
            else:
                peer = rdt_protocol.GBNPeer(
                    (self.ip, 0), rdt_protocol.READ_MODE
                )

            _, upload_port = peer.sock.getsockname()

            logger.info(f"Assigned port {upload_port} for upload from {addr}")

            if file_size > SIX_MB:
                logger.error(f"File size exceeds limit: {file_size} bytes")
                error_code = 2

            response = file_protocol.encode_response(error_code, upload_port)
            self.sock.sendto(response, addr)

            if error_code != 0:
                peer.stop()
                return

            thread = threading.Thread(
                target=self.handle_upload,
                args=(peer, file_name, addr, file_size)
            )
            self.threads[addr] = thread
            self.clients[addr] = peer

        elif op == file_protocol.DOWNLOAD:
            try:
                file_size = os.path.getsize(self.storage+"/"+file_name)
                response = file_protocol.encode_response(
                    error_code, 0, file_size
                )
                self.sock.sendto(response, addr)
                logger.info(f"Client {addr} requested download of {file_name}")

                if proto == 0:
                    peer = rdt_protocol.GBNPeer(
                        addr, rdt_protocol.WRITE_MODE, win_size=1
                    )
                else:
                    peer = rdt_protocol.GBNPeer(addr, rdt_protocol.WRITE_MODE)
                _, download_port = peer.sock.getsockname()

                logger.info(
                    f"Assigned port {download_port} for download to {addr}"
                )
                self.threads[addr] = threading.Thread(
                    target=self.handle_download, args=(peer, file_name)
                )
                self.clients[addr] = peer

            except FileNotFoundError:
                logger.error(f"File {file_name} not found")
                error_code = 1
                response = file_protocol.encode_response(error_code, 0, 0)
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
                    logger.warning(f"Error receiving file: {e}")
                    break

            if received_size >= file_size:
                logger.info(
                    f"New file uploaded: {file_name} from {client_addr}"
                )

    def handle_download(self, peer, file_name):
        try:
            with open(f"{self.storage}/{file_name}", "rb") as f:
                while True:
                    data = f.read(DATA_SIZE)
                    if not data:
                        break
                    peer.send(data)
        except Exception as e:
            logger.error(f"Error sending file: {e}")

    def stop_server(self):
        for client in self.clients.values():
            client.stop()
        for thread in self.threads.values():
            thread.join()
        self.sock.close()
        logger.info("Server stopped")
