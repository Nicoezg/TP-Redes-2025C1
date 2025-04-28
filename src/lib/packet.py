from struct import pack, unpack


class Packet:
    def __init__(self, seq, ack, data=None):
        self.seq = seq
        self.ack = ack
        self.data = data if data is not None else bytes()

    @classmethod
    def from_bytes(cls, bytes):
        """
        Parses bytes to generate a Packet instance
        """

        # 2 bytes for sequence number (unsigned short)
        # 2 bytes for ack (unsigned short)
        # len(bytes) - 4 bytes for data
        # big-endian
        seq, ack, data = unpack("!1H1H{}s".format(len(bytes) - 4), bytes)
        return cls(seq, ack, data)

    def to_bytes(self):
        print(f"[DEBUG] Packet.to_bytes(): data type is {type(self.data)}")
        return pack("!1H1H{}s".format(len(self.data)), self.seq, self.ack, self.data)
