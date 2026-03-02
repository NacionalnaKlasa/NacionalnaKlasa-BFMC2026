import pygame
import math
import sys
from localization import LocalizationModule

GRAPH_PATH = "/home/konstantin/Desktop/lokalizacija/LOCAL/staza_graf.graphml"
TRACK_IMAGE_PATH = "/home/konstantin/Desktop/lokalizacija/LOCAL/staza_smanjena.png"
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Visual Localization Test")
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

    # Init navigation
    nav = LocalizationModule(GRAPH_PATH, visit_threshold=60.0)
    nodes = nav.get_all_nodes()

    # Car starts at first node
    node_ids = list(nodes.keys())
    car_x, car_y = nodes[node_ids[0]]
    car_angle = 0.0
    speed = 3.0
    goal_set = False
    state = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Click to set goal (same as your Pygame version)
                mx, my = event.pos
                goal_x, goal_y = mx / factor, my / factor
                nav.set_goal(car_x, car_y, goal_xy=(goal_x, goal_y))
                goal_set = True
                print(f"🎯 Goal set: ({goal_x:.0f}, {goal_y:.0f})")

        # =============================================
        # 📥 RECEIVE FROM CAR (replace these 3 lines)
        # Currently simulated. On real car, get from camera/IMU:
        #
        #   car_x, car_y = car.get_position()       # from camera localization
        #   car_angle    = car.get_heading()         # from IMU or camera
        # =============================================

        # Auto-drive toward goal
        if goal_set:
            state = nav.update(car_x, car_y)
            if not state["arrived"]:
                correction = nav.get_steering_angle(car_x, car_y, car_angle)
                car_angle += correction * 0.3
                car_x += speed * math.cos(car_angle)
                car_y += speed * math.sin(car_angle)

                 # =============================================
                # 📤 SEND TO CAR (replace these 3 lines)
                # Currently simulated. On real car, send commands:
                #
                #   car.set_steering(correction)         # radians
                #   car.set_speed(speed)                 # or stop if arrived
                #
                # What you can send:
                #   correction         → steering angle error (radians)
                #   state["target_x"]  → next waypoint X (map coords)
                #   state["target_y"]  → next waypoint Y (map coords)
                #   state["distance"]  → distance to next waypoint
                #   state["heading"]   → absolute angle to target
                #   state["arrived"]   → True = stop the car
                # =============================================
                car_angle += correction * 0.3
                car_x += speed * math.cos(car_angle)
                car_y += speed * math.sin(car_angle)
            else:
                #car.stop()
                state["arrived"] = True
                goal_set = False

        # --- DRAW ---
        screen.fill((30, 30, 30))

        # Track image
        if track_img:
            screen.blit(track_img, (0, 0))

        # All nodes (gray dots)
        for nid, (nx_, ny_) in nodes.items():
            pygame.draw.circle(screen, (100, 100, 100), (int(nx_ * factor), int(ny_ * factor)), 3)

        # Path (green line + yellow target)
        if goal_set:
            path_coords = nav.get_path_coords()
            if len(path_coords) > 1:
                points = [(int(x * factor), int(y * factor)) for x, y in path_coords]
                pygame.draw.lines(screen, (0, 255, 0), False, points, 2)

            # Target node (yellow)
            if state and not state["arrived"]:
                tx, ty = int(state["target_x"] * factor), int(state["target_y"] * factor)
                pygame.draw.circle(screen, (255, 215, 0), (tx, ty), 10)

        # Car (orange circle + blue direction line)
        ex, ey = int(car_x * factor), int(car_y * factor)
        pygame.draw.circle(screen, (255, 140, 0), (ex, ey), 8)
        dx = ex + 20 * math.cos(car_angle)
        dy = ey + 20 * math.sin(car_angle)
        pygame.draw.line(screen, (0, 0, 255), (ex, ey), (int(dx), int(dy)), 3)

        # HUD
        if state and goal_set:
            if state["arrived"]:
                txt = font.render("ARRIVED!", True, (0, 255, 0))
            else:
                txt = font.render(
                    f"Progress: {state['progress']}/{state['total_nodes']} | "
                    f"Dist: {state['distance']:.0f}", True, (255, 255, 255))
            screen.blit(txt, (10, 10))
        else:
            txt = font.render("Click anywhere to set goal", True, (255, 255, 255))
            screen.blit(txt, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()