import os
import logging

def calc_log_level(v=False, q=False):
    if v:
        return logging.INFO
    if q:
        return logging.CRITICAL
    return logging.ERROR

def configure_log_level(args):
    if args.verbose:
        level = logging.DEBUG
    elif args.quiet:
        level = logging.ERROR
    else:
        level = logging.INFO

    logging.basicConfig(format='[%(levelname)s] %(message)s', level=level)


def validate_addr(host, port):
    if int(port) > 65535 or int(port) <= 0:
        raise Exception(f"{port} is not a valid port.")

def validate_storage(path):
    if not os.path.exists(path):
        raise Exception("Directory not found.")
    if not os.path.isdir(path):
        raise Exception(f"{path} is not a valid directory.")

def validate_file(path):
    if not os.path.exists(path):
        raise Exception("File not found.")
    if not os.path.isfile(path):
        raise Exception(f"{path} is not a valid file.")

