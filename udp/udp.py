import socket
import math
import cv2

"""
Class used for UDP communication
Message structure:  message;;ID

Where message is what user wants to send and ID is library internal counter
"""

class UDP:
    def __init__(self):
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.lastMessageID: int = 0
        self.nextMessageID: int = 0
        
        self.chunk_size = 1000
        
    def send(self, message, address, incrementID: bool = False):
        message += b";;" + self.nextMessageID.to_bytes(length=4)
        self.socket.sendto(message, address)
        if incrementID:
            self.nextMessageID += 1
    
    def recv(self, size: int):
        
        data, address = self.socket.recvfrom(size)
        parts = data.rsplit(b";;", 1)
        
        data = parts[0]
        # lastMessageID = int(parts[1])
        lastMessageID = int.from_bytes(parts[1], byteorder='big')
        
        if lastMessageID < self.lastMessageID:
            return None
        
        return data, address, lastMessageID
        
    def close(self):
        self.socket.close()
        
    def incrementID(self):
        self.nextMessageID += 1