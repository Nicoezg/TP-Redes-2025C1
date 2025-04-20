import os
import logging

logger = logging.getLogger(__name__)

def calc_log_level(v=False, q=False):
    if v:
        return logging.INFO
    if q:
        return logging.CRITICAL
    return logging.ERROR

def validate_addr(host, port):
    if int(port) > 65535 or int(port) <= 0:
        raise Exception(f"{port} is not a valid port.")

def validate_file(path):
    if not os.path.exists(path):
        raise Exception("File not found.")
    if not os.path.isfile(path):
        raise Exception(f"{path} is not a valid file.")

def client_upload(args):
    try:
        logger.setLevel(calc_log_level(args.verbose, args.quiet))
        srv_name, srv_port = args.host, args.port
        validate_addr(srv_name, srv_port)
        validate_file(args.src)

        logger.info("Upload client run successful!")
    except Exception as e:
        logger.error(f"Client error: {e}")
