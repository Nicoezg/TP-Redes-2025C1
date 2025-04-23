import socket as s
import threading
from queue import Queue

READ_MODE = 0
WRITE_MODE = 1
CHUNK_SIZE = 1024
MAX_TIMEOUTS = 5

class GBNPeer:
    def __init__(self, addr, mode, win_size=10, timeout=2.0):
        self.addr = addr
        self.win_size = win_size
        self.timeout = timeout

        self.sock = s.socket(s.AF_INET, s.SOCK_DGRAM)
        self.sock.settimeout(timeout)

        self.queue = Queue()
        self.send_buffer = {}

        self.base = 0
        self.next_seq = 0
        self.timeout_count = 0

        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)

        self.mode = mode
        self.running = False

    def send(self, data: str):
        if not self.mode == WRITE_MODE:
            raise Exception("Invalid action. Not in write mode.")
        if not self.running:
            raise Exception("Sender not running.")

        self.queue.put(data)
        with self.cond:
            self.cond.notify()

    def _send_packet(self, seq, data: str):
        packet = f"{seq}|{data}".encode()
        self.sock.sendto(packet, addr)

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

                try:
                    self.cond.release()
                    ack_data, _ = self.sock.recvfrom(CHUNK_SIZE)
                    self.cond.acquire()

                    ack = int(ack_data.decode())
                    if ack >= self.base and ack < self.next_seq:
                        for seq in range(self.base, ack + 1):
                            self.send_buffer.pop(seq)
                        self.base = ack + 1
                except s.timeout:
                    self.timeout_count += 1
                    if self.timeout >= MAX_TIMEOUTS:
                        return

                    # Retransmit window
                    for seq in range(self.base, self.next_seq):
                        self._send_packet(seq, self.send_buffer[seq])

                # Wait if nothing to do
                if self.queue.empty() and self.base == self.next_seq:
                    self.cond.wait()

   def stop(self):
       self.running = False
       self.sock.close()
       with self.cond:
           self.cond.notify_all()

