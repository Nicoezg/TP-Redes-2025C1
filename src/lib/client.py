import os
import logging
from lib import common as c

logger = logging.getLogger(__name__)

def client_upload(args):
    try:
        logger.setLevel(c.calc_log_level(args.verbose, args.quiet))

        srv_name, srv_port = args.host, args.port
        c.validate_addr(srv_name, srv_port)
        c.validate_file(args.src)

        logger.info("Upload client run successful!")
    except Exception as e:
        logger.error(f"Client error: {e}")
