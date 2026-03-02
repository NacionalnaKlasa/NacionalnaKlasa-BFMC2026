import socket
import time

CAR_IP = "192.168.50.1"   # <-- set to your RPI's IP
CAR_PORT = 5005
PC_PORT = 5006

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PC_PORT)) 

#data,_ = sock.recvfrom(4096)
i = 0   
while i < 50:
    msg = f"Hello RPI! Count: {i}"
    sock.sendto(msg.encode(), (CAR_IP, CAR_PORT))
    
    print(f"Sent: {msg}")
   
    data, addr = sock.recvfrom(4096)
    print("-------------------------")
    print(f"Recieved:{data.decode()}")
    i+=1
    time.sleep(1)


sock.close()