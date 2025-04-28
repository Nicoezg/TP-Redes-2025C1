
from logging import Logger
from lib import common as c
from lib import file_protocol
from lib import rdt_protocol
import socket

class Client:
    def __init__(self, ip, name,port, protocol,logger: Logger):
        self.ip = ip
        self.name = name
        self.port = int(port)
        self.protocol = protocol

        self.logger = logger

    def initial_connection(self,args):
        try:
            self.logger.info(f"Uploading {args.src} to {args.host}:{args.port} as {args.name}")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            request = file_protocol.encode_request(file_protocol.UPLOAD, self.name, 0 if self.protocol== "saw" else 1)
            self.sock.sendto(request, (self.ip, self.port))

            response, _ = self.sock.recvfrom(1024)
            print(response)
            response_str = response.decode()
            if not response_str.startswith("OK|"):
                raise Exception("Server did not accept upload")

            self.upload_port = int(response_str.split("|")[1])

            self.logger.info(f"Server responded with OK. Upload port: {self.upload_port}")
            self.sock.close()
            self.client_upload(args, self.upload_port) 

        except Exception as e:
            self.logger.error(f"Connection error: {e}")


    def client_upload(self, args, upload_port):
        try:

            self.logger.setLevel(c.calc_log_level(args.verbose, args.quiet))

            srv_name, srv_port = self.ip, self.port 
            c.validate_addr(srv_name, srv_port) 
            c.validate_file(args.src)

            self.logger.info(f"Uploading {args.src} to {srv_name}:{upload_port} as {args.name}") 

            if args.protocol == "saw":
                rdt = rdt_protocol.GBNPeer((srv_name, upload_port), rdt_protocol.WRITE_MODE,1) 
            else:
                rdt = rdt_protocol.GBNPeer((srv_name, upload_port), rdt_protocol.WRITE_MODE)

            with open(args.src, 'rb') as file:
                file.seek(0, 2)
                length = file.tell()
                file.seek(0)
                first_data = file.read(1000)
                rdt.send(file_protocol.encode_first_msg(length, first_data))
                while True:
                    data = file.read(1000)
                    if not data:
                        break
                    rdt.send(data)
                
                self.logger.info("Upload client run successful!")
            while (rdt.all_sent):
                pass


        except Exception as e:
            self.logger.error(f"Client error: {e}")

    def client_download(self,args):
        try:
            self.logger.setLevel(c.calc_log_level(args.verbose, args.quiet))

            srv_name, srv_port = args.host, args.port
            c.validate_addr(srv_name, srv_port)

            self.logger.info("Starting download client...")
            self.logger.info(f"Downloading {args.name} from {srv_name}:{srv_port}")

            if args.protocol == "saw":  # si el cliente elige el protocolo stop and wait
                rdt_protocol = rdt_protocol.GBNPeer((srv_name, srv_port), rdt_protocol.READ_MODE, 1)
            else:  # si el cliente elige el protocolo go back n
                rdt_protocol = rdt_protocol.GBNPeer((srv_name, srv_port), rdt_protocol.READ_MODE)
            
            rdt_protocol.send(file_protocol.encode_request(file_protocol.DOWNLOAD, args.name, 0 if args.protocol == "saw" else 1))

            size=rdt_protocol.recv()
            size = file_protocol.decode_first_msg(size)
            size_act = 0
            with open(args.name, 'wb') as file:
                while True:
                    data = rdt_protocol.recv()
                    if not data or size<=size_act:
                        break
                    file.write(data)                
                    size_act += len(data)

            self.logger.info("Download client run successful!")
        except Exception as e:
            self.logger.error(f"Client error: {e}")