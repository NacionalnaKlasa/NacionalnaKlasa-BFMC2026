import socket
import json
import threading
import time

# =============================================
# 🔧 NETWORK CONFIG — change PC_IP to your PC's IP
# =============================================
PC_IP = "192.168.50.102"       # ← your PC's IP
CAR_PORT = 5005              # Car listens here
PC_PORT = 5005               # PC listens here

# UDP sockets
sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_recv.bind(("0.0.0.0", CAR_PORT))
sock_recv.setblocking(False)

sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_to_pc(data):
    """Send car state to PC for visualization."""
    try:
        msg = json.dumps(data).encode()
        sock_send.sendto(msg, (PC_IP, PC_PORT))
    except:
        pass


def receive_from_pc():
    """Non-blocking receive commands from PC."""
    try:
        data, _ = sock_recv.recvfrom(4096)
        return json.loads(data.decode())
    except:
        return None


# =============================================
# 📤 Call this every loop tick to send position to PC
# =============================================
def send_position(car_x, car_y, car_angle, speed=0.0):
    send_to_pc({
        "car_x": car_x,
        "car_y": car_y,
        "car_angle": car_angle,
        "speed": speed,
    })


# =============================================
# 📥 Call this every loop tick to get commands from PC
# =============================================
def get_command():
    """
    Returns dict or None. Possible commands:
        {"cmd": "goal",  "goal_x": ..., "goal_y": ...}
        {"cmd": "steer", "correction": ..., "target_x": ..., "target_y": ..., "heading": ...}
        {"cmd": "mode",  "mode": "auto" / "manual"}
        {"cmd": "stop"}
    """
    return receive_from_pc()


# =============================================
# EXAMPLE: Integration with your BFMC car loop
# =============================================
if __name__ == "__main__":
    print("🚗 Car receiver running...")
    print(f"   Listening on port {CAR_PORT}")
    print(f"   Sending to PC {PC_IP}:{PC_PORT}")

    mode = "manual"

    while True:
        # 📥 Get command from PC
        cmd = get_command()
        if cmd:
            print(f"   Received: {cmd}")

            if cmd.get("cmd") == "mode":
                mode = cmd["mode"]
                print(f"   Mode: {mode}")

            elif cmd.get("cmd") == "goal":
                goal_x = cmd["goal_x"]
                goal_y = cmd["goal_y"]
                print(f"   Goal: ({goal_x:.0f}, {goal_y:.0f})")

            elif cmd.get("cmd") == "steer" and mode == "auto":
                correction = cmd["correction"]
                # car.set_steering(correction)
                # car.set_speed(...)
                print(f"   Steer: {correction:.3f} rad")

            elif cmd.get("cmd") == "stop":
                # car.stop()
                print("   STOP")

        # 📤 Send current position to PC
        # Replace with real values from your camera/IMU:
        car_x, car_y = 1000.0, 2000.0     # ← car.get_position()
        car_angle = 0.0                     # ← car.get_heading()
        speed = 0.0                         # ← car.get_speed()
        send_position(car_x, car_y, car_angle, speed)

        time.sleep(0.033)  # ~30 Hz