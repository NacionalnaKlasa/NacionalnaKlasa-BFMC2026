import pygame
import math
import networkx as nx
import re
import random 

# --- PODEŠAVANJA ---
SLIKA_STAZE = "C:\\Users\\Korisnik\\Desktop\\BOSCH\\CODE\\Floyd\\LOCAL\\staza_smanjena.png"        
GRAF_FAJL = "C:\\Users\\Korisnik\\Desktop\\BOSCH\\CODE\\Floyd\\LOCAL\\staza_graf.graphml" 
SIRINA_EKRANA = 900
VISINA_EKRANA = 900
FPS = 60

# Boje
BELA = (255, 255, 255)
CRVENA = (255, 0, 0)     
PLAVA = (0, 0, 255)      
SIVA = (100, 100, 100)   
ZUTA = (255, 255, 0)     # Aktivni čvor
CRNA = (0, 0, 0)
ZELENA = (0, 255, 0)

# --- KLASA AUTO ---
class RobotAuto:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ugao = 0.0          # Gde auto gleda (heading)
        
        # Podaci koji "stižu" sa senzora
        self.trenutna_brzina = 0.0
        self.trenutni_ugao_volana = 0.0

    def primi_podatke(self, brzina, ugao_tockova):
        """ Ovde simuliramo prijem podataka sa Serial/WiFi """
        self.trenutna_brzina = brzina
        self.trenutni_ugao_volana = ugao_tockova

    def azuriraj_fiziku(self):
        """ Dead Reckoning: Računamo gde je auto na osnovu brzine i volana """
        # Kinematski model
        self.x += self.trenutna_brzina * math.cos(self.ugao)
        self.y += self.trenutna_brzina * math.sin(self.ugao)
        
        # Ako je volan okrenut, auto rotira
        # (Delimo sa 40 jer je to fiktivna dužina osovine u pikselima)
        if self.trenutni_ugao_volana != 0:
            self.ugao += (self.trenutna_brzina / 40.0) * math.tan(self.trenutni_ugao_volana)

    def crtaj(self, ekran, faktor):
        ex = int(self.x * faktor)
        ey = int(self.y * faktor)
        
        # Telo auta
        pygame.draw.circle(ekran, CRVENA, (ex, ey), int(15 * faktor))
        
        # Smer kretanja (Plava linija)
        duzina = 30 * faktor
        dx = ex + duzina * math.cos(self.ugao)
        dy = ey + duzina * math.sin(self.ugao)
        pygame.draw.line(ekran, PLAVA, (ex, ey), (dx, dy), 2)

        # Smer točkova (Zelena linija - da vidimo gde skreće)
        ugao_tockova = self.ugao + self.trenutni_ugao_volana
        tx = ex + duzina * math.cos(ugao_tockova)
        ty = ey + duzina * math.sin(ugao_tockova)
        pygame.draw.line(ekran, ZELENA, (ex, ey), (tx, ty), 2)

# --- FUNKCIJA ZA SIMULIRANJE PODATAKA ---
def simuliraj_dolazak_podataka(brojac_vremena):
    """
    Ova funkcija glumi vašeg robota.
    Vraća (brzina, ugao_volana).
    """
    # Mala logika da auto vozi u krug/osmicu
    ciklus = brojac_vremena % 1000
    
    brzina = 3.0 # Konstantna brzina
    
    # Menjamo volan tokom vremena da napravimo putanju
    if ciklus < 200:
        ugao = 0.0       # Vozi pravo
    elif ciklus < 500:
        ugao = 0.3       # Skreći desno
    elif ciklus < 700:
        ugao = 0.0       # Pravo
    else:
        ugao = -0.3      # Skreći levo
        
    return brzina, ugao

# --- UČITAVANJE GRAFA (NAPREDNA VERZIJA) ---
def ucitaj_graf_robusno(putanja):
    print(f"--- UČITAVANJE GRAFA: {putanja} ---")
    try:
        G = nx.read_graphml(putanja)
    except Exception as e:
        print(f"GRESKA: {e}")
        return nx.Graph(), {}

    pos = {}
    for node, data in G.nodes(data=True):
        x, y = None, None
        
        # Metod 1: Direktno
        if 'x' in data and 'y' in data:
            x, y = float(data['x']), float(data['y'])
        # Metod 2: Traženje u tekstu
        else:
            for k, v in data.items():
                s = str(v)
                if 'x=' in s and 'y=' in s:
                    mx = re.search(r'x=["\']?([\d\.]+)["\']?', s)
                    my = re.search(r'y=["\']?([\d\.]+)["\']?', s)
                    if mx and my:
                        x, y = float(mx.group(1)), float(my.group(1))
                        break
        
        if x is not None: pos[node] = (x, y)
        else: pos[node] = (0, 0) # Fallback

    print(f"Učitano koordinata: {len(pos)}")
    return G, pos

def nadji_najblizi(ax, ay, pos):
    min_dist = float('inf')
    naj_id = None
    for nid, (nx, ny) in pos.items():
        # Ako je čvor (0,0) preskoči ga jer je verovatno greška
        if nx == 0 and ny == 0: continue
        
        d = math.sqrt((nx-ax)**2 + (ny-ay)**2)
        if d < min_dist:
            min_dist = d
            naj_id = nid
    return naj_id, min_dist

def crtaj_graf(ekran, G, pos, faktor, aktivni):
    # Grane
    for u, v in G.edges():
        if u in pos and v in pos:
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            if x1==0 or x2==0: continue
            pygame.draw.line(ekran, SIVA, (int(x1*faktor), int(y1*faktor)), (int(x2*faktor), int(y2*faktor)), 1)
    
    # Čvorovi
    for n, (x, y) in pos.items():
        if x==0 and y==0: continue
        sx, sy = int(x*faktor), int(y*faktor)
        
        if n == aktivni:
            pygame.draw.circle(ekran, ZUTA, (sx, sy), int(12*faktor)) # Aktivni
        else:
            pygame.draw.circle(ekran, CRNA, (sx, sy), int(5*faktor))  # Obični

# --- MAIN ---
def main():
    pygame.init()
    ekran = pygame.display.set_mode((SIRINA_EKRANA, VISINA_EKRANA))
    pygame.display.set_caption("FULL SIMULACIJA: Auto + Graf + Podaci")
    sat = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)

    # 1. Slika
    try:
        orig = pygame.image.load(SLIKA_STAZE).convert()
        w, h = orig.get_size()
        faktor = min(SIRINA_EKRANA/w, VISINA_EKRANA/h)
        nova_w, nova_h = int(w*faktor), int(h*faktor)
        mapa = pygame.transform.smoothscale(orig, (nova_w, nova_h))
    except:
        print("Nema slike, koristim crnu pozadinu.")
        w, h = 5000, 5000
        faktor = 0.16
        mapa = pygame.Surface((800, 800))
        mapa.fill(BELA)

    # 2. Graf
    G, pos = ucitaj_graf_robusno(GRAF_FAJL)

    # 3. Auto (start na sredini)
    auto = RobotAuto(w//2, h//2)

    brojac = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        # --- KORAK A: SIMULACIJA PODATAKA ---
        # Ovde dobijamo podatke (kao da robot šalje)
        nova_brzina, novi_ugao = simuliraj_dolazak_podataka(brojac)
        
        # Šaljemo podatke autu
        auto.primi_podatke(nova_brzina, novi_ugao)

        # --- KORAK B: AŽURIRANJE FIZIKE ---
        auto.azuriraj_fiziku()
        
        # Ograničenje da ne ode sa mape
        auto.x = max(0, min(auto.x, w))
        auto.y = max(0, min(auto.y, h))

        # --- KORAK C: NAVIGACIJA (GRAF) ---
        naj_cvor, dist = nadji_najblizi(auto.x, auto.y, pos)

        # --- KORAK D: CRTANJE ---
        ekran.fill(CRNA)
        ekran.blit(mapa, (0, 0))                 # 1. Mapa
        crtaj_graf(ekran, G, pos, faktor, naj_cvor) # 2. Graf (Crtamo ga PREKO mape)
        auto.crtaj(ekran, faktor)                # 3. Auto (Crtamo PREKO grafa)

        # Ispis podataka
        tekstovi = [
            f"SIMULACIJA PODATAKA (AUTO-PILOT)",
            f"Ulaz Brzina: {auto.trenutna_brzina:.2f}",
            f"Ulaz Volan: {math.degrees(auto.trenutni_ugao_volana):.1f}°",
            f"--- NAVIGACIJA ---",
            f"Najbliži čvor: {naj_cvor}",
            f"Distanca: {dist:.1f} px"
        ]
        
        for i, t in enumerate(tekstovi):
            slika_t = font.render(t, True, CRNA)
            pygame.draw.rect(ekran, BELA, (10, 10 + i*22, 280, 20))
            ekran.blit(slika_t, (15, 12 + i*22))

        pygame.display.flip()
        sat.tick(FPS)
        brojac += 1

    pygame.quit()

if __name__ == "__main__":
    main()