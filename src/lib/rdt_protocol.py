import socket as s
import threading
import errno
import logging as logger
from queue import Queue, Empty

from lib.packet import Packet

READ_MODE = 0
WRITE_MODE = 1
CHUNK_SIZE = 1400
MAX_TIMEOUTS = 5
BASE_WIN_SIZE = 10
BASE_TIMEOUT = 0.1


class GBNPeer:
    def __init__(self, addr, mode, win_size=BASE_WIN_SIZE,
                 timeout=BASE_TIMEOUT, sock=None):
        self.addr = addr
        self.mode = mode
        if win_size <= 0:
            raise ValueError("Invalid window size. Must be higher than 0.")
        self.win_size = win_size
        self.timeout = timeout

        # Use the provided socket or create a new one
        self.sock = sock if sock else s.socket(s.AF_INET, s.SOCK_DGRAM)
        if self.mode == READ_MODE and not sock:
            self.sock.bind(self.addr)

        # Set timeout for ACKs
        if self.mode == WRITE_MODE:
            self.sock.settimeout(timeout)

        self.queue = Queue()
        self.send_buffer = {}

        self.base = 0
        self.next_seq = 0
        self.timeout_count = 0

        self.lock = threading.RLock()
        self.cond = threading.Condition(self.lock)

        self.running = True
        if self.mode == READ_MODE:
            threading.Thread(target=self._recv_loop, daemon=True).start()
        elif self.mode == WRITE_MODE:
            threading.Thread(target=self._sender_loop, daemon=True).start()

    def send(self, data):
        if not self.mode == WRITE_MODE:
            raise Exception("Invalid action. Not in write mode.")
        if not self.running:
            raise Exception("Sender not running.")

        self.queue.put(data)
        with self.cond:
            self.cond.notify()

    def recv(self, block=True, timeout=None):
        if not self.mode == READ_MODE:
            raise Exception("Invalid action. Not in read mode.")
        if not self.running:
            raise Exception("Receiver not running.")
        return self.queue.get(block=block, timeout=timeout)

    def _send_packet(self, packet: Packet):
        logger.debug(
            f"sending packet (seq:{packet.seq}, ack:{packet.ack}) "
            f"to {self.addr}"
        )
        self.sock.sendto(packet.to_bytes(), self.addr)

    def _fill_window(self):
        while self.next_seq < self.base + self.win_size:
            try:
                data = self.queue.get_nowait()
            except Empty:
                break

            self.send_buffer[self.next_seq] = data
            packet = Packet(self.next_seq, 0, data)
            self._send_packet(packet)
            self.next_seq += 1

    def _sender_loop(self):
        while self.running:
            with self.cond:
                self._fill_window()

                # Wait if nothing to do
                while self.queue.empty() and self.base == self.next_seq:
                    self.cond.wait()

                    # Check if woken by a call to self.stop
                    if not self.running:
                        return

            try:
                ack_data, addr = self.sock.recvfrom(CHUNK_SIZE)
                ack_packet = Packet.from_bytes(ack_data)
                logger.debug(
                    f"[sender-loop] received packet (seq:{ack_packet.seq}, "
                    f"ack:{ack_packet.ack}) from {addr}"
                )

                self.timeout_count = 0
                ack = ack_packet.ack
                if ack >= self.base and ack < self.next_seq:
                    # If is valid ACK update the send buffer
                    for seq in range(self.base, ack + 1):
                        self.send_buffer.pop(seq)
                    self.base = ack + 1
            except s.timeout:
                self.timeout_count += 1
                if self.timeout_count >= MAX_TIMEOUTS:
                    logger.info(
                        f"[sender-loop] number of timeouts exceeded: "
                        f"{self.timeout_count}. Closing connection..."
                    )
                    self.running = False
                    self.sock.close()
                    return

                # Retransmit window
                logger.info(
                    f"[sender-loop] retransmitting packets from seq: "
                    f"{self.base} to seq: {self.next_seq} {self.addr}"
                )
                for seq in range(self.base, self.next_seq):
                    packet = Packet(seq, 0, self.send_buffer[seq])
                    self._send_packet(packet)

    def _recv_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(CHUNK_SIZE)
            except OSError as e:
                # errno 9: Bad file descriptor (socket closed)
                if e.errno == errno.EBADF and not self.running:
                    return
                else:
                    raise

            try:
                packet = Packet.from_bytes(data)
                logger.debug(
                    f"[recv-loop] received packet (seq:{packet.seq}, "
                    f"ack:{packet.ack}) from {addr}"
                )
                seq = packet.seq
                msg = packet.data
            except Exception:
                continue

            if seq == self.next_seq:
                self.next_seq += 1
                self.queue.put(msg)

                ack = self.next_seq - 1
                ack_packet = Packet(0, ack)  # "empty" packet (ack)
                logger.debug(
                    f"[recv-loop] sending packet (seq:{ack_packet.seq}, "
                    f"ack:{ack_packet.ack}) to {addr}"
                )
                self.sock.sendto(ack_packet.to_bytes(), addr)
            else:
                expected_seq = (self.next_seq - 1) if self.next_seq > 0 else 0
                ack = expected_seq
                ack_packet = Packet(0, ack)  # "empty" packet (ack)
                logger.debug(
                    f"[recv-loop] sending packet (seq:{ack_packet.seq}, "
                    f"ack:{ack_packet.ack}) to {addr}"
                )
                self.sock.sendto(ack_packet.to_bytes(), addr)

    def all_sent(self):
        return self.queue.empty() and not self.send_buffer

    def stop(self):
        if self.running:
            self.running = False
            self.sock.close()
            with self.cond:
                self.cond.notify_all()

    def is_write_mode(self):
        return self.mode == WRITE_MODE
