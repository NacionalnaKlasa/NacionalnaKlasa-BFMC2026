import math
import pygame
import sys
import time
from localization import LocalizationModule
import threading
from tcpLib import PCServer

TRACK_IMAGE_PATH = r"C:\Users\Korisnik\Desktop\BOSCH\graph\staza_smanjena.png"
GRAPH_PATH = r"C:\Users\Korisnik\Desktop\BOSCH\graph\staza_graf.graphml"

def server_init(port):
    server = PCServer(port=65432)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    return server, server_thread
class BoschCar:
    def __init__(self, L=100.0, x=0.0, y=0.0):
        self.L = L       # Raspon osovina (Q) u cm
        self.x = x       # Pocetna X koordinata
        self.y = y       # Pocetna Y koordinata
        self.theta = 0.0 # Pocetni ugao auta u radijanima
        
    def update_position(self, v, delta_deg, dt):
        """
        v: brzina u cm/s
        delta_deg: ugao prednjih tockova u stepenima
        dt: vremenski korak u sekundama
        """
        # 1. Konvertovanje ugla volana u radijane
        delta_rad = math.radians(delta_deg)
        
        # 2. Izracunavanje ugaonog ubrzanja (promene ugla)
        omega = (v / self.L) * math.tan(delta_rad)
        
        # 3. Azuriranje pozicije i ugla (Eulerov metod)
        # Prvo azuriramo X i Y na osnovu TRENUTNOG ugla
        self.x += v * math.cos(self.theta) * dt
        self.y += v * math.sin(self.theta) * dt
        
        # Zatim azuriramo ugao za sledeci korak
        self.theta += omega * dt


x0 = 100.0
y0 = 100.0
auto = BoschCar(L=100.0, x=x0, y=y0)  # pocetni ugao auta je 0 stepeni (okrenut prema desno)
def run(auto, TRACK_IMAGE_PATH, GRAPH_PATH, TIMEOUT_THRESHOLD, server, server_thread):
    # ---INICIJALIZACIJA PYGAME---
    pygame.init()
    display = pygame.display.set_mode((800, 800))
    background = pygame.image.load(TRACK_IMAGE_PATH)
    X, Y = background.get_size()
    SCALE_X = 800.0 / X
    SCALE_Y = 800.0 / Y
    background = pygame.transform.scale(background, (800, 800))

    # Init navigation
    nav = LocalizationModule(GRAPH_PATH, visit_threshold=60.0)
    nodes = nav.get_all_nodes()
    edges = nav.G.edges()

    v = 0      # cm/s
    delta_deg = 0 # stepeni
    time_period = 5.0 # sekundi
            # simuliramo racunanje svakih 10 milisekundi

    # crtanje auta
    car_draw = pygame.Surface((20, 10), pygame.SRCALPHA)
    car_draw.fill((200, 0, 0))

    clock = pygame.time.Clock()
    font_obj = pygame.font.Font(None, 24)

    startTime = time.monotonic_ns()
    shouldEnd = 5e9

    # --- OSTAJEMO NA 60 FPS, ALI FIZIKU ZAKUCAVAMO NA 5ms ---
    physics_dt = 0.005 # fiksni korak za matematiku (5 ms)
    accumulator = 0.0  # sakuplja vreme izmedju frejmova


    target_steps = int(time_period / physics_dt) # koliko koraka matematike zelimo da simuliramo
    current_step = 0

    waitForClick = True
    carSet = False
    node_x, node_y = 0.0, 0.0
    car_start_x_cm, car_start_y_cm = 0.0, 0.0

    dt=0.0
    last_packet_time = time.time()
    TIMEOUT_THRESHOLD = 0.5  # Ako ništa ne stigne 0.5 sekundi, stani
    counter_rpi = 0
    running = True

    while running:
        # dt koristimo samo za glatkoću animacije ako RPi ne šalje DT
        frame_time = clock.tick(60) / 1000.0  
        
        # --- 3. MREŽNA KOMUNIKACIJA (TCP) ---
        # Proveravamo da li je stigao paket sa RPi-ja
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                server.closing()
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if waitForClick:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    # Pretvaranje piksela u CM za LocalizationModule
                    graph_x = mouse_x / SCALE_X
                    graph_y = mouse_y / SCALE_Y
                    
                    # Snap na najbliži čvor
                    nearest_node = nav._nearest_node(graph_x, graph_y)
                    node_x, node_y = nav.pos[nearest_node]
                    
                    # Inicijalizacija auta u CM
                    auto.x = node_x
                    auto.y = node_y
                    auto.theta = 0.0

                    car_start_x_cm = auto.x
                    car_start_y_cm = auto.y
                    
                    carSet = True
                    last_packet_time = time.time()
                    waitForClick = False
                    print(f"Auto postavljen na čvor: {nearest_node} ({node_x*SCALE_X:.2f}, {node_y*SCALE_Y:.2f}) px board")
        paketi = server.get_data()
        if carSet:    
            for msg in paketi:
                # RPi šalje npr: {"v": 25.0, "delta": 15.0, "dt": 0.05}
                if "v" in msg and "delta" in msg:
                    v = float(msg["v"])
                    delta_deg = float(msg["delta"])

                    current_time = time.time()
                    dt = current_time - last_packet_time
                    last_packet_time = current_time

                    counter_rpi += 1
                    if dt > 0.2:
                        dt = 0.05
                auto.update_position(v, delta_deg, dt)
        
        if time.time() - last_packet_time > TIMEOUT_THRESHOLD:
                v = 0.0
                #print("Nema signala sa RPi-ja, auto se zaustavlja.")
        

        # --- 5. CRTANJE (DISPLAY) ---
        display.blit(background, (0, 0))
        
        # Crtanje grafa (Ivice i Čvorovi)
        for u, m in edges:
            x1, y1 = nodes[u][0] * SCALE_X, nodes[u][1] * SCALE_Y
            x2, y2 = nodes[m][0] * SCALE_X, nodes[m][1] * SCALE_Y
            pygame.draw.line(display, (0, 0, 255), (x1, y1), (x2, y2), 1)
            
        for node_id, (nx, ny) in nodes.items():
            pygame.draw.circle(display, (255, 255, 0), (int(nx * SCALE_X), int(ny * SCALE_Y)), 3)

        # Crtanje auta (Pretvaranje CM u PX za rect)
        rotated_car = pygame.transform.rotate(car_draw, -math.degrees(auto.theta))
        rect = rotated_car.get_rect(center=(int(auto.x * SCALE_X), int(auto.y * SCALE_Y)))
        display.blit(rotated_car, rect)

        # HUD (Telemetrija)
        display.blit(font_obj.render(f"V: {v:.1f} cm/s", True, (255,255,255)), (10, 10))
        display.blit(font_obj.render(f"Ugao: {delta_deg:.1f}°", True, (255,255,255)), (10, 35))
        display.blit(font_obj.render(f"X: {auto.x:.1f} cm", True, (255,255,255)), (10, 60))
        display.blit(font_obj.render(f"Y: {auto.y:.1f} cm", True, (255,255,255)), (10, 85))

        pygame.display.flip()

    pygame.quit()
    print("\n\n")
    print(f"Pocetka pozicija (x0={car_start_x_cm:.2f}, y0={car_start_y_cm:.2f}) cm")
    print(f"Poslednje koordinate (x={auto.x:.2f}, y={auto.y:.2f}) cm")
    print(f"Primljeno ukupno {counter_rpi} paketa od Rpi-ja")
    sys.exit()
