import time
import sys
sys.path.insert(0, r'C:\Users\User\Desktop\bfmc\frontendUDP')
from udp.udp_sender import UDP_Sender
from udp.types import DATA_TYPES, BROADCAST_MODE
from udp.fps_clock import FPSClock

# Konfiguracija
sender = UDP_Sender(mode=BROADCAST_MODE.UNICAST, addresses=["127.0.0.1"], port=8000)
TARGET_FPS = 30
clock = FPSClock(TARGET_FPS)

states = [
    "IDLE - Waiting for start",
    "FOLLOW LINE - Active",
    "STOP SIGN DETECTED",
    "CROSSWALK - Slowing down",
    "PARKING MODE - Searching spot",
    "EMERGENCY BRAKE!"
]

state_index = 0
last_change_time = time.time()

print(f"Test slanje započeto na portu {sender.port}...")


while True:
    # Proveri da li je prošlo 3 sekunde od poslednje promene
    current_time = time.time()
    if current_time - last_change_time >= 3.0:
        state_index = (state_index + 1) % len(states)
        last_change_time = current_time
        print(f"[SENDING] Current State: {states[state_index]}")

    sender.send(states[state_index], DATA_TYPES.STRING)
        
    # Održavanje FPS-a (iako za stringove nije kritično kao za video)
    clock.tick()