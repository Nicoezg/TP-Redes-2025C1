
import logging as logger
import os
from lib import common as c
from lib import file_protocol
from lib import rdt_protocol
import socket

class Client:
    def __init__(self, ip, name,port, protocol):
        self.ip = ip
        self.name = name
        self.port = int(port)
        self.protocol = protocol

    def initial_connection(self, args, op):
        try:
            if op== 0:
                logger.info(f"Uploading {args.src} to {args.host}:{args.port} as {args.name}")
                c.validate_file(args.src)
                file_size = os.path.getsize(args.src)
                request = file_protocol.encode_request(file_protocol.UPLOAD, self.name, 0 if self.protocol== "saw" else 1, file_size if op == file_protocol.UPLOAD else 0)
            
            elif op == 1:
                logger.info(f"Downloading {args.name} from {args.host}:{args.port}")
                request = file_protocol.encode_request(file_protocol.DOWNLOAD, self.name, 0 if self.protocol== "saw" else 1)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            if op == 1:
                self.sock.bind(('', 0))
            

            self.sock.sendto(request, (self.ip, self.port))

            response, _ = self.sock.recvfrom(1496)
            error_code, upload_port, file_size = file_protocol.decode_response(response)
            if error_code != 0:
                # Bla bla bla
                raise Exception("Server did not accept upload")
            self.upload_port = upload_port
            local_address = self.sock.getsockname()


            logger.info(f"Server responded with OK. Upload port: {self.upload_port}")
            if op == file_protocol.UPLOAD:
                self.client_upload(args, self.upload_port)
            elif op == file_protocol.DOWNLOAD:
                self.client_download(args,local_address,file_size)

        except Exception as e:
            logger.error(f"Connection error: {e}")


    def client_upload(self, args, upload_port):
        try:
            srv_name, srv_port = self.ip, self.port 
            c.validate_addr(srv_name, srv_port) 

            logger.info(f"Uploading {args.src} to {srv_name}:{upload_port} as {args.name}") 

            if args.protocol == "saw":
                rdt = rdt_protocol.GBNPeer((srv_name, upload_port), rdt_protocol.WRITE_MODE, win_size=1)
            else:
                rdt = rdt_protocol.GBNPeer((srv_name, upload_port), rdt_protocol.WRITE_MODE)

            with open(args.src, 'rb') as file:
                file.seek(0, 2)
                file.seek(0)
                while True:
                    data = file.read(1496)
                    if not data:
                        break
                    rdt.send(data)
                
                logger.info("Upload client run successful!")
            while (not rdt.all_sent()):
                pass


        except Exception as e:
            logger.error(f"Client error: {e}")

    def client_download(self,args,local_address,size):
        try:
            srv_name, srv_port = args.host, args.port
            c.validate_addr(srv_name, srv_port)

            logger.info("Starting download client...")
            logger.info(f"Client listening on {local_address[0]}:{local_address[1]}")
            logger.info(f"Downloading {args.name} from {srv_name}:{srv_port}")

            if args.protocol == "saw":  # si el cliente elige el protocolo stop and wait
                rdt = rdt_protocol.GBNPeer(local_address, rdt_protocol.READ_MODE, win_size=1, sock=self.sock)
            else:  # si el cliente elige el protocolo go back n
                rdt = rdt_protocol.GBNPeer(local_address, rdt_protocol.READ_MODE, sock=self.sock)
            

            size_act = 0
            with open(args.dst, 'wb') as file:
                while True:
                    if size<=size_act:
                        break
                    data = rdt.recv()
                    if not data:
                        break
                    file.write(data)             
                    size_act += len(data)

            logger.info("Download client run successful!")
        except Exception as e:
            logger.error(f"Client error: {e}")
