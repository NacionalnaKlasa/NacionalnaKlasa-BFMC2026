from .tcp import TCP
from .config import SERVER_PORT, BACKLOG, SERVER_IP_ADDRESS

class TCP_SERVER(TCP):
    def __init__(self):
        super().__init__()
        self.bind('0.0.0.0', SERVER_PORT)
        self.listen(BACKLOG)
        print("Server listening...")

    def bind(self, ip, port):
       try:
           self.socket.bind((ip, port))
       except Exception as e:
           print(f"Error occurred while binding: {e}")
           exit(1)

    def listen(self, backlog=1):
        try:
            self.socket.listen(backlog)
        except Exception as e:
            print(f"Error occurred while listening: {e}")
            exit(1)

    def accept(self):
        return self.socket.accept()


    def disconnect_client(self, client_socket):
        try:
            self.socket.close(client_socket)
        except Exception as e:
            print(f"Error occurred while disconnecting client: {e}")
            exit(1)