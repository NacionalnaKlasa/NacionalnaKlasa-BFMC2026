import pygame
import math
import threading
from localization import LocalizationModule
from tcpLib import PCServer  

GRAPH_PATH = r"C:\Users\Korisnik\Desktop\BOSCH\CODE\Floyd\GRAPH\staza_graf.graphml"
TRACK_IMAGE_PATH = r"C:\Users\Korisnik\Desktop\BOSCH\graph\staza_smanjena.png"
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

SERVER_PORT = 65432

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PC 1 - Main control and visualisation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18, bold=True)

    try:
        track_img = pygame.image.load(TRACK_IMAGE_PATH)
        img_w, img_h = track_img.get_size()
        factor = min(SCREEN_WIDTH / img_w, SCREEN_HEIGHT / img_h)
        track_img = pygame.transform.scale(track_img, (int(img_w * factor), int(img_h * factor)))
    except:
        print("Picture is not found")
        track_img = None
        factor = 0.2

    nav = LocalizationModule(GRAPH_PATH, visit_threshold=60.0)
    nodes = nav.get_all_nodes()

    pc = PCServer(port=SERVER_PORT)
    server_thread = threading.Thread(target=pc.start, daemon=True)
    server_thread.start()
    
    # --- Varijable za stanje automobila ---
    click_mode = "start"
    car_x, car_y = 0.0, 0.0
    car_angle = 0.0
    current_speed = 0.0
    steering_angle = 0.0
    goal_set = False
    state = None

    last_msg_time = pygame.time.get_ticks()
    connection_active = False
    was_connected = False # Pamti da li je RPi bio tu u prošlom frejmu

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        is_connected = pc.conn is not None

        # ==========================================================
        # LOGIKA RESETOVANJA PRI PONOVNOJ KONEKCIJI
        # ==========================================================
        if is_connected and not was_connected:
            print("\n[SYSTEM] RPi se ponovo povezao! Resetujem mapu...")
            click_mode = "start" # Omogućava ti da opet klikneš prvu tačku
            goal_set = False
            state = None
            connection_active = False
            current_speed = 0.0
            steering_angle = 0.0
            car_x, car_y = 0.0, 0.0

        if not is_connected and was_connected:
            print("\n[SYSTEM] Konekcija sa RPi prekinuta! Cekam novu...")
            connection_active = False
            current_speed = 0.0
            steering_angle = 0.0

        was_connected = is_connected

        # ==========================================================
        # 1. TCP KOMUNIKACIJA I WATCHDOG
        # ==========================================================
        if is_connected:
            poruke = pc.get_data()
            
            if poruke:
                last_msg_time = pygame.time.get_ticks()
                connection_active = True
                
            for msg in poruke:
                if msg.get("type") == "telemetry":
                    current_speed = msg.get("speed", 0.0)
                    steering_angle = msg.get("steering_angle", 0.0)

            if pygame.time.get_ticks() - last_msg_time > 500:
                current_speed = 0.0
                steering_angle = 0.0
                connection_active = False 

        # ==========================================================
        # 2. IZRACUNAVANJE KOORDINATA AUTA
        # ==========================================================
        if click_mode != "start" and is_connected:
            if abs(current_speed) > 0.1:
                rate_factor = 20.0 
                car_angle += (current_speed * math.tan(steering_angle) / 100.0) * (dt * rate_factor)
                car_x += current_speed * math.cos(car_angle) * (dt * rate_factor)
                car_y += current_speed * math.sin(car_angle) * (dt * rate_factor)

        # ==========================================================
        # 3. PYGAME STREAM I KONTROLA KLIKOVA
        # ==========================================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and is_connected:
                mx, my = event.pos
                wx, wy = mx / factor, my / factor

                if click_mode == "start":
                    car_x, car_y = wx, wy
                    car_angle = 0.0
                    click_mode = "goal"
                    last_msg_time = pygame.time.get_ticks()
                    
                    print(f"📍 Start postavljen na PC-u: ({wx:.0f}, {wy:.0f})")
                    pc.send_data({"type": "init"})
                    print("📤 Init signal poslat na RPi.")

                elif click_mode == "goal" or click_mode == "driving":
                    nav.set_goal(car_x, car_y, goal_xy=(wx, wy))
                    goal_set = True
                    click_mode = "driving"
                    print(f"🎯 Nova meta postavljena: ({wx:.0f}, {wy:.0f})")

        # ==========================================================
        # 4. UPDATE NAVIGACIJE
        # ==========================================================
        if goal_set:
            state = nav.update(car_x, car_y)
            if state["arrived"]:
                goal_set = False
                print("🏁 Auto je stigao na cilj! Klikni za novu metu.")

        # ==========================================================
        # 5. CRTANJE NA EKRANU
        # ==========================================================
        screen.fill((30, 30, 30))

        if track_img:
            screen.blit(track_img, (0, 0))

        for nid, (nx_, ny_) in nodes.items():
            pygame.draw.circle(screen, (100, 100, 100), (int(nx_ * factor), int(ny_ * factor)), 3)

        if goal_set:
            path_coords = nav.get_path_coords()
            if len(path_coords) > 1:
                points = [(int(x * factor), int(y * factor)) for x, y in path_coords]
                pygame.draw.lines(screen, (0, 255, 0), False, points, 2)

            if state and not state["arrived"]:
                tx, ty = int(state["target_x"] * factor), int(state["target_y"] * factor)
                pygame.draw.circle(screen, (255, 215, 0), (tx, ty), 10)

        # Crtamo kružić i liniju pravca samo ako smo prošli početni klik i konekcija je živa
        if click_mode != "start" and is_connected and connection_active:
            ex, ey = int(car_x * factor), int(car_y * factor)
            pygame.draw.circle(screen, (255, 140, 0), (ex, ey), 8)
            dx = ex + 20 * math.cos(car_angle)
            dy = ey + 20 * math.sin(car_angle)
            pygame.draw.line(screen, (0, 0, 255), (ex, ey), (int(dx), int(dy)), 3)

        # Prikaz statusnog teksta
        if not is_connected:
            txt = font.render("Cekam da se RPi poveze...", True, (255, 50, 50))
        elif not connection_active and click_mode != "start":
            txt = font.render("Konekcija prekinuta! Auto zaustavljen.", True, (255, 0, 0))
        elif click_mode == "start":
            txt = font.render("RPi povezan! Klikni da postavis STARTNU poziciju.", True, (0, 200, 255))
        elif click_mode == "goal":
            txt = font.render("Klikni na stazu da postavis CILJ.", True, (255, 215, 0))
        elif goal_set and state and not state["arrived"]:
            txt = font.render(f"Pratim RPi... X: {car_x:.0f}, Y: {car_y:.0f} | Do cilja: {state['distance']:.0f}", True, (255, 255, 255))
        else:
            txt = font.render("STIGLI SMO! Klikni za novi cilj.", True, (0, 255, 0))
        
        screen.blit(txt, (10, 10))
        pygame.display.flip()

    pc.closing()
    pygame.quit()

if __name__ == "__main__":
    main()