import logging
from lib import common as c
import file_protocol
import rdt_protocol

logger = logging.getLogger(__name__)

def client_upload(args):
    try:
        logger.setLevel(c.calc_log_level(args.verbose, args.quiet))

        srv_name, srv_port = args.host, args.port
        c.validate_addr(srv_name, srv_port)
        c.validate_file(args.src)

        logger.info("Upload client run successful!")
        logger.info(f"Uploading {args.src} to {srv_name}:{srv_port} as {args.name}")
        if args.protocol =="saw":#si el cliente elige el protocolo stop and wait
            rdt_protocol = rdt_protocol.GBNPeer((srv_name, srv_port), rdt_protocol.WRITE_MODE,1)
        else:# si el cliente elige el protocolo go back n
            rdt_protocol = rdt_protocol.GBNPeer((srv_name, srv_port), rdt_protocol.WRITE_MODE)
        rdt_protocol.send(file_protocol.encode_request(file_protocol.UPLOAD, args.name, 0 if args.protocol == "saw" else 1))
        with open(args.src, 'rb') as file:
            length = file.len()
            data = file.read(1000)
            rdt_protocol.send(file_protocol.encode_first_msg(length, data))
            while data:
                data = file.read(1000)
                rdt_protocol.send(data)
    except Exception as e:
        logger.error(f"Client error: {e}")

def client_download(args):
    try:
        logger.setLevel(c.calc_log_level(args.verbose, args.quiet))

        srv_name, srv_port = args.host, args.port
        c.validate_addr(srv_name, srv_port)

        logger.info("Starting download client...")
        logger.info(f"Downloading {args.name} from {srv_name}:{srv_port}")

        if args.protocol == "saw":  # si el cliente elige el protocolo stop and wait
            rdt_protocol = rdt_protocol.GBNPeer((srv_name, srv_port), rdt_protocol.READ_MODE, 1)
        else:  # si el cliente elige el protocolo go back n
            rdt_protocol = rdt_protocol.GBNPeer((srv_name, srv_port), rdt_protocol.READ_MODE)
        
        rdt_protocol.send(file_protocol.encode_request(file_protocol.DOWNLOAD, args.name, 0 if args.protocol == "saw" else 1))

        with open(args.name, 'wb') as file:
            while True:
                data = rdt_protocol.recv()
                if not data:
                    break
                file.write(data)                

        logger.info("Download client run successful!")
    except Exception as e:
        logger.error(f"Client error: {e}")
