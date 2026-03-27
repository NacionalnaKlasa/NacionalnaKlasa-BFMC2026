import cv2
import sys
sys.path.insert(0, '/home/filip/projects/udp_broadcast')

from udp.udp_receiver import UDP_Receiver
from udp.types import DATA_TYPES

def run_receiver():
    receiver = UDP_Receiver()
    print("Slušam na portu... Pritisni 'q' za izlaz.")
    
    try:
        while True:
            data, data_type = receiver.recv()
            
            if data is not None and data_type == DATA_TYPES.IMAGE:
                cv2.imshow("Video Stream", data)
                
                # Čekaj 1ms na 'q' tipku
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
    except KeyboardInterrupt:
        print("\nZavršavam rad.")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_receiver()