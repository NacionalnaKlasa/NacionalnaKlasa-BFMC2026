import cv2
from udp.udp_sender import UDP_Sender
from udp.types import DATA_TYPES, BROADCAST_MODE
from udp.fps_clock import FPSClock

def run_sender(mode: BROADCAST_MODE = BROADCAST_MODE.BROADCAST, 
               addresses = None, target_fps: int = 30):
    """
    Slanje video stream-a sa konstantnim FPS-om
    
    Args:
        mode: BROADCAST_MODE.BROADCAST ili BROADCAST_MODE.UNICAST
        addresses: Za BROADCAST - None, za UNICAST - IP adresa ili lista IP adresa
        target_fps: Ciljan FPS (default: 30)
    """
    sender = UDP_Sender(mode=mode, addresses=addresses)
    cap = cv2.VideoCapture("/home/filip/projects/udp_broadcast/test/videos/qualification_video.mp4")
    
    # Kreiraj FPS clock koji će održavati konstantan frame rate
    clock = FPSClock(target_fps)

    print(f"Slanje video strima sa {target_fps} FPS...")

    try:
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Pošalji frejm
            sender.send(frame, DATA_TYPES.IMAGE)
            frame_count += 1
            
            # Čekaj da bi se održao target FPS
            clock.tick()

    except KeyboardInterrupt:
        print("Slanje prekinuto.")
    finally:
        cap.release()
        print(f"Ukupno poslato frejm-ova: {frame_count}")

if __name__ == "__main__":
    import sys
    
    # Parsiranje argumentata
    mode = BROADCAST_MODE.BROADCAST
    addresses = None
    target_fps = 30
    
    if len(sys.argv) > 1:
        # Prvi argument: broadcast ili unicast
        mode_str = sys.argv[1].lower()
        if mode_str == "broadcast":
            mode = BROADCAST_MODE.BROADCAST
        elif mode_str == "unicast":
            mode = BROADCAST_MODE.UNICAST
            # Preostali argumenti su IP adrese
            if len(sys.argv) > 2:
                addresses = sys.argv[2:]
            else:
                print("Greška: UNICAST zahteva bar jednu IP adresu!")
                print("Primer: python -m examples.video.senderVideo unicast 192.168.1.100")
                sys.exit(1)
    
    # FPS iz argumenta
    if len(sys.argv) > 1 and sys.argv[-1].isdigit():
        target_fps = int(sys.argv[-1])
    
    run_sender(mode, addresses, target_fps)