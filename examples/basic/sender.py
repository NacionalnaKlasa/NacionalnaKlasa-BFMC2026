"""
Osnovni primjer slanja podataka preko UDP-a.

Primjer korišćenja:
    sender = UDP_Sender()
    sender.send("Hello World!", DATA_TYPES.STRING)
    sender.send(42, DATA_TYPES.INTEGER)
    sender.send(3.14, DATA_TYPES.FLOAT)
    sender.send(True, DATA_TYPES.BOOLEAN)
"""

import sys
sys.path.insert(0, '/home/filip/projects/udp_broadcast')

from udp.udp_sender import UDP_Sender
from udp.types import DATA_TYPES, BROADCAST_MODE

def main():
    sender = UDP_Sender(mode=BROADCAST_MODE.BROADCAST)
    
    # Primjeri slanja različitih tipova podataka
    sender.send("Hello World!", DATA_TYPES.STRING)
    print("Poslana string poruka")
    
    sender.send(42, DATA_TYPES.INTEGER)
    print("Poslan integer")
    
    sender.send(3.14, DATA_TYPES.FLOAT)
    print("Poslan float")
    
    sender.send(True, DATA_TYPES.BOOLEAN)
    print("Poslana boolean vrijednost")

if __name__ == "__main__":
    main()