import pygame
import math
import socket
import json
import threading
from localization import LocalizationModule

GRAPH_PATH = "/home/konstantin/Desktop/lokalizacija/LOCAL/staza_graf.graphml"
TRACK_IMAGE_PATH = "/home/konstantin/Desktop/lokalizacija/LOCAL/staza_smanjena.png"
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

# =============================================
# 🔧 NETWORK CONFIG — change CAR_IP to your car's IP
# =============================================
CAR_IP = "192.168.50.1"     # ← your car's IP
PC_PORT = 5005               # PC listens here (receives from car)
CAR_PORT = 5005              # Car listens here (receives from PC)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PC Visualizer — Manual + Auto")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18, bold=True)

    # Load track image
    try:
        track_img = pygame.image.load(TRACK_IMAGE_PATH)
        img_w, img_h = track_img.get_size()
        factor = min(SCREEN_WIDTH / img_w, SCREEN_HEIGHT / img_h)
        track_img = pygame.transform.scale(track_img, (int(img_w * factor), int(img_h * factor)))
    except:
        track_img = None
        factor = 0.2

    # Init navigation (for path display + steering calc)
    nav = LocalizationModule(GRAPH_PATH, visit_threshold=60.0)
    nodes = nav.get_all_nodes()

    # UDP sockets
    sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_recv.bind(("0.0.0.0", PC_PORT))
    sock_recv.setblocking(False)

    # State
    car_x, car_y, car_angle, car_speed = 0.0, 0.0, 0.0, 0.0
    click_mode = "start"
    goal_set = False
    state = None
    mode = "manual"  # "manual" or "auto"
    trail = []       # car position history

    # =============================================
    def send_to_car(data):
        """Send dict to car via UDP."""
        try:
            msg = json.dumps(data).encode()
            sock_send.sendto(msg, (CAR_IP, CAR_PORT))
        except:
            pass

    def receive_from_car():
        """Non-blocking receive from car."""
        try:
            data, _ = sock_recv.recvfrom(4096)
            return json.loads(data.decode())
        except:
            return None
    # =============================================

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # M = toggle manual/auto mode
                if event.key == pygame.K_m:
                    mode = "auto" if mode == "manual" else "manual"
                    send_to_car({"cmd": "mode", "mode": mode})
                    print(f"🔄 Mode: {mode.upper()}")

                # R = reset (pick new start)
                if event.key == pygame.K_r:
                    click_mode = "start"
                    goal_set = False
                    trail.clear()
                    send_to_car({"cmd": "stop"})
                    print("🔄 Reset")

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                wx, wy = mx / factor, my / factor

                if click_mode == "start":
                    car_x, car_y = wx, wy
                    car_angle = 0.0
                    click_mode = "goal"
                    trail.clear()
                    print(f"📍 Start set: ({wx:.0f}, {wy:.0f})")

                elif click_mode == "goal":
                    nav.set_goal(car_x, car_y, goal_xy=(wx, wy))
                    goal_set = True
                    click_mode = "driving"
                    # Send goal to car
                    send_to_car({"cmd": "goal", "goal_x": wx, "goal_y": wy})
                    print(f"🎯 Goal set: ({wx:.0f}, {wy:.0f})")

                elif click_mode == "driving":
                    nav.set_goal(car_x, car_y, goal_xy=(wx, wy))
                    goal_set = True
                    send_to_car({"cmd": "goal", "goal_x": wx, "goal_y": wy})
                    print(f"🎯 New goal: ({wx:.0f}, {wy:.0f})")

        # =============================================
        # 📥 RECEIVE FROM CAR (position updates)
        # =============================================
        car_data = receive_from_car()
        # if car_data:
        #     car_x = car_data.get("car_x", car_x)
        #     car_y = car_data.get("car_y", car_y)
        #     car_angle = car_data.get("car_angle", car_angle)
        #     car_speed = car_data.get("speed", car_speed)
        #     trail.append((car_x, car_y))
        #     if len(trail) > 2000:
        #         trail.pop(0)

        # # Navigation update (runs on PC for display)
        # if goal_set:
        #     state = nav.update(car_x, car_y)

        #     if mode == "auto" and not state["arrived"]:
        #         correction = nav.get_steering_angle(car_x, car_y, car_angle)
        #         # =============================================
        #         # 📤 SEND STEERING TO CAR (auto mode only)
        #         # =============================================
        #         send_to_car({
        #             "cmd": "steer",
        #             "correction": correction,
        #             "target_x": state["target_x"],
        #             "target_y": state["target_y"],
        #             "heading": state["heading"],
        #         })

        #     if state["arrived"]:
        #         goal_set = False
        #         send_to_car({"cmd": "stop"})
        #         print("🏁 ARRIVED!")

        # Send car position to RPI for graph calculation
        if goal_set:
            send_to_car({
                "cmd": "position",
                "car_x": car_x,
                "car_y": car_y,
                "car_angle": car_angle,
                "mode": mode
            })

            # Receive navigation info from RPI
            nav_info = receive_from_car()
            if nav_info:
                state = nav_info  # Use navigation info from RPI
                # Optionally: send steering command if in auto mode
                if mode == "auto" and not state.get("arrived", False):
                    send_to_car({
                        "cmd": "steer",
                        "correction": state["correction"],
                        "target_x": state["target_x"],
                        "target_y": state["target_y"],
                        "heading": state["heading"],
                    })
                if state.get("arrived", False):
                    goal_set = False
                    send_to_car({"cmd": "stop"})
                    print("🏁 ARRIVED!")

        # --- DRAW ---
        screen.fill((30, 30, 30))

        if track_img:
            screen.blit(track_img, (0, 0))

        # All nodes (gray dots)
        for nid, (nx_, ny_) in nodes.items():
            pygame.draw.circle(screen, (100, 100, 100), (int(nx_ * factor), int(ny_ * factor)), 3)

        # Trail (white dots — where car has been)
        for tx_, ty_ in trail:
            pygame.draw.circle(screen, (255, 255, 255), (int(tx_ * factor), int(ty_ * factor)), 2)

        # Path (green line + yellow target)
        if goal_set:
            path_coords = nav.get_path_coords()
            if len(path_coords) > 1:
                points = [(int(x * factor), int(y * factor)) for x, y in path_coords]
                pygame.draw.lines(screen, (0, 255, 0), False, points, 2)

            if state and not state["arrived"]:
                tx, ty = int(state["target_x"] * factor), int(state["target_y"] * factor)
                pygame.draw.circle(screen, (255, 215, 0), (tx, ty), 10)

        # Car (orange circle + blue direction)
        if click_mode != "start":
            ex, ey = int(car_x * factor), int(car_y * factor)
            pygame.draw.circle(screen, (255, 140, 0), (ex, ey), 8)
            dx = ex + 20 * math.cos(car_angle)
            dy = ey + 20 * math.sin(car_angle)
            pygame.draw.line(screen, (0, 0, 255), (ex, ey), (int(dx), int(dy)), 3)

        # HUD
        mode_color = (0, 255, 0) if mode == "auto" else (255, 165, 0)
        mode_txt = font.render(f"Mode: {mode.upper()} (M to toggle) | R to reset", True, mode_color)
        screen.blit(mode_txt, (10, SCREEN_HEIGHT - 30))

        if click_mode == "start":
            txt = font.render("Click to set STARTING POINT", True, (0, 200, 255))
        elif click_mode == "goal":
            txt = font.render("Click to set GOAL", True, (255, 215, 0))
        elif goal_set and state and not state["arrived"]:
            txt = font.render(
                f"Progress: {state['progress']}/{state['total_nodes']} | "
                f"Dist: {state['distance']:.0f} | Speed: {car_speed:.1f}", True, (255, 255, 255))
        else:
            txt = font.render("ARRIVED! Click to set new goal", True, (0, 255, 0))
        screen.blit(txt, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    sock_send.close()
    sock_recv.close()
    pygame.quit()

if __name__ == "__main__":
    main()