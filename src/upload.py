import argparse
import logging
from lib import client

def main():
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(
            prog='TPClientUp',
            description='Upload client for the file transfer app')
    verbosity_args = parser.add_mutually_exclusive_group()
    verbosity_args.add_argument('-v', '--verbose', help="increase output verbosity", action="store_true")
    verbosity_args.add_argument('-q', '--quiet', help="decrease output verbosity", action="store_true")
    parser.add_argument('-H', '--host', help="server IP address", required=True)
    parser.add_argument('-p', '--port', help="server port", required=True)
    parser.add_argument('-s', '--src', help="source file path", required=True)
    parser.add_argument('-n', '--name', help="file name", required=True)
    parser.add_argument('-r', '--protocol', help="error recovery protocol")

    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.INFO)
    elif args.quiet:
        logger.setLevel(logging.CRITICAL)
    else:
        logger.setLevel(logging.ERROR)


    client.Client(args.host, args.name, args.port, args.protocol,logger).initial_connection(args, 0)

if __name__ == '__main__':
    main()
