FILE_NAME_START = 2
UPLOAD = 0
DOWNLOAD = 1

"""
The request format is as follows:
    - 1 byte for operation (0 for upload, 1 for download)
    - 1 byte for file name size
    - n bytes for file name (UTF-8 encoded)
    - 1 byte for error-recovery protocol (0 for Stop-and-Wait, 1 for Go-Back-N)
    - 3 bytes for file size (big-endian) (only for upload)


The response message format is as follows:
    - 1 byte for error code (0 for OK, != 0 for ERROR)
    - 2 bytes for port number (big-endian) (only for upload)
    - 3 bytes for file size (big-endian) (only for download)

Upload and download examples:
+-----------------------------------+-----------------------------------+
| Client                            | Server                            |
+-----------------------------------+-----------------------------------+
| ----> Upload, example.txt, 0, 1024|                                   |
|                                   | <---- Response                    |
| ----> data                        |                                   |
|                                   | <---- ACK                         |
| ----> data                        |                                   |
|                                   | <---- ACK                         |
| ----> data, etc                   |                                   |
+-----------------------------------+-----------------------------------+
| ----> Download, example.txt, 1    |                                   |
|                                   | <---- Response                    |
|                                   | <---- data                        |
| ----> ACK                         |                                   |
|                                   | <---- data                        |
| ----> ACK                         |                                   |
|                                   | <---- data, etc                   |
+-----------------------------------+-----------------------------------+
"""


def decode_request(data):
    """
    Decodes a request and returns file name,
    error-recovery protocol and file size.
    """
    op = data[0]

    file_name_size = data[1]

    file_name_end = FILE_NAME_START + file_name_size
    file_name = data[FILE_NAME_START:file_name_end].decode('utf-8')

    protocol = data[file_name_end]
    file_size = _decode_file_size(data[file_name_end + 1:])

    return op, file_name, protocol, file_size


def encode_request(op, file_name, protocol, file_size=0):
    """
    Encodes a request into bytes with the operation, file name,
    error-recovery protocol and file size (0 if download).
    """
    file_name = file_name.encode('utf-8')
    file_name_size = len(file_name)

    data = (
        bytes([op, file_name_size]) +
        bytes(file_name) +
        bytes([protocol]) +
        _encode_file_size(file_size)
    )
    return data


def encode_response(error_code, port=0, file_size=0):
    """
    Encodes a response into bytes with the error code, port number (if upload)
    and file size (if download).
    """
    return (
        bytes([error_code]) +
        _encode_port(port) +
        _encode_file_size(file_size)
    )


def decode_response(data):
    """
    Decodes a response and returns the error code, port and file size.
    """
    error_code = data[0]
    port = _decode_port(data[1:3])
    file_size = _decode_file_size(data[3:6])

    return error_code, port, file_size


def _encode_file_size(file_size):
    """
    Encodes the file size into 3 bytes.
    """
    return file_size.to_bytes(3, byteorder='big')


def _decode_file_size(data):
    """
    Decodes the file size from 3 bytes.
    """
    return int.from_bytes(data, byteorder='big')


def _encode_port(port):
    """
    Encodes the port number into 2 bytes.
    """
    return port.to_bytes(2, byteorder='big')


def _decode_port(data):
    """
    Decodes the port number from 2 bytes.
    """
    return int.from_bytes(data, byteorder='big')
