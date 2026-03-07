from .. tcp_server import TCP_SERVER

import struct

def main():
    server = TCP_SERVER()
    conn, addr = server.accept()

    speed, angle, status = struct.unpack('!iii', conn.recv(12))
    
    while not status:
        if not status:
            print(f"Received speed: {speed}, Received angle: {angle}")
        else:
            print("Received unknown message!")
        speed, angle, status = struct.unpack('!iii', conn.recv(12))

    conn.close()
    server.close()
    

if __name__ == '__main__':
    main()