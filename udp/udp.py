import socket
import math
import cv2

class UDP:
    def __init__(self):
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.lastMessageID: int = 0
        self.nextMessageID: int = 0
        
        self.chunk_size = 1000
        
    def send(self, message, address):
        message = f"{message};;-1;;-1;;{self.nextMessageID}".encode()
        self.socket.sendto(message, address)
        self.nextMessageID += 1
        
    def sendImage(self, image, address):
        encode_param = []
        _, buffer = cv2.imencode('.jpg', image, encode_param)
        img_bytes = buffer.tobytes()
        
        total_chunks = math.ceil(len(img_bytes) / self.chunk_size)

        for i in range(total_chunks):
            start = i * self.chunk_size
            end = start + self.chunk_size
            chunk_data = img_bytes[start:end]
            
            data = f"{chunk_data};;{i};;{total_chunks};;{self.nextMessageID}".encode('utf-8')
            self.socket.sendto(data, address)
            self.nextMessageID += 1
            
    def recv(self, size:int):
        data, address = self.socket.recvfrom(size)
        parts = data.rsplit(b";;", 3)
        
        data = parts[0]
        current_chunk = parts[1]
        total_chunks  = parts[2]
        messageID = int(parts[3])
        
        if messageID < self.lastMessageID:
            return None
        else:
            self.lastMessageID = messageID
            return data, current_chunk, total_chunks, address

    def close(self):
        self.socket.close()