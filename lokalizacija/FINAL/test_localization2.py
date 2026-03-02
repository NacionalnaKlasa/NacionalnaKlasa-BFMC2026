import pygame
import math
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

    # Click states: "start" → "goal" → "driving"
    click_mode = "start"
    car_x, car_y = 0, 0
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
                mx, my = event.pos
                wx, wy = mx / factor, my / factor

                if click_mode == "start":
                    # First click = set car starting position
                    car_x, car_y = wx, wy
                    car_angle = 0.0
                    click_mode = "goal"
                    print(f"📍 Start set: ({wx:.0f}, {wy:.0f})")

                elif click_mode == "goal":
                    # Second click = set goal, start driving
                    nav.set_goal(car_x, car_y, goal_xy=(wx, wy))
                    goal_set = True
                    click_mode = "driving"
                    print(f"🎯 Goal set: ({wx:.0f}, {wy:.0f})")

                elif click_mode == "driving":
                    # Click during/after driving = new goal from current position
                    nav.set_goal(car_x, car_y, goal_xy=(wx, wy))
                    goal_set = True
                    print(f"🎯 New goal: ({wx:.0f}, {wy:.0f})")

        # Auto-drive toward goal
        if goal_set:
            # =============================================     Potrebno dodati na auticu
            # 📥 RECEIVE FROM CAR — replace these 2 lines
            # car_x, car_y = car.get_position()
            # car_angle    = car.get_heading()
            # =============================================
            state = nav.update(car_x, car_y)
            if not state["arrived"]:
                correction = nav.get_steering_angle(car_x, car_y, car_angle)

                # ============================================= Potrebno dodati na auticu
                # 📤 SEND TO CAR — replace these 3 lines
                # car.set_steering(correction)
                # car.set_speed(speed)
                #
                # Available to send:
                #   correction          → steering error (radians)
                #   state["target_x"]   → next waypoint X
                #   state["target_y"]   → next waypoint Y
                #   state["distance"]   → distance to waypoint
                #   state["heading"]    → absolute angle to target
                # =============================================

                car_angle += correction * 0.3               # ← remove this
                car_x += speed * math.cos(car_angle)        # ← remove this
                car_y += speed * math.sin(car_angle)        # ← remove this
                print(f"Car position: ({car_x:.0f}, {car_y:.0f}), Angle: {car_angle:.2f}")
            else:
                goal_set = False
                # car.stop()                                # ← add this
                print("🏁 ARRIVED! Click to set new goal.")

        # --- DRAW ---
        screen.fill((30, 30, 30))

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

            if state and not state["arrived"]:
                tx, ty = int(state["target_x"] * factor), int(state["target_y"] * factor)
                pygame.draw.circle(screen, (255, 215, 0), (tx, ty), 10)

        # Car (orange circle + blue direction line)
        if click_mode != "start":
            ex, ey = int(car_x * factor), int(car_y * factor)
            pygame.draw.circle(screen, (255, 140, 0), (ex, ey), 8)
            dx = ex + 20 * math.cos(car_angle)
            dy = ey + 20 * math.sin(car_angle)
            pygame.draw.line(screen, (0, 0, 255), (ex, ey), (int(dx), int(dy)), 3)

        # HUD
        if click_mode == "start":
            txt = font.render("Click to set STARTING POINT", True, (0, 200, 255))
        elif click_mode == "goal":
            txt = font.render("Click to set GOAL", True, (255, 215, 0))
        elif goal_set and state and not state["arrived"]:
            txt = font.render(
                f"Progress: {state['progress']}/{state['total_nodes']} | "
                f"Dist: {state['distance']:.0f}", True, (255, 255, 255))
        else:
            txt = font.render("ARRIVED! Click to set new goal", True, (0, 255, 0))
        screen.blit(txt, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()