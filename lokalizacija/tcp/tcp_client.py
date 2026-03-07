from .tcp import TCP
from .config import SERVER_PORT, SERVER_IP_ADDRESS

import time
import struct

class TCP_CLIENT(TCP):
    def __init__(self):
        super().__init__()
        self.connected : bool = False
        self.last_connect_time : int = 0
        self.connect(SERVER_IP_ADDRESS, SERVER_PORT)
    
    def connect(self, ip, port):
        if not self.socket.connect_ex((ip, port)):
            self.connected = True
            self.last_connect_time = time.monotonic_ns()
         
    def reconnect(self, ip, port, delay=1):
        if time.monotonic_ns() - self.last_connect_time > delay:
            self.connect(ip, port)

    def disconnect(self):
        if self.connected:
            self.socket.close()
        self.connected = False
    
    def send(self, speed, angle, status):
        if not self.connected:
            self.reconnect(SERVER_IP_ADDRESS, SERVER_PORT)
        else:
            msg = struct.pack("!iii", speed, angle, status)
            return super().send(msg)
    
    def receive(self, msg):
         if not self.connected:
            self.reconnect()
         else:
            return super().recv(msg)
         
    