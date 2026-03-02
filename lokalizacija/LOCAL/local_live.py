import pygame
import math
import random # Koristimo samo za testiranje (glumimo podatke)

# --- PODEŠAVANJA ---
PUTANJA_DO_SLIKE = "C:\\Users\\Korisnik\\Desktop\\BOSCH\\CODE\\Floyd\\LOCAL\\staza_smanjena.png"  
SIRINA_EKRANA = 800
VISINA_EKRANA = 800
FPS = 60

# Fizičke konstante (Moraju biti iste kao u prethodnom kodu)
DUZINA_AUTA = 40         
BELA = (255, 255, 255)
CRVENA = (255, 0, 0)
PLAVA = (0, 0, 255)
CRNA = (0, 0, 0)
ZELENA = (0, 255, 0)

class RobotAuto:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ugao = 0.0           
        
        # Ovi podaci sada dolaze SPOLJA (sa pravog auta)
        self.trenutna_brzina = 0.0         
        self.trenutni_ugao_volana = 0.0    

    def primi_podatke(self, brzina, ugao_tockova):
        """
        Ova funkcija prima sirove podatke sa senzora pravog auta.
        brzina: float (pikseli po frejmu ili m/s skalirano)
        ugao_tockova: float (radijani, npr. -0.5 do 0.5)
        """
        self.trenutna_brzina = brzina
        self.trenutni_ugao_volana = ugao_tockova

    def azuriraj_poziciju(self):
        """
        Računa novu X, Y poziciju na osnovu primljene brzine i ugla.
        Ovo je 'Dead Reckoning' - procena pozicije.
        """
        # 1. Pomeranje
        self.x += self.trenutna_brzina * math.cos(self.ugao)
        self.y += self.trenutna_brzina * math.sin(self.ugao)

        # 2. Rotacija (samo ako se točkovi okreću)
        if self.trenutni_ugao_volana != 0:
            ugaona_brzina = (self.trenutna_brzina / DUZINA_AUTA) * math.tan(self.trenutni_ugao_volana)
            self.ugao += ugaona_brzina

    def crtaj(self, ekran, faktor_skaliranja):
        # Ista logika crtanja kao i pre
        ekran_x = int(self.x * faktor_skaliranja)
        ekran_y = int(self.y * faktor_skaliranja)
        radijus = int(15 * faktor_skaliranja)
        if radijus < 3: radijus = 3

        pygame.draw.circle(ekran, CRVENA, (ekran_x, ekran_y), radijus)
        
        # Smer auta
        duzina = 40 * faktor_skaliranja
        kraj_x = ekran_x + duzina * math.cos(self.ugao)
        kraj_y = ekran_y + duzina * math.sin(self.ugao)
        pygame.draw.line(ekran, PLAVA, (ekran_x, ekran_y), (kraj_x, kraj_y), 2)

# --- DEO ZA KOMUNIKACIJU SA ROBOTOM ---

def simuliraj_dolazak_podataka(brojac_vremena):
    """
    glumi da robot šalje podatke. 
    Kada povezete pravi robot, ovu funkciju ćete obrisati i koristiti Serial ili WiFi.
    """
    # Pravimo lažnu "vožnju" u krug
    # Svakih 100 frejmova promeni ponašanje
    if (brojac_vremena // 100) % 2 == 0:
        brzina = 2.0  # Auto ide napred
        ugao = 0.1    # Blago skreće desno
    else:
        brzina = 1.5
        ugao = -0.1   # Blago skreće levo
        
    return brzina, ugao

# --------------------------------------

def main():
    pygame.init()
    ekran = pygame.display.set_mode((SIRINA_EKRANA, VISINA_EKRANA))
    pygame.display.set_caption("Live Tracking - Podaci sa Robota")
    sat = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)

    # Učitavanje mape (isto kao pre)
    try:
        orig_mapa = pygame.image.load(PUTANJA_DO_SLIKE).convert()
        w, h = orig_mapa.get_size()
        faktor = min(SIRINA_EKRANA / w, VISINA_EKRANA / h)
        skalirana_mapa = pygame.transform.smoothscale(orig_mapa, (int(w * faktor), int(h * faktor)))
    except FileNotFoundError:
        print("Nema slike! Koristim crnu pozadinu.")
        w, h = 5000, 5000
        faktor = 0.16
        skalirana_mapa = pygame.Surface((800, 800))
        skalirana_mapa.fill(CRNA)

    # Auto počinje na sredini
    auto = RobotAuto(x=w//2, y=h//2)
    
    brojac = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- KORAK 1: PRIJEM PODATAKA ---
        # Ovde pozivamo funkciju koja dobavlja podatke.
        # Kasnije ćete ovde čitati sa Serial porta.
        
        dobijena_brzina, dobijen_ugao = simuliraj_dolazak_podataka(brojac)
        
        # Prosleđujemo podatke autu
        auto.primi_podatke(dobijena_brzina, dobijen_ugao)

        # --- KORAK 2: AŽURIRANJE ---
        auto.azuriraj_poziciju()

        # Ograničenje da ne ode sa mape
        auto.x = max(0, min(auto.x, w))
        auto.y = max(0, min(auto.y, h))

        # --- KORAK 3: CRTANJE ---
        ekran.fill(CRNA)
        ekran.blit(skalirana_mapa, (0, 0))
        auto.crtaj(ekran, faktor)

        # Ispis primljenih podataka
        info = f"RX Brzina: {auto.trenutna_brzina:.2f} | RX Ugao: {math.degrees(auto.trenutni_ugao_volana):.1f}°"
        tekst = font.render(info, True, CRNA)
        pygame.draw.rect(ekran, BELA, (10, 10, 300, 30))
        ekran.blit(tekst, (15, 15))

        pygame.display.flip()
        sat.tick(FPS)
        brojac += 1

    pygame.quit()

if __name__ == "__main__":
    main()