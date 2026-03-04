import socket
import json
import time

class PCServer:
    def __init__(self, port=65432):
        self.host = "0.0.0.0"
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn = None
        self.buffer = ""
        self.is_running = False

    def start(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        self.is_running = True
        print(f"PC Server ready on port {self.port}...")
        
        # GLAVNA IZMENA: Petlja koja stalno čeka nove klijente
        while self.is_running:
            try:
                # Timeout od 1 sekunde omogućava petlji da povremeno proveri self.is_running
                self.sock.settimeout(1.0) 
                conn, addr = self.sock.accept()
                print(f"Client connected: {addr}")
                
                self.conn = conn
                self.conn.setblocking(False)
                self.buffer = ""
                
                # Zadrži se ovde sve dok je klijent konektovan
                while self.conn is not None and self.is_running:
                    time.sleep(0.1)
                    
            except socket.timeout:
                continue # Nema novih klijenata u ovoj sekundi, vrti petlju ponovo
            except Exception as e:
                pass

    def get_data(self):
        try:
            if not self.conn:
                return []
            data = self.conn.recv(1024).decode('utf-8')
            if not data: 
                # DETEKCIJA PREKIDA: Ako RPi pošalje prazan string, ugasio se
                self.conn.close()
                self.conn = None
                return []
            self.buffer += data
            messages = []
            while "\n" in self.buffer:
                line, self.buffer = self.buffer.split("\n", 1)
                if line.strip():
                    messages.append(json.loads(line))
            return messages
        except (BlockingIOError, json.JSONDecodeError):
            return []
        except Exception:
            # Gubitak signala / nasilno gašenje skripte na RPi
            if self.conn:
                self.conn.close()
            self.conn = None
            return []

    def send_data(self, data_dict):
        if self.conn:
            try:
                msg = json.dumps(data_dict) + "\n"
                self.conn.sendall(msg.encode('utf-8'))
            except Exception:
                self.conn.close()
                self.conn = None

    def closing(self):
        self.is_running = False
        if self.conn: self.conn.close()
        self.sock.close()

class FloydClient:
    def __init__(self, ip_pc, port=65432):
        self.ip = ip_pc
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer = ""

    def connecting(self):
        try:
            self.sock.connect((self.ip, self.port))
            self.sock.setblocking(False)
            print(f"Connected on PC: {self.ip}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def get_data(self):
        try:
            data = self.sock.recv(1024).decode('utf-8')
            if not data: return []
            self.buffer += data
            messages = []
            while "\n" in self.buffer:
                line, self.buffer = self.buffer.split("\n", 1)
                if line.strip():
                    messages.append(json.loads(line))
            return messages
        except (BlockingIOError, json.JSONDecodeError, Exception):
            return []

    def send_data(self, data_dict):
        try:
            msg = json.dumps(data_dict) + "\n"
            self.sock.sendall(msg.encode('utf-8'))
        except: pass

    def closing(self):
        self.sock.close()