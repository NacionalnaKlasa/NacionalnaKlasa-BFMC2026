from .. tcp_client import TCP_CLIENT

def main():
    client = TCP_CLIENT()
    client.send("Hej Serveru!")
    client.disconnect()
    

if __name__ == '__main__':
    main()