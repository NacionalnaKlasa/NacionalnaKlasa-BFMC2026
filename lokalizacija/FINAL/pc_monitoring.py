import pygame
import math
import threading
from localization import LocalizationModule
from tcpLib import PCServer 
from config import *

class PCMonitoring:
    def __init__(self, graph_path=GRAPH_PATH, track_image_path=TRACK_BACKGROUND_PATH, 
                 port=65432, width=1000, height=800):
        """
        Inicialisation of whole system, Pygame, TCP server and navigation.
        User can forward their paths, or default values from config.py will be used.
        """
        self.width = width
        self.height = height
        
        # 1. Inicijalisation of Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("PC 1 - Main control and visualisation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18, bold=True)

        # 2. Inicijalisation of track image
        self._load_track_image(track_image_path)

        # 3. Inicijalisation of navigation and nodes
        self.nav = LocalizationModule(graph_path, visit_threshold=60.0)
        self.nodes = self.nav.get_all_nodes()

        # 4. Starting TCP Servera
        self.pc = PCServer(port=port)
        self.server_thread = threading.Thread(target=self.pc.start, daemon=True)
        self.server_thread.start()

        self._reset_state()
        self.running = False

    def _load_track_image(self, path):
        
        try:
            track_img = pygame.image.load(path)
            img_w, img_h = track_img.get_size()
            self.factor = min(self.width / img_w, self.height / img_h)
            self.track_img = pygame.transform.scale(track_img, (int(img_w * self.factor), int(img_h * self.factor)))
        except:
            print("[WARNING] Track photo is not found!")
            self.track_img = None
            self.factor = 0.2

    def _reset_state(self):
        
        self.click_mode = "start"
        self.car_x, self.car_y = 0.0, 0.0
        self.car_angle = 0.0
        self.current_speed = 0.0
        self.steering_angle = 0.0
        self.goal_set = False
        self.state = None
        
        self.last_msg_time = pygame.time.get_ticks()
        self.connection_active = False
        self.was_connected = False

    def run(self):
        """Main loop of the program that is called by the end user."""
        self.running = True
        
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            is_connected = self.pc.conn is not None

            # --- Logic of reset when reconnecting ---
            if is_connected and not self.was_connected:
                print("\n[SYSTEM] RPi is connecting again! Reseting map...")
                self._reset_state()

            if not is_connected and self.was_connected:
                print("\n[SYSTEM] Connection with RPi lost! Waiting for new connection...")
                self.connection_active = False
                self.current_speed = 0.0
                self.steering_angle = 0.0

            self.was_connected = is_connected

            # --- 1. TCP Komunication ---
            if is_connected:
                poruke = self.pc.get_data()
                if poruke:
                    self.last_msg_time = pygame.time.get_ticks()
                    self.connection_active = True
                    
                for msg in poruke:
                    if msg.get("type") == "telemetry":
                        self.current_speed = msg.get("speed", 0.0)
                        self.steering_angle = msg.get("steering_angle", 0.0)

                if pygame.time.get_ticks() - self.last_msg_time > 500:
                    self.current_speed = 0.0
                    self.steering_angle = 0.0
                    self.connection_active = False 

            # --- 2. Calculating coords ---
            if self.click_mode != "start" and is_connected:
                if abs(self.current_speed) > 0.1:
                    rate_factor = 20.0 
                    self.car_angle += (self.current_speed * math.tan(self.steering_angle) / 100.0) * (dt * rate_factor)
                    self.car_x += self.current_speed * math.cos(self.car_angle) * (dt * rate_factor)
                    self.car_y += self.current_speed * math.sin(self.car_angle) * (dt * rate_factor)

            # --- 3. Pygame events and click ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and is_connected:
                    mx, my = event.pos
                    wx, wy = mx / self.factor, my / self.factor

                    if self.click_mode == "start":
                        self.car_x, self.car_y = wx, wy
                        self.car_angle = 0.0
                        self.click_mode = "goal"
                        self.last_msg_time = pygame.time.get_ticks()
                        print(f"📍 Start set on PC: ({wx:.0f}, {wy:.0f})")
                        self.pc.send_data({"type": "init"})
                        
                    elif self.click_mode in ["goal", "driving"]:
                        self.nav.set_goal(self.car_x, self.car_y, goal_xy=(wx, wy))
                        self.goal_set = True
                        self.click_mode = "driving"
                        print(f"🎯 New goal set: ({wx:.0f}, {wy:.0f})")

            # --- 4. Update Navigacije ---
            if self.goal_set:
                self.state = self.nav.update(self.car_x, self.car_y)
                if self.state["arrived"]:
                    self.goal_set = False
                    print("🏁 Car arrived at the goal! Click for new goal.")

            # --- 5. Crtanje ---
            self._draw_screen(is_connected)

        # Gašenje na kraju petlje
        self.cleanup()

    def _draw_screen(self, is_connected):
        
        self.screen.fill((30, 30, 30))

        if self.track_img:
            self.screen.blit(self.track_img, (0, 0))

        for nid, (nx_, ny_) in self.nodes.items():
            pygame.draw.circle(self.screen, (100, 100, 100), (int(nx_ * self.factor), int(ny_ * self.factor)), 3)

        if self.goal_set:
            path_coords = self.nav.get_path_coords()
            if len(path_coords) > 1:
                points = [(int(x * self.factor), int(y * self.factor)) for x, y in path_coords]
                pygame.draw.lines(self.screen, (0, 255, 0), False, points, 2)

            if self.state and not self.state["arrived"]:
                tx, ty = int(self.state["target_x"] * self.factor), int(self.state["target_y"] * self.factor)
                pygame.draw.circle(self.screen, (255, 215, 0), (tx, ty), 10)

        if self.click_mode != "start" and is_connected and self.connection_active:
            ex, ey = int(self.car_x * self.factor), int(self.car_y * self.factor)
            pygame.draw.circle(self.screen, (255, 140, 0), (ex, ey), 8)
            dx = ex + 20 * math.cos(self.car_angle)
            dy = ey + 20 * math.sin(self.car_angle)
            pygame.draw.line(self.screen, (0, 0, 255), (ex, ey), (int(dx), int(dy)), 3)

        self._draw_status_text(is_connected)
        pygame.display.flip()

    def _draw_status_text(self, is_connected):
        
        if not is_connected:
            txt = self.font.render("Waiting for RPi to connect...", True, (255, 50, 50))
        elif not self.connection_active and self.click_mode != "start":
            txt = self.font.render("Connection lost! Car stopped.", True, (255, 0, 0))
        elif self.click_mode == "start":
            txt = self.font.render("RPi connected! Click to set START position.", True, (0, 200, 255))
        elif self.click_mode == "goal":
            txt = self.font.render("Click on the track to set GOAL.", True, (255, 215, 0))
        elif self.goal_set and self.state and not self.state["arrived"]:
            txt = self.font.render(f"Tracking RPi... X: {self.car_x:.0f}, Y: {self.car_y:.0f} | To goal: {self.state['distance']:.0f}", True, (255, 255, 255))
        else:
            txt = self.font.render("WE ARRIVED! Click for new goal.", True, (0, 255, 0))
        
        self.screen.blit(txt, (10, 10))

    def cleanup(self):
        
        print("[SYSTEM] Closing monitoring...")
        self.pc.closing()
        pygame.quit()