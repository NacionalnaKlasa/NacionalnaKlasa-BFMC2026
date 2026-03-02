import pygame
import math
import networkx as nx
import re
import json
import paho.mqtt.client as mqtt
import threading

# --- PODEŠAVANJA ---
SLIKA_STAZE = "C:\\Users\\Korisnik\\Desktop\\BOSCH\\CODE\\Floyd\\LOCAL\\staza_smanjena.png"        
GRAF_FAJL = "C:\\Users\\Korisnik\\Desktop\\BOSCH\\CODE\\Floyd\\LOCAL\\staza_graf.graphml"   
SIRINA_EKRANA = 1000
VISINA_EKRANA = 800
FPS = 60

# MQTT PODEŠAVANJA
BROKER = "test.mosquitto.org"
TOPIC = "robot/telemetry"

# Globalne promenljive za podatke sa robota (da bi threadovi mogli da ih dele)
live_data = {
    "brzina": 0.0,
    "ugao": 0.0,
    "connected": False
}

# --- MQTT FUNKCIJE ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Dashboard povezan na Broker!")
        client.subscribe(TOPIC)
        live_data["connected"] = True

def on_message(client, userdata, msg):
    try:
        # Dekodiramo poruku
        tekst = msg.payload.decode()
        podaci = json.loads(tekst)
        
        # Ažuriramo globalne promenljive
        live_data["brzina"] = float(podaci.get("brzina", 0))
        live_data["ugao"] = float(podaci.get("ugao", 0))
        # print(f"📩 Primljeno: {podaci}") # Otkomentarišite za debug
    except Exception as e:
        print(f"Greška pri parsiranju: {e}")

def pokreni_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)
    client.loop_forever()

# --- PYGAME KLASE (Iste kao pre) ---
class RobotPrikaz:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ugao = 0.0 

    def azuriraj_na_osnovu_telemetrije(self, brzina, ugao_volana):
        # Ovde simulacija samo PRATI podatke, ne stvara ih
        self.x += brzina * math.cos(self.ugao)
        self.y += brzina * math.sin(self.ugao)
        
        if ugao_volana != 0 and brzina != 0:
            self.ugao += (brzina / 40.0) * math.tan(ugao_volana)

    def crtaj(self, ekran, faktor):
        ex, ey = int(self.x * faktor), int(self.y * faktor)
        pygame.draw.circle(ekran, (255, 140, 0), (ex, ey), int(12 * faktor))
        duzina = 30 * faktor
        dx = ex + duzina * math.cos(self.ugao)
        dy = ey + duzina * math.sin(self.ugao)
        pygame.draw.line(ekran, (0, 0, 255), (ex, ey), (dx, dy), 3)

# ... (Funkcije za učitavanje grafa ostaju iste, skratio sam ih radi preglednosti) ...
def ucitaj_graf_i_koordinate(putanja):
    try: return nx.read_graphml(putanja), {} # Ovde ubacite vašu punu funkciju od ranije!
    except: return nx.Graph(), {} 
# (Napomena: Iskoristite onu 'robusnu' funkciju iz prethodnog odgovora)

# --- MAIN ---
def main():
    pygame.init()
    ekran = pygame.display.set_mode((SIRINA_EKRANA, VISINA_EKRANA))
    pygame.display.set_caption("ROBOT DASHBOARD - Live Telemetry")
    sat = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20)

    # Pokretanje MQTT-a u posebnom threadu (da ne blokira grafiku)
    mqtt_thread = threading.Thread(target=pokreni_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    # Učitavanje slike (Koristite vaš kod za učitavanje i skaliranje)
    try:
        orig = pygame.image.load(SLIKA_STAZE).convert()
        w, h = orig.get_size()
        faktor = min(SIRINA_EKRANA/w, VISINA_EKRANA/h)
        mapa = pygame.transform.smoothscale(orig, (int(w*faktor), int(h*faktor)))
    except:
        w, h = 5000, 5000; faktor = 0.16
        mapa = pygame.Surface((800, 800)); mapa.fill((255,255,255))

    # Auto počinje na sredini (ili na startnoj poziciji iz grafa)
    robot = RobotPrikaz(w//2, h//2)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        # --- GLAVNI DEO: AŽURIRANJE SA MREŽE ---
        # Uzimamo podatke koji su stigli preko Wi-Fi
        trenutna_brzina = live_data["brzina"]
        trenutni_ugao = live_data["ugao"]
        
        # Pomeramo vizuelni prikaz robota
        robot.azuriraj_na_osnovu_telemetrije(trenutna_brzina, trenutni_ugao)
        
        # Ograničenje da ne pobegne sa ekrana
        robot.x = max(0, min(robot.x, w))
        robot.y = max(0, min(robot.y, h))

        # --- CRTANJE ---
        ekran.fill((0, 0, 0))
        ekran.blit(mapa, (0, 0))
        
        # Crtamo robota
        robot.crtaj(ekran, faktor)

        # Status Panel
        status_boja = (0, 255, 0) if live_data["connected"] else (255, 0, 0)
        status_txt = "ONLINE" if live_data["connected"] else "OFFLINE"
        
        info = [
            f"STATUS: {status_txt}",
            f"Brzina: {trenutna_brzina:.2f}",
            f"Ugao: {math.degrees(trenutni_ugao):.2f}°",
            f"Pozicija: X={int(robot.x)} Y={int(robot.y)}"
        ]
        
        pygame.draw.rect(ekran, (255,255,255), (10, 10, 250, 120))
        pygame.draw.circle(ekran, status_boja, (240, 30), 8) # Lampica statusa

        for i, txt in enumerate(info):
            t = font.render(txt, True, (0,0,0))
            ekran.blit(t, (15, 20 + i*25))

        pygame.display.flip()
        sat.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()