import os
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    pass

def calc_log_level(v=False, q=False):
    if v:
        return logging.INFO
    if q:
        return logging.CRITICAL
    return logging.ERROR

def validate_storage(path):
    if not os.path.exists(path):
        raise Exception("Directory not found.")
    if not os.path.isdir(path):
        raise Exception(f"{path} is not a valid directory.")

def run_server(args):
    try:
        logger.setLevel(calc_log_level(args.verbose, args.quiet))
        srv_name, srv_port = args.host, args.port
        validate_storage(args.storage)

        logger.info("Server run successful!")
    except Exception as e:
        logger.error(f"Server error: {e}")

