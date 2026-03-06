from .. tcp_server import TCP_SERVER

def main():
    server = TCP_SERVER()
    conn, addr = server.accept()

    msg = conn.recv(1024)
    print(f"Received: {msg}")
    conn.close()

    server.close()
    

if __name__ == '__main__':
    main()