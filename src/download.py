import argparse
import logging
from lib.client import client_download

def main():
    logging.basicConfig(format='[%(levelname)s] %(message)s')

    parser = argparse.ArgumentParser(
            prog='TPClientUp',
            description='Upload client for the file transfer app')
    verbosity_args = parser.add_mutually_exclusive_group()
    verbosity_args.add_argument('-v', '--verbose', help="increase output verbosity", action="store_true")
    verbosity_args.add_argument('-q', '--quiet', help="decrease output verbosity", action="store_true")
    parser.add_argument('-H', '--host', help="server IP address", required=True)
    parser.add_argument('-p', '--port', help="server port", required=True)
    parser.add_argument('-d', '--dst', help="destination file path", required=True)
    parser.add_argument('-n', '--name', help="file name", required=True)
    parser.add_argument('-r', '--protocol', help="error recovery protocol")

    args = parser.parse_args()

    client_download(args)

if __name__ == '__main__':
    main()
