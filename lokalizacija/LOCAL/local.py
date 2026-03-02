import pygame
import math

# --- PODEŠAVANJA ---
# Zamenite ovo sa tačnim imenom vašeg fajla
PUTANJA_DO_SLIKE = "C:\\Users\\Korisnik\\Desktop\\BOSCH\\CODE\\Floyd\\LOCAL\\staza_smanjena.png" 

# Veličina prozora simulacije (npr. 800x800 da bude kvadratno)
SIRINA_EKRANA = 800
VISINA_EKRANA = 800
FPS = 60

# Fizičke konstante auta (u pikselima originalne mape)
DUZINA_AUTA = 400         # Razmak između prednje i zadnje osovine
MAX_UGAO_VOLANA = math.radians(30) # Maksimalno skretanje (30 stepeni)
UBRZANJE = 0.2
TRENJE = 0.98            # Otpor vazduha/trenje (usporava auto)

# Boje (R, G, B)
BELA = (255, 255, 255)
CRVENA = (255, 0, 0)
PLAVA = (0, 0, 255)
CRNA = (0, 0, 0)
ZELENA = (0, 255, 0)

class RobotAuto:
    def __init__(self, x, y):
        # Pozicija i stanje fizike (koristi REALNE koordinate mape)
        self.x = x
        self.y = y
        self.ugao = 0.0           # Ugao kretanja auta (radijani)
        self.brzina = 0.0         # Brzina u pikselima po frejmu
        self.ugao_volana = 0.0    # Trenutni ugao prednjih točkova

    def azuriraj_fiziku(self):
        """
        Implementira Kinematski model bicikla.
        Ažurira poziciju na osnovu brzine i ugla volana.
        """
        # 1. Pomeranje auta u smeru u kom trenutno gleda
        # Dodajemo komponente brzine na X i Y
        self.x += self.brzina * math.cos(self.ugao)
        self.y += self.brzina * math.sin(self.ugao)

        # 2. Rotacija auta ako je volan zakrenut
        # Formula: ugaona_brzina = (brzina / duzina_auta) * tan(ugao_volana)
        if self.ugao_volana != 0:
            ugaona_brzina = (self.brzina / DUZINA_AUTA) * math.tan(self.ugao_volana)
            self.ugao += ugaona_brzina

    def crtaj(self, ekran, faktor_skaliranja):
        """
        Crta auto na ekranu, preračunavajući njegove realne koordinate
        u koordinate ekrana koristeći faktor skaliranja.
        """
        # Preračunavamo poziciju za ekran
        ekran_x = int(self.x * faktor_skaliranja)
        ekran_y = int(self.y * faktor_skaliranja)
        
        # Veličina auta na ekranu (skalirana)
        radijus_auta = int(15 * faktor_skaliranja)
        # Obezbeđujemo da se auto uvek vidi, čak i kad je mapa jako umanjena
        if radijus_auta < 3: radijus_auta = 3

        # Crtamo telo auta (Crveni krug)
        pygame.draw.circle(ekran, CRVENA, (ekran_x, ekran_y), radijus_auta)

        # Dužine linija za smer takođe skaliramo
        duzina_linije = 40 * faktor_skaliranja

        # Crtamo liniju smera kretanja (Plava linija - gde auto gleda)
        kraj_x = ekran_x + duzina_linije * math.cos(self.ugao)
        kraj_y = ekran_y + duzina_linije * math.sin(self.ugao)
        pygame.draw.line(ekran, PLAVA, (ekran_x, ekran_y), (kraj_x, kraj_y), 2)

        # Crtamo smer točkova (Zelena linija - gde je volan okrenut)
        # Ovo pomaže da se vizuelno vidi unos skretanja
        ugao_tocka = self.ugao + self.ugao_volana
        tockak_x = ekran_x + duzina_linije * math.cos(ugao_tocka)
        tockak_y = ekran_y + duzina_linije * math.sin(ugao_tocka)
        pygame.draw.line(ekran, ZELENA, (ekran_x, ekran_y), (tockak_x, tockak_y), 2)

def main():
    pygame.init()
    
    # Podešavanje prozora
    ekran = pygame.display.set_mode((SIRINA_EKRANA, VISINA_EKRANA))
    pygame.display.set_caption("Simulacija Robot Auta - Skaliran Prikaz")
    sat = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)

    # 1. Učitavanje i skaliranje slike mape
    try:
        # Učitavamo originalnu veliku sliku
        originalna_mapa = pygame.image.load(PUTANJA_DO_SLIKE).convert()
        mapa_sirina, mapa_visina = originalna_mapa.get_size()
        print(f"Mapa uspešno učitana! Originalna veličina: {mapa_sirina}x{mapa_visina}")
        
        # Računamo faktore skaliranja za širinu i visinu
        faktor_x = SIRINA_EKRANA / mapa_sirina
        faktor_y = VISINA_EKRANA / mapa_visina
        # Uzimamo manji faktor da bi cela slika stala (zadržavamo proporcije)
        faktor_skaliranja = min(faktor_x, faktor_y)
        print(f"Faktor skaliranja: {faktor_skaliranja:.4f}")

        # Skaliramo sliku na veličinu koja staje u ekran
        nova_sirina = int(mapa_sirina * faktor_skaliranja)
        nova_visina = int(mapa_visina * faktor_skaliranja)
        skalirana_mapa = pygame.transform.smoothscale(originalna_mapa, (nova_sirina, nova_visina))

    except FileNotFoundError:
        print(f"GREŠKA: Nije pronađena slika '{PUTANJA_DO_SLIKE}'.")
        return # Prekidamo program ako nema slike

    # 2. Kreiranje auta (Počinje na sredini ORGINALNE mape)
    # Auto uvek "živi" u realnim koordinatama (npr. 2500, 2500)
    auto = RobotAuto(x=mapa_sirina // 2, y=mapa_visina // 2)

    running = True
    while running:
        # --- OBRADA DOGAĐAJA ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- SIMULACIJA UNOSA (Tastatura) ---
        tasteri = pygame.key.get_pressed()
        
        # Gas (Gore/Dole)
        if tasteri[pygame.K_UP]:
            auto.brzina += UBRZANJE
        elif tasteri[pygame.K_DOWN]:
            auto.brzina -= UBRZANJE
        else:
            # Primena trenja za postepeno usporavanje
            auto.brzina *= TRENJE

        # Volan (Levo/Desno)
        if tasteri[pygame.K_LEFT]:
            auto.ugao_volana -= 0.05
        elif tasteri[pygame.K_RIGHT]:
            auto.ugao_volana += 0.05
        else:
            # Automatsko vraćanje volana u centar (opciono, realističnije)
            auto.ugao_volana *= 0.9

        # Ograničenje ugla volana (maksimalno skretanje)
        auto.ugao_volana = max(-MAX_UGAO_VOLANA, min(auto.ugao_volana, MAX_UGAO_VOLANA))

        # --- AŽURIRANJE FIZIKE ---
        auto.azuriraj_fiziku()

        # Sprečavanje da auto izađe van granica originalne mape
        auto.x = max(0, min(auto.x, mapa_sirina))
        auto.y = max(0, min(auto.y, mapa_visina))

        # --- CRTANJE ---
        ekran.fill(CRNA) # Čišćenje ekrana

        # 1. Crtanje skalirane mape (od gornjeg levog ugla 0,0)
        ekran.blit(skalirana_mapa, (0, 0))

        # 2. Crtanje auta (prosledjujemo faktor da bi znao gde da se nacrta)
        auto.crtaj(ekran, faktor_skaliranja)

        # 3. Crtanje telemetrije (Podaci u gornjem levom uglu)
        tekst_podaci = [
            f"Brzina: {auto.brzina:.2f}",
            f"Ugao Volana: {math.degrees(auto.ugao_volana):.2f}°",
            # Prikazujemo REALNE koordinate (sa velike mape)
            f"Pozicija (Realna): X={int(auto.x)}, Y={int(auto.y)}",
            f"Smer (Heading): {math.degrees(auto.ugao) % 360:.2f}°"
        ]
        
        for i, linija in enumerate(tekst_podaci):
            povrsina_teksta = font.render(linija, True, CRNA)
            # Crtamo beli pravougaonik iza teksta radi čitljivosti
            pygame.draw.rect(ekran, BELA, (10, 10 + i * 25, 260, 25))
            ekran.blit(povrsina_teksta, (15, 12 + i * 25))

        pygame.display.flip()
        sat.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()