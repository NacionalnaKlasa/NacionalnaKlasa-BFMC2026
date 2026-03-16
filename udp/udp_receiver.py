from src.udp import UDP
from .config import UDP_PORT

import socket

class UDP_Receiver(UDP):
    def __init__(self, address:str = "", port:int = UDP_PORT):
        super().__init__()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.socket.setblocking(False)
        self.socket.bind((address, port))
        
    def recv(self, size:int = 1024):
        return super().recv(size)