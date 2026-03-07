from .. tcp_client import TCP_CLIENT

def main():
    client = TCP_CLIENT()
    
    status = 0
    
    while not status:
        speed = int(input("Type desired speed: "))
        angle = int(input("Type desired angle: "))
        status = int(input("Type desired status: "))
        print("\n")
        client.send(speed, angle, status)

    client.disconnect()
    

if __name__ == '__main__':
    main()