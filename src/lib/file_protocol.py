FILE_NAME_START = 2
UPLOAD = 0
DOWNLOAD = 1

"""
The request format is as follows:
    - 1 byte for operation (0 for upload, 1 for download)
    - 1 byte for file name size
    - n bytes for file name (UTF-8 encoded)
    - 1 byte for error-recovery protocol (0 for Stop-and-Wait, 1 for Go-Back-N)

The first message format is as follows:
    - 3 bytes for file size (big-endian) (more than enough for 5MB)
    - n bytes for data

Upload and download examples:
+-------------------------------+-------------------------------+
| Client                        | Server                        |
+-------------------------------+-------------------------------+
| ----> Upload, example.txt, 0  |                               |
|                               | <---- ACK                     |
| ----> File size, data         |                               |
|                               | <---- ACK                     |
| ----> data                    |                               |
|                               | <---- ACK                     |
| ----> data, etc               |                               |
+-------------------------------+-------------------------------+
| ----> Download, example.txt, 1|                               |
|                               | <---- ACK                     |
|                               | <---- File size, data         |
| ----> ACK                     |                               |
|                               | <---- data                    |
| ----> ACK                     |                               |
|                               | <---- data, etc               |
+-------------------------------+-------------------------------+
"""


def decode_request(data):
    """
    Decodes a request and returns the operation, file name
    and error-recovery protocol.
    """

    op = data[0]
    file_name_size = data[1]

    file_name_end = FILE_NAME_START + file_name_size
    file_name = data[FILE_NAME_START:file_name_end].decode('utf-8')

    protocol = data[file_name_end]

    return op, file_name, protocol


def encode_request(op, file_name, protocol):
    """
    Encodes a request into bytes with the operation, file name
    and error-recovery protocol.
    """
    file_name = file_name.encode('utf-8')
    file_name_size = len(file_name)

    data = bytes([op, file_name_size]) + file_name + bytes([protocol])
    return data


def encode_first_msg(file_size, data):
    """
    Encodes the file size into 3 bytes and appends the data.
    """
    return file_size.to_bytes(3, byteorder='big') + data


def decode_file_size(data):
    """
    Decodes the file size from the first 3 bytes and returns both
    the file size and the remaining data.
    """
    return int.from_bytes(data[:3], byteorder='big'), data[3:]
