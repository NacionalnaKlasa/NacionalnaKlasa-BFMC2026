"""
Osnovni primjer prijemanja podataka preko UDP-a.

Primjer korišćenja:
    receiver = UDP_Receiver()
    while True:
        data, data_type = receiver.recv()
        if data is not None:
            print(f"Primljena poruka: {data} (tip: {data_type})")
"""

import sys
sys.path.insert(0, '/home/filip/projects/udp_broadcast')

from udp.udp_receiver import UDP_Receiver
from udp.types import DATA_TYPES

def main():
    receiver = UDP_Receiver()
    print("Čekam poruke... (Ctrl+C za izlaz)")
    
    try:
        while True:
            data, data_type = receiver.recv()
            if data is not None:
                print(f"Primljena poruka ({data_type}): {data}")
    except KeyboardInterrupt:
        print("\nZavršavam rad.")

if __name__ == "__main__":
    main()