import cv2
import time
import sys
sys.path.insert(0, r'C:\Users\User\Desktop\bfmc\frontendUDP')
from udp.udp_sender import UDP_Sender
from udp.types import DATA_TYPES, BROADCAST_MODE
from udp.fps_clock import FPSClock

sender = UDP_Sender(mode=BROADCAST_MODE.UNICAST, addresses=["127.0.0.1"], port=9990)
cap = cv2.VideoCapture(r'C:\Users\User\Desktop\bfmc\frontendUDP\videos\54D.mp4') # Putanja do tvog videa
#TARGET_FPS = 30
TARGET_FPS = cap.get(cv2.CAP_PROP_FPS)
clock = FPSClock(TARGET_FPS)

print(f"Slanje započeto na portu {sender.port} sa {TARGET_FPS} FPS...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0) #loop videa kad dodjem na kraj
        continue
    
    # Slanje frejma preko UDP-a
    sender.send(frame, DATA_TYPES.IMAGE)
    sender.send("FOLLOW LINE", DATA_TYPES.STRING)
    #odrzava konstantan ritam
    clock.tick()

cap.release()