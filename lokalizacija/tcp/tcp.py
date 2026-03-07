import socket

class TCP():
    def __init__(self):
        self.socket:socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def recv(self, len):
        return self.socket.recv(len)
    
    def send(self, msg):
        return self.socket.send(msg)
    
    def close(self):
        self.socket.close()