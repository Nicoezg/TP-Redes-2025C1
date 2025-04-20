import logging
from lib import common as c

logger = logging.getLogger(__name__)

def run_server(args):
    try:
        logger.setLevel(c.calc_log_level(args.verbose, args.quiet))

        srv_name, srv_port = args.host, args.port
        c.validate_addr(srv_name, srv_port)
        c.validate_storage(args.storage)

        logger.info("Server run successful!")
    except Exception as e:
        logger.error(f"Server error: {e}")

