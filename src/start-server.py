import argparse
import logging
from lib.server import run_server

def main():
    logging.basicConfig(format='[%(levelname)s] %(message)s')

    parser = argparse.ArgumentParser(
            prog='TPServer',
            description='Server for the file transfer app')
    verbosity_args = parser.add_mutually_exclusive_group()
    verbosity_args.add_argument('-v', '--verbose', help="increase output verbosity", action="store_true")
    verbosity_args.add_argument('-q', '--quiet', help="decrease output verbosity", action="store_true")
    parser.add_argument('-H', '--host', help="service IP address", required=True)
    parser.add_argument('-p', '--port', help="service port", required=True)
    parser.add_argument('-s', '--storage', help="storage dir path", required=True)
    parser.add_argument('-r', '--protocol', help="error recovery protocol")

    args = parser.parse_args()

    try:
        run_server(args)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == '__main__':
    main()
