import os

class ValidationError(Exception):
    pass

def validate_storage(path):
    if not os.path.exists(path):
        raise Exception("Directory not found.")
    if not os.path.isdir(path):
        raise Exception(f"{path} is not a valid directory.")

def run_server(args):
    try:
        srv_name, srv_port = args.host, args.port
        validate_storage(args.storage)

        print("Server run successful!")
    except Exception as e:
        print(f"Server error: {e}")

