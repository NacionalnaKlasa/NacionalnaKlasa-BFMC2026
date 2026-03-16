from src.udp import UDP
from .config import UDP_PORT, UDP_BROADCAST_ADDRESS

import socket

class UDP_Sender(UDP):
    
    def __init__(self, address:str = UDP_BROADCAST_ADDRESS, port:int = UDP_PORT):
        super().__init__()
        
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server_address = (address, port)
        
    def send(self, message):
        super().send(message, self.server_address)