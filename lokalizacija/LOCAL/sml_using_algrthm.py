import pygame
import math
import networkx as nx
import re
import os

# --- SETTINGS ---
TRACK_IMAGE_PATH = "/home/konstantin/Desktop/lokalizacija/LOCAL/staza_smanjena.png"         
GRAPH_FILE_PATH  = "/home/konstantin/Desktop/lokalizacija/LOCAL/staza_graf.graphml" 
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60

# Distance in pixels to consider a node "visited"
VISIT_THRESHOLD = 60.0

# Colors
WHITE = (255, 255, 255)
RED_GOAL = (255, 50, 50)
BLUE_START = (50, 50, 255)
GRAY_PATH = (200, 200, 200)
GREEN_FUTURE = (0, 255, 0)   # Path yet to be traversed
CYAN_VISITED = (0, 200, 200) # Path already traversed
YELLOW_TARGET = (255, 215, 0) # The node we are currently aiming for
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
        self.x += self.current_speed * math.cos(self.angle)
        self.y += self.current_speed * math.sin(self.angle)
        if self.current_steering_angle != 0 and self.current_speed != 0:
            self.angle += (self.current_speed / 40.0) * math.tan(self.current_steering_angle)

    def draw(self, screen, factor):
        ex, ey = int(self.x * factor), int(self.y * factor)
        pygame.draw.circle(screen, ORANGE_CAR, (ex, ey), int(50 * factor))
        length = 80 * factor
        dx = ex + length * math.cos(self.angle)
        dy = ey + length * math.sin(self.angle)
        pygame.draw.line(screen, (0, 0, 255), (ex, ey), (dx, dy), 14)

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

# --- NEW FUNCTION FOR DRAWING PROGRESS ---
def draw_advanced_navigation(screen, pos, factor, path, target_index):
    """
    Draws the path in 3 colors:
    1. Visited (Cyan)
    2. Current Target (Yellow)
    3. Future (Green)
    """
    if len(path) < 2: return

    # Convert coordinates to screen pixels
    points = [(int(pos[n][0]*factor), int(pos[n][1]*factor)) for n in path]

    # 1. DRAWING LINES
    for i in range(len(points) - 1):
        start_pos = points[i]
        end_pos = points[i+1]

        # If this segment is already crossed (segment index less than target index)
        if i < target_index - 1:
            color = CYAN_VISITED
            thickness = 4
        # If this is the current segment we are driving towards
        elif i == target_index - 1:
            color = GREEN_FUTURE
            thickness = 6 # Slightly thicker
        # Future segments
        else:
            color = GREEN_FUTURE
            thickness = 4

        pygame.draw.line(screen, color, start_pos, end_pos, thickness)

    # 2. DRAWING NODES
    for i, n in enumerate(path):
        sx, sy = points[i]

        # Determining node color and size
        if i < target_index:
            # Visited nodes
            pygame.draw.circle(screen, CYAN_VISITED, (sx, sy), 6)
        elif i == target_index:
            # CURRENT TARGET (Blinking or large yellow)
            pygame.draw.circle(screen, YELLOW_TARGET, (sx, sy), 12) # Large circle
            pygame.draw.circle(screen, BLACK, (sx, sy), 13, 1)   # Outline
        else:
            # Future nodes
            pygame.draw.circle(screen, GREEN_FUTURE, (sx, sy), 5)

# --- MAIN ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Navigation: Follow the Yellow Dot!")
    clock = pygame.time.Clock()
    font_large = pygame.font.SysFont("Arial", 24, bold=True)
    font_small = pygame.font.SysFont("Arial", 16)

    # Loading
    try:
        orig = pygame.image.load(TRACK_IMAGE_PATH).convert()
        w, h = orig.get_size()
        factor = min(SCREEN_WIDTH/w, SCREEN_HEIGHT/h)
        map_image = pygame.transform.smoothscale(orig, (int(w*factor), int(h*factor)))
    except:
        w, h = 5000, 5000; factor = 0.16
        map_image = pygame.Surface((800, 800)); map_image.fill(WHITE)

    G, pos = load_graph_and_coordinates(GRAPH_FILE_PATH)

    # If no graph, create a dummy one
    if not pos:
        pos = {'n0': (100,100), 'n1': (500,500)}; G.add_edge('n0','n1')

    # Path initialization
    start_node = list(pos.keys())[0]
    goal_node = list(pos.keys())[-1]
    path = find_path(G, start_node, goal_node)

    # --- VARIABLES FOR TRACKING PROGRESS ---
    target_index = 1  # Start by targeting the second node in the list (index 1)
                      # (index 0 is start where we already are)
    next_node_id = path[target_index] if len(path) > 1 else str(start_node)

    # Car
    sx, sy = pos[start_node]
    auto = RobotCar(sx, sy)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

            # --- CLICK CHANGES GOAL AND RESETS PROGRESS ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                real_x, real_y = mx / factor, my / factor

                # Find node nearest to click (New GOAL)
                min_dist = float('inf'); new_goal = None
                for n, (nx, ny) in pos.items():
                    d = math.sqrt((nx-real_x)**2 + (ny-real_y)**2)
                    if d < min_dist: min_dist = d; new_goal = n

                # Find node nearest to car (New START)
                min_start_dist = float('inf'); new_start = None
                for n, (nx, ny) in pos.items():
                     d = math.sqrt((nx-auto.x)**2 + (ny-auto.y)**2)
                     if d < min_start_dist: min_start_dist = d; new_start = n

                if new_goal and new_start:
                    goal_node = new_goal
                    start_node = new_start
                    # Calculate new path
                    path = find_path(G, start_node, goal_node)
                    # RESET TARGET to the beginning of the new path
                    target_index = 1
                    if len(path) > 1:
                        next_node_id = path[target_index]
                    else:
                        next_node_id = "GOAL"

        # --- CHECKPOINT LOGIC (Navigation Core) ---
        if len(path) > 1 and target_index < len(path):
            # Get coordinates of current target
            target_id = path[target_index]
            mx, my = pos[target_id]

            # Calculate distance from car to target
            dist_to_target = math.sqrt((auto.x - mx)**2 + (auto.y - my)**2)

            # If close enough (< 60 pixels)
            if dist_to_target < VISIT_THRESHOLD:
                target_index += 1 # Switch to next
                if target_index < len(path):
                    next_node_id = path[target_index]
                else:
                    next_node_id = "ARRIVED!"

        # --- DRIVING ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]: auto.current_speed += 0.2
        elif keys[pygame.K_DOWN]: auto.current_speed -= 0.2
        else: auto.current_speed *= 0.96

        if keys[pygame.K_LEFT]: auto.current_steering_angle -= 0.05
        elif keys[pygame.K_RIGHT]: auto.current_steering_angle += 0.05
        else: auto.current_steering_angle *= 0.85

        auto.update_physics()
        auto.x = max(0, min(auto.x, w))
        auto.y = max(0, min(auto.y, h))

        # --- DRAWING ---
        screen.fill(BLACK)
        screen.blit(map_image, (0, 0))

        # Draw inactive edges (gray)
        for u, v in G.edges():
            if u in pos and v in pos:
                pygame.draw.line(screen, (80,80,80),
                                (int(pos[u][0]*factor), int(pos[u][1]*factor)),
                                (int(pos[v][0]*factor), int(pos[v][1]*factor)), 1)

        # Draw ADVANCED NAVIGATION (coloring visited and target)
        draw_advanced_navigation(screen, pos, factor, path, target_index)

        auto.draw(screen, factor)

        # --- INFO PANEL (Top Right) ---
        # Draw background for text
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - 310, 10, 300, 120))
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - 310, 10, 300, 120), 2) # Outline

        texts = [
            (f"NEXT TARGET: {next_node_id}", YELLOW_TARGET, font_large),
            (f"Progress: {target_index} / {len(path)} nodes", BLACK, font_small),
            (f"Speed: {auto.current_speed:.1f}", BLACK, font_small),
            ("Drive to the YELLOW dot!", BLACK, font_small)
        ]

        for i, (txt, color, font) in enumerate(texts):
            if color == YELLOW_TARGET: # Since yellow is light, write it with outline or darker
                render = font.render(txt, True, (200, 180, 0))
            else:
                render = font.render(txt, True, color)
            screen.blit(render, (SCREEN_WIDTH - 300, 20 + i*30))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()