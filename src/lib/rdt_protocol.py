import socket as s
import threading
import errno
from queue import Queue, Empty

READ_MODE = 0
WRITE_MODE = 1
CHUNK_SIZE = 1024
MAX_TIMEOUTS = 5

class GBNPeer:
    def __init__(self, addr, mode, win_size=10, timeout=2.0):
        self.addr = addr
        self.mode = mode
        self.win_size = win_size
        self.timeout = timeout

        self.sock = s.socket(s.AF_INET, s.SOCK_DGRAM)
        if self.mode == READ_MODE:
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

    def send(self, data: str):
        if not self.mode == WRITE_MODE:
            raise Exception("Invalid action. Not in write mode.")
        if not self.running:
            raise Exception("Sender not running.")

        self.queue.put(data)
        with self.cond:
            self.cond.notify()

    def recv(self, block=True, timeout=None):
        return self.queue.get(block=block, timeout=timeout)

    def _send_packet(self, seq, data: str):
        packet = f"{seq}|{data}".encode()
        self.sock.sendto(packet, self.addr)

    def _fill_window(self):
        while self.next_seq < self.base + self.win_size:
            try:
                data = self.queue.get_nowait()
            except Empty:
                break

            self.send_buffer[self.next_seq] = data
            self._send_packet(self.next_seq, data)
            self.next_seq += 1

    def _sender_loop(self):
        while self.running:
            with self.cond:
                self._fill_window()

                # Wait if nothing to do
                if self.queue.empty() and self.base == self.next_seq:
                    self.cond.wait()

            try:
                ack_data, _ = self.sock.recvfrom(CHUNK_SIZE)

                self.timeout_count = 0
                ack = int(ack_data.decode())
                if ack >= self.base and ack < self.next_seq:
                    # If is valid ACK update the send buffer
                    for seq in range(self.base, ack + 1):
                        self.send_buffer.pop(seq)
                    self.base = ack + 1
            except s.timeout:
                self.timeout_count += 1
                if self.timeout_count >= MAX_TIMEOUTS:
                    return

                # Retransmit window
                for seq in range(self.base, self.next_seq):
                    self._send_packet(seq, self.send_buffer[seq])



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
                raw = data.decode()
                seq_str, msg = raw.split("|", 1)
                seq = int(seq_str)
            except:
                continue

            if seq == self.next_seq:
                self.next_seq += 1
                self.queue.put(msg)

                ack_packet = str(self.next_seq - 1).encode()
                self.sock.sendto(ack_packet, addr)

            else:
                expected_seq = (self.next_seq - 1) if self.next_seq > 0 else 0
                ack_packet = str(expected_seq).encode()
                self.sock.sendto(ack_packet, addr)

    def all_sent(self):
        return self.queue.empty() and not self.send_buffer

    def stop(self):
        self.running = False
        self.sock.close()
        with self.cond:
            self.cond.notify_all()

