import math
import pygame
import sys
import time
from localization import LocalizationModule

TRACK_IMAGE_PATH = r"C:\Users\Korisnik\Desktop\BOSCH\graph\staza_smanjena.png"
GRAPH_PATH = r"C:\Users\Korisnik\Desktop\BOSCH\graph\staza_graf.graphml"

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

# --- TESTIRANJE KODA ---
x0 = 100.0
y0 = 100.0
auto = BoschCar(L=100.0, x=x0, y=y0)  # pocetni ugao auta je 0 stepeni (okrenut prema desno)

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

v = 25.0       # cm/s
delta_deg = 15 # stepeni
time_period = 5.0 # sekundi
dt = 0.01           # simuliramo racunanje svakih 10 milisekundi

# crtanje auta
car_draw = pygame.Surface((20, 10), pygame.SRCALPHA)
car_draw.fill((200, 0, 0))

clock = pygame.time.Clock()

running = True

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

while running:
    frame_time = clock.tick(60) / 1000.0  # 60 fps = 16.67ms osvezavanje ekrana, a mi matematiku racunamo na svakih 5ms, znaci 3x racunamo poziciju auta pre nego sto osvezim ekran
    
    #if time.monotonic_ns() - startTime > shouldEnd: #realno vrijeme ne vrijeme simulacije
    #    break # moze prekinuti simulaciju iako nije izvrseno 1000 * 5ms 
    accumulator += frame_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #lijevi klik
            if waitForClick:    
                mouse_x, mouse_y = pygame.mouse.get_pos()
                graph_x = mouse_x / SCALE_X
                graph_y = mouse_y / SCALE_Y

                nearest_node = nav._nearest_node(graph_x, graph_y)
                node_x, node_y = nav.pos[nearest_node]

                auto.x = node_x  # postavljamo auto na koordinate najblizeg cvora
                auto.y = node_y
                car_start_x_cm = auto.x  # za matematiku koristim cm
                car_start_y_cm = auto.y

                auto.theta = 0.0 #resetujemo ugao auta na 0 stepeni
                print(f"\nKorisnik auto postavio na {node_x*SCALE_X:.2f}, {node_y*SCALE_Y:.2f} (pixel koord)")

                accumulator = 0.0 # ne zelimo da akumuliramo vreme koje smo cekali klik
                current_step = 0
                waitForClick = False
                carSet = True


    if carSet: #matematika krece tek kad se postavi pocetna pozicija
        while accumulator >= physics_dt:
            auto.update_position(v, delta_deg, physics_dt)
            accumulator -= physics_dt

            current_step += 1

            if current_step >= target_steps:
                running = False
                break

    display.blit(background, (0, 0))
    for u,m in edges:
        if u in nodes and m in nodes:
            x1 = nodes[u][0] * SCALE_X
            y1 = nodes[u][1] * SCALE_Y  
            x2 = nodes[m][0] * SCALE_X
            y2 = nodes[m][1] * SCALE_Y
            pygame.draw.line(display, (0, 0, 255), (x1, y1), (x2, y2), 1) #crtanje ivica grafa
    for node_id, (x, y) in nav.pos.items():
        pygame.draw.circle(display, (255, 255, 0), (int(x*SCALE_X), int(y*SCALE_Y)), 3) #crtanje cvorova grafa
    
    rotated_car = pygame.transform.rotate(car_draw, math.degrees(auto.theta))
    rect = rotated_car.get_rect(center=(int(auto.x*SCALE_X), int(auto.y*SCALE_Y))) #crtanje u px
    display.blit(rotated_car, rect.topleft)

    font = pygame.font.SysFont(None, 24)
    tekst_brzina = font.render(f"Brzina (v): {v:.1f} cm/s", True, (255, 255, 255))
    tekst_ugao = font.render(f"Ugao tockova: {delta_deg:.1f} stepeni", True, (255, 255, 255))
    tekst_orijentacija = font.render(f"Ugao auta (theta): {math.degrees(auto.theta):.1f} stepeni", True, (255, 255, 255))
    
    display.blit(tekst_brzina, (10, 10))
    display.blit(tekst_ugao, (10, 35))
    display.blit(tekst_orijentacija, (10, 60))

    pygame.display.flip()

pygame.quit()
print("\n")
print(f"Pocetka pozicija (x0={car_start_x_cm:.2f}, y0={car_start_y_cm:.2f}) cm")
print(f"Brzina kretanje: {v:.1f} cm/s")
print(f"Ugao tockova: {delta_deg:.1f} stepeni")
print(f"Nakon {time_period} s:")
print(f"X: {auto.x:.2f} cm")
print(f"Y: {auto.y:.2f} cm")
sys.exit()
