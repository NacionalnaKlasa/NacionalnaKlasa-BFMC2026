import pygame
import math
import networkx as nx
import re

# --- PODEŠAVANJA ---
SLIKA_STAZE = "/home/konstantin/Desktop/lokalizacija/LOCAL/staza_smanjena.png"         
GRAF_FAJL = "/home/konstantin/Desktop/lokalizacija/LOCAL/staza_graf.graphml"  
SIRINA_EKRANA = 900
VISINA_EKRANA = 900
FPS = 60

# Boje
BELA = (255, 255, 255)
CRVENA = (255, 0, 0)     # Auto
PLAVA = (0, 0, 255)      # Smer auta
SIVA = (100, 100, 100)   # Grane grafa
ZUTA = (255, 255, 0)     # TRENUTNI (najbliži) čvor
CRNA = (0, 0, 0)

class RobotAuto:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ugao = 0.0
        self.brzina = 0.0
        self.ugao_volana = 0.0

    def azuriraj(self):
        # Kinematika (kretanje)
        self.x += self.brzina * math.cos(self.ugao)
        self.y += self.brzina * math.sin(self.ugao)
        if self.ugao_volana != 0:
            self.ugao += (self.brzina / 40) * math.tan(self.ugao_volana)

    def crtaj(self, ekran, faktor):
        ex = int(self.x * faktor)
        ey = int(self.y * faktor)
        pygame.draw.circle(ekran, CRVENA, (ex, ey), int(15 * faktor))
        # Linija smera
        dx = ex + 30 * faktor * math.cos(self.ugao)
        dy = ey + 30 * faktor * math.sin(self.ugao)
        pygame.draw.line(ekran, PLAVA, (ex, ey), (dx, dy), 2)

# --- FUNKCIJE ZA GRAF ---

def ucitaj_graf(putanja):
    print(f"--- POKUŠAVAM DA UČITAM: {putanja} ---")
    try:
        G = nx.read_graphml(putanja)
    except Exception as e:
        print(f"❌ GREŠKA: Ne mogu da otvorim fajl! {e}")
        return nx.Graph(), {}

    pos = {}
    broj_nula = 0
    
    for node, data in G.nodes(data=True):
        x, y = None, None
        
        # 1. Prva provera: Da li networkx već vidi 'x' i 'y'?
        if 'x' in data and 'y' in data:
            x, y = float(data['x']), float(data['y'])
        
        # 2. Druga provera: Tražimo unutar svih yEd podataka
        else:
            for kljuc, vrednost in data.items():
                tekst_vrednost = str(vrednost)
                # Tražimo bilo šta što liči na x="broj" ili x='broj'
                if 'x=' in tekst_vrednost and 'y=' in tekst_vrednost:
                    # Regex koji hvata i 123 i 123.45, sa navodnicima ili apostrofima
                    mx = re.search(r'x=["\']?([\d\.]+)["\']?', tekst_vrednost)
                    my = re.search(r'y=["\']?([\d\.]+)["\']?', tekst_vrednost)
                    
                    if mx and my:
                        x = float(mx.group(1))
                        y = float(my.group(1))
                        break # Našli smo koordinate, idemo na sledeći čvor
        
        # Ako smo našli koordinate, upisujemo ih
        if x is not None and y is not None:
            pos[node] = (x, y)
        else:
            # Ako nismo našli, stavljamo 0,0 ali brojimo greške
            pos[node] = (0, 0)
            broj_nula += 1

    # --- DIJAGNOSTIKA ---
    print(f"Ukupno čvorova u fajlu: {len(G.nodes)}")
    print(f"Uspešno učitane koordinate: {len(pos) - broj_nula}")
    print(f"Čvorovi sa greškom (0,0): {broj_nula}")
    
    if len(pos) > 0:
        # Ispisujemo prva 3 čvora da proverimo brojeve
        primeri = list(pos.items())[:3]
        print(f"Primer koordinata: {primeri}")
        
    return G, pos

def nadji_najblizi_cvor(auto_x, auto_y, pozicije_cvorova):
    """ Pronalazi čvor koji je fizički najbliži autu """
    najmanja_distanca = float('inf')
    najblizi_id = None

    for node_id, (nx, ny) in pozicije_cvorova.items():
        # Euklidska distanca: sqrt((x2-x1)^2 + (y2-y1)^2)
        dist = math.sqrt((nx - auto_x)**2 + (ny - auto_y)**2)
        
        if dist < najmanja_distanca:
            najmanja_distanca = dist
            najblizi_id = node_id
            
    return najblizi_id, najmanja_distanca

def crtaj_graf_na_ekranu(ekran, G, pos, faktor, aktivni_cvor):
    """ Crta linije i tačke grafa """
    # 1. Crtanje Grana (Linija)
    for u, v in G.edges():
        if u in pos and v in pos:
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            # Skaliramo koordinate
            pygame.draw.line(ekran, SIVA, 
                             (int(x1*faktor), int(y1*faktor)), 
                             (int(x2*faktor), int(y2*faktor)), 1)

    # 2. Crtanje Čvorova (Tačaka)
    for node, (x, y) in pos.items():
        sx = int(x * faktor)
        sy = int(y * faktor)
        
        if node == aktivni_cvor:
            # Aktivni čvor crtamo velik i ŽUT
            pygame.draw.circle(ekran, ZUTA, (sx, sy), int(10 * faktor))
        else:
            # Ostale čvorove crtamo male i SIVE
            pygame.draw.circle(ekran, CRNA, (sx, sy), int(5 * faktor))

# --- GLAVNI PROGRAM ---

def main():
    pygame.init()
    ekran = pygame.display.set_mode((SIRINA_EKRANA, VISINA_EKRANA))
    pygame.display.set_caption("Simulacija + GraphML Praćenje")
    sat = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)

    # 1. Učitavanje slike i računanje skaliranja
    try:
        orig_mapa = pygame.image.load(SLIKA_STAZE).convert()
        w, h = orig_mapa.get_size()
        faktor = min(SIRINA_EKRANA / w, VISINA_EKRANA / h)
        nova_w, nova_h = int(w * faktor), int(h * faktor)
        skalirana_mapa = pygame.transform.smoothscale(orig_mapa, (nova_w, nova_h))
    except:
        print("Nema slike. Pravim praznu.")
        w, h = 5000, 5000
        faktor = 0.16
        skalirana_mapa = pygame.Surface((800, 800))
        skalirana_mapa.fill(BELA)

    # 2. Učitavanje GRAFA
    G, pozicije_cvorova = ucitaj_graf(GRAF_FAJL)

    # 3. Auto
    auto = RobotAuto(x=w//2, y=h//2) # Počinje na sredini

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        # --- ULAZ (Simulacija vožnje tastaturom) ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]: auto.brzina += 0.2
        elif keys[pygame.K_DOWN]: auto.brzina -= 0.2
        else: auto.brzina *= 0.98

        if keys[pygame.K_LEFT]: auto.ugao_volana -= 0.05
        elif keys[pygame.K_RIGHT]: auto.ugao_volana += 0.05
        else: auto.ugao_volana *= 0.9

        # --- AŽURIRANJE ---
        auto.azuriraj()
        
        # Ograničenje na mapi
        auto.x = max(0, min(auto.x, w))
        auto.y = max(0, min(auto.y, h))

        # --- LOGIKA GRAFA: Gde sam sada? ---
        najblizi_id, distanca = nadji_najblizi_cvor(auto.x, auto.y, pozicije_cvorova)

        # --- CRTANJE ---
        ekran.fill(CRNA)
        
        # 1. Mapa
        ekran.blit(skalirana_mapa, (0, 0))
        
        # 2. Graf (Crtamo ga PREKO mape, a ISPOD auta)
        crtaj_graf_na_ekranu(ekran, G, pozicije_cvorova, faktor, najblizi_id)
        
        # 3. Auto
        auto.crtaj(ekran, faktor)

        # 4. Info panel
        info_txt = [
            f"Brzina: {auto.brzina:.1f}",
            f"Najbliži čvor: {najblizi_id}",
            f"Udaljenost od čvora: {distanca:.1f} px"
        ]
        for i, txt in enumerate(info_txt):
            img = font.render(txt, True, CRNA)
            pygame.draw.rect(ekran, BELA, (10, 10 + i*20, 200, 20))
            ekran.blit(img, (15, 12 + i*20))

        pygame.display.flip()
        sat.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()