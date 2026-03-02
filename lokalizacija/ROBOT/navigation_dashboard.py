import pygame
import math
import networkx as nx
import re
import os
import json
import threading
import paho.mqtt.client as mqtt

# --- SETTINGS ---
TRACK_IMAGE_PATH = "/home/konstantin/Downloads/LOCAL/staza_smanjena.png"
GRAPH_FILE_PATH = "/home/konstantin/Downloads/LOCAL/staza_graf.graphml"
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60

# Distance in pixels to consider a node "visited"
VISIT_THRESHOLD = 60.0

# --- CONNECTION SETTINGS (Robot Data) ---
MQTT_BROKER = "test.mosquitto.org" # Or your Raspberry Pi IP (e.g., "192.168.1.5")
MQTT_TOPIC = "robot/telemetry"

# Shared variable to store data coming from the robot
ROBOT_DATA = {
    "speed": 0.0,
    "steering_angle": 0.0,
    "connected": False
}

# --- COLORS ---
WHITE = (255, 255, 255)
RED_GOAL = (255, 50, 50)
BLUE_START = (50, 50, 255)
GRAY_PATH = (200, 200, 200)
GREEN_FUTURE = (0, 255, 0)
CYAN_VISITED = (0, 200, 200)
YELLOW_TARGET = (255, 215, 0)
BLACK = (0, 0, 0)
ORANGE_CAR = (255, 140, 0)

# --- ROBOT CAR CLASS ---
class RobotCar:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0.0
        self.current_speed = 0.0
        self.current_steering_angle = 0.0

    def update_physics(self):
        # NOTE: This calculates position based on received Speed/Angle.
        # This is "Dead Reckoning".
        self.x += self.current_speed * math.cos(self.angle)
        self.y += self.current_speed * math.sin(self.angle)
        
        if self.current_steering_angle != 0 and self.current_speed != 0:
            # Formula: Angular Velocity = Velocity / Wheelbase * tan(Steering)
            self.angle += (self.current_speed / 40.0) * math.tan(self.current_steering_angle)

    def draw(self, screen, factor):
        ex, ey = int(self.x * factor), int(self.y * factor)
        pygame.draw.circle(screen, ORANGE_CAR, (ex, ey), int(12 * factor))
        length = 30 * factor
        dx = ex + length * math.cos(self.angle)
        dy = ey + length * math.sin(self.angle)
        pygame.draw.line(screen, (0, 0, 255), (ex, ey), (dx, dy), 3)

# --- DATA RECEIVER FUNCTIONS (MQTT) ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
        ROBOT_DATA["connected"] = True
    else:
        print(f"❌ Connection failed, code: {rc}")

def on_message(client, userdata, msg):
    try:
        # We expect a JSON string like: {"speed": 5.0, "angle": 0.1}
        payload = msg.payload.decode()
        data = json.loads(payload)
        
        # Update the shared variable safely
        ROBOT_DATA["speed"] = float(data.get("speed", 0))
        ROBOT_DATA["steering_angle"] = float(data.get("angle", 0)) 
        # Note: Ensure the robot sends 'angle' as steering angle (radians)
        
    except Exception as e:
        print(f"⚠️ Error parsing data: {e}")

def start_data_receiver():
    """Starts the MQTT listener in a background thread"""
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        print(f"Connecting to {MQTT_BROKER}...")
        client.connect(MQTT_BROKER, 1883, 60)
        client.loop_forever() # Blocks this thread (which is fine, it's a daemon)
    except Exception as e:
        print(f"❌ Could not connect to Broker: {e}")

# --- GRAPH LOGIC ---
def load_graph_and_coordinates(path):
    if not os.path.exists(path): return nx.Graph(), {}
    try: G = nx.read_graphml(path)
    except: return nx.Graph(), {}

    pos = {}
    for node, data in G.nodes(data=True):
        x, y = None, None
        if 'x' in data and 'y' in data:
            x, y = float(data['x']), float(data['y'])
        else:
            for k, v in data.items():
                s = str(v)
                mx = re.search(r'x=["\']?([\d\.]+)["\']?', s)
                my = re.search(r'y=["\']?([\d\.]+)["\']?', s)
                if mx and my:
                    x, y = float(mx.group(1)), float(my.group(1)); break
        if x is not None: pos[node] = (x, y)

    for u, v in G.edges():
        if u in pos and v in pos:
            dist = math.sqrt((pos[u][0]-pos[v][0])**2 + (pos[u][1]-pos[v][1])**2)
            G[u][v]['weight'] = dist
    return G, pos

def find_path(G, start, end):
    try:
        path = nx.dijkstra_path(G, start, end, weight='weight')
        return path
    except: return []

# --- DRAWING PROGRESS ---
def draw_advanced_navigation(screen, pos, factor, path, target_index):
    if len(path) < 2: return
    points = [(int(pos[n][0]*factor), int(pos[n][1]*factor)) for n in path]

    # Draw Lines
    for i in range(len(points) - 1):
        start_pos = points[i]
        end_pos = points[i+1]
        
        if i < target_index - 1:
            color = CYAN_VISITED; thickness = 4
        elif i == target_index - 1:
            color = GREEN_FUTURE; thickness = 6
        else:
            color = GREEN_FUTURE; thickness = 4
        pygame.draw.line(screen, color, start_pos, end_pos, thickness)

    # Draw Nodes
    for i, n in enumerate(path):
        sx, sy = points[i]
        if i < target_index:
            pygame.draw.circle(screen, CYAN_VISITED, (sx, sy), 6)
        elif i == target_index:
            pygame.draw.circle(screen, YELLOW_TARGET, (sx, sy), 12)
            pygame.draw.circle(screen, BLACK, (sx, sy), 13, 1)
        else:
            pygame.draw.circle(screen, GREEN_FUTURE, (sx, sy), 5)

# --- MAIN ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dashboard: Live Robot Data")
    clock = pygame.time.Clock()
    font_large = pygame.font.SysFont("Arial", 24, bold=True)
    font_small = pygame.font.SysFont("Arial", 16)

    # 1. Start the Data Receiver (Thread)
    data_thread = threading.Thread(target=start_data_receiver)
    data_thread.daemon = True # Kills thread when app closes
    data_thread.start()

    # 2. Load Assets
    try:
        orig = pygame.image.load(TRACK_IMAGE_PATH).convert()
        w, h = orig.get_size()
        factor = min(SCREEN_WIDTH/w, SCREEN_HEIGHT/h)
        map_image = pygame.transform.smoothscale(orig, (int(w*factor), int(h*factor)))
    except:
        w, h = 5000, 5000; factor = 0.16
        map_image = pygame.Surface((800, 800)); map_image.fill(WHITE)

    G, pos = load_graph_and_coordinates(GRAPH_FILE_PATH)
    if not pos: 
        pos = {'n0': (100,100), 'n1': (500,500)}; G.add_edge('n0','n1')

    # Path setup
    start_node = list(pos.keys())[0]
    goal_node = list(pos.keys())[-1]
    path = find_path(G, start_node, goal_node)
    
    target_index = 1
    next_node_id = path[target_index] if len(path) > 1 else str(start_node)

    # Car setup
    sx, sy = pos[start_node]
    auto = RobotCar(sx, sy)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

            # --- MOUSE CLICK: Set new Goal ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                real_x, real_y = mx / factor, my / factor

                # Find nearest node to click (Goal)
                min_dist = float('inf'); new_goal = None
                for n, (nx, ny) in pos.items():
                    d = math.sqrt((nx-real_x)**2 + (ny-real_y)**2)
                    if d < min_dist: min_dist = d; new_goal = n
                
                # Find nearest node to Car (Start)
                min_start_dist = float('inf'); new_start = None
                for n, (nx, ny) in pos.items():
                     d = math.sqrt((nx-auto.x)**2 + (ny-auto.y)**2)
                     if d < min_start_dist: min_start_dist = d; new_start = n

                if new_goal and new_start:
                    goal_node = new_goal
                    start_node = new_start
                    path = find_path(G, start_node, goal_node)
                    target_index = 1
                    next_node_id = path[target_index] if len(path) > 1 else "GOAL"

        # --- UPDATE CAR FROM ROBOT DATA ---
        # Instead of keyboard, we read from the shared variable
        auto.current_speed = ROBOT_DATA["speed"]
        auto.current_steering_angle = ROBOT_DATA["steering_angle"]
        
        # Calculate new position based on that data
        auto.update_physics()
        auto.x = max(0, min(auto.x, w))
        auto.y = max(0, min(auto.y, h))

        # --- CHECKPOINT LOGIC ---
        if len(path) > 1 and target_index < len(path):
            target_id = path[target_index]
            mx, my = pos[target_id]
            dist_to_target = math.sqrt((auto.x - mx)**2 + (auto.y - my)**2)
            
            if dist_to_target < VISIT_THRESHOLD:
                target_index += 1
                if target_index < len(path):
                    next_node_id = path[target_index]
                else:
                    next_node_id = "ARRIVED!"

        # --- DRAWING ---
        screen.fill(BLACK)
        screen.blit(map_image, (0, 0))
        
        # Draw edges
        for u, v in G.edges():
            if u in pos and v in pos:
                pygame.draw.line(screen, (80,80,80), 
                                (int(pos[u][0]*factor), int(pos[u][1]*factor)), 
                                (int(pos[v][0]*factor), int(pos[v][1]*factor)), 1)
        
        draw_advanced_navigation(screen, pos, factor, path, target_index)
        auto.draw(screen, factor)

        # --- INFO PANEL ---
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - 310, 10, 300, 130))
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - 310, 10, 300, 130), 2)

        # Connection Status
        status_color = (0, 200, 0) if ROBOT_DATA["connected"] else (200, 0, 0)
        status_text = "ONLINE" if ROBOT_DATA["connected"] else "WAITING..."

        texts = [
            (f"STATUS: {status_text}", status_color, font_small),
            (f"NEXT TARGET: {next_node_id}", YELLOW_TARGET, font_large),
            (f"Speed: {auto.current_speed:.1f}", BLACK, font_small),
            (f"Steering: {math.degrees(auto.current_steering_angle):.1f}°", BLACK, font_small),
            ("Click map to change Goal", BLACK, font_small)
        ]

        for i, (txt, color, font) in enumerate(texts):
            if color == YELLOW_TARGET:
                 render = font.render(txt, True, (200, 180, 0))
            else:
                 render = font.render(txt, True, color)
            screen.blit(render, (SCREEN_WIDTH - 300, 20 + i*25))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()