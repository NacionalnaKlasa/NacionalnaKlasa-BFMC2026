from udp.udp import UDP

from .config import UDP_PORT, UDP_BROADCAST_ADDRESS, MAX_CHUNK_SIZE
from .types  import DATA_TYPES, BROADCAST_MODE

import socket
import struct
import math
import cv2

"""
Higher level API library used to send messages
Structure of message: data;;dataType;;chunk;;totalChunks

Where data is actual data that should be sent, chunk is current chunk that is being sent 
and totalChunks is number of chunks that receiver should expect for current message.

totalChunks should be always 1 for short strings and int, float, boolean
totalChunks will be > 1 for images and long strings 
"""

class UDP_Sender(UDP):
    
    def __init__(self, mode: BROADCAST_MODE = BROADCAST_MODE.BROADCAST, 
                 addresses: list = None, port: int = UDP_PORT):
        """
        Inicijalizuj UDP sender
        
        Args:
            mode: BROADCAST_MODE.BROADCAST ili BROADCAST_MODE.UNICAST
            addresses: Lista IP adresa za unicast (npr. ["192.168.1.100", "192.168.1.101"])
            port: UDP port
        """
        super().__init__()
        
        self.mode = mode
        self.port = port
        
        if mode == BROADCAST_MODE.BROADCAST:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.server_addresses = [(UDP_BROADCAST_ADDRESS, port)]
            print(f"[SENDER] Mode: BROADCAST na {UDP_BROADCAST_ADDRESS}:{port}")
        else:
            # UNICAST
            if not addresses:
                raise ValueError("UNICAST mode zahteva listu IP adresa!")
            if isinstance(addresses, str):
                addresses = [addresses]
            
            self.server_addresses = [(addr, port) for addr in addresses]
            print(f"[SENDER] Mode: UNICAST na {len(addresses)} adresa:")
            for addr in addresses:
                print(f"         → {addr}:{port}")
        
        self.maxChunkSize = MAX_CHUNK_SIZE
        self._dispatch_table = {
            DATA_TYPES.IMAGE:   self.sendImage,
            DATA_TYPES.BOOLEAN: self.sendBoolean,
            DATA_TYPES.INTEGER: self.sendInteger,
            DATA_TYPES.FLOAT:   self.sendFloat,
            DATA_TYPES.STRING:  self.sendString,
        }
        
        self.dataCounter = 0
        
    def send(self, message, dataType: DATA_TYPES):
        dataChunks: list = []
        handler = self._dispatch_table.get(dataType)
        dataChunks = handler(message)
        total_chunks:int = len(dataChunks)
        
        for i, chunk in enumerate(dataChunks):
            message_bytes = chunk + b";;" + dataType.value.to_bytes(length=1, byteorder='big', signed=True) + b";;" + i.to_bytes(length=4, byteorder='big') + b";;" + (total_chunks - 1).to_bytes(length=4, byteorder='big')
            
            # Pošalji na sve adrese
            for addr in self.server_addresses:
                super().send(message_bytes, addr)
    
        super().incrementID()
        dataChunks.clear()
        
    """
    Methods bellow should split data in chunk for sending
    """
    
    def sendImage(self, image) -> list:
        encode_param = []
        _, buffer = cv2.imencode('.jpg', image, encode_param)
        img_bytes = buffer.tobytes()
        
        total_chunks = math.ceil(len(img_bytes) / self.maxChunkSize)
        data = []
        for i in range(total_chunks):
            start = i * self.maxChunkSize
            end = start + self.maxChunkSize
            data.append(img_bytes[start:end])
            
        return data
    
    def sendString(self, string:str) -> list:
        string_bytes = string.encode()
        data = [string_bytes[i : i + self.maxChunkSize] for i in range(0, len(string_bytes), self.maxChunkSize)]
        
        return data        
    
    def sendInteger(self, number: int) -> list:
        data = []
        int_bytes = struct.pack('>i', number)
        data.append(int_bytes)
                
        return data
    
    def sendFloat(self, number: float) -> list:
        data = []
        float_bytes = struct.pack('>d', number)
        data.append(float_bytes)
        
        return data
    
    def sendBoolean(self, value: bool) -> list:
        data = []
        bool_bytes = struct.pack('?', value)
        data.append(bool_bytes)
        
        return data