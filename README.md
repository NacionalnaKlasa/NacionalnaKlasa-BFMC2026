# 🎥 BFMC Video Surveillance - UDP Streamer

Ovaj projekat omogućava strimovanje video sadržaja u realnom vremenu putem **UDP protokola**. Sistem koristi **Flask** web server za prikazivanje više video feed-ova istovremeno, dok pozadinske niti (threads) primaju podatke sa različitih UDP portova.

## 🏗 Struktura Projekta

Prema trenutnoj lokalnoj konfiguraciji, projekat je organizovan na sledeći način:

```text
frontendUDP/
├── config.py           # Konfiguracija (lista portova, host, naslov)
├── main.py             # Glavna Flask aplikacija (pokretač)
├── README.md           # Dokumentacija projekta
├── requirements.txt    # Neophodne Python biblioteke
├── .gitignore          # Ignorisanje pycache i video fajlova
├── src/
│   └── frontendUDP.py  # Glavna klasa za procesiranje UDP frejmova
├── senders/
│   └── sender.py       # Skripta koja čita video i šalje ga na UDP port
├── udp/                # Biblioteka sa UDP_Sender i UDP_Receiver klasama
└── videos/             # Folder u kojem se nalaze .mp4 .avi fajlovi
```

## 🛠 Kako pokrenuti sistem
Sistem zahteva da server i pošiljaoci rade istovremeno u zasebnim terminalima.

### 1. Pokretanje Servera (Receiver)
Ovo će pokrenuti Flask web interfejs koji čeka podatke:

```bash
python main.py
```

Nakon pokretanja, otvori browser na adresi: http://127.0.0.1:5000

### 2. Pokretanje Slanja (Sender)
Otvori novi terminal, uđi u folder senders i pokreni skriptu:

```bash
cd senders
python sender.py
```
## ⚙️ Konfiguracija (config.py)
Sistem je potpuno modularan. Broj kamera na ekranu se automatski prilagođava listi portova:

1.  PORTS: Lista svih aktivnih UDP portova.

2.  STATE_PORTS: Portovi namenjeni isključivo za tekstualne statuse (npr. brzina, mod vožnje).

3.  FPS_LOCALCLOCK: Limitira brzinu slanja podataka ka browseru (default: 30).

## 💡 Ključne funkcionalnosti
**1.    Konstantan FPS**: Koristi FPSClock za održavanje stabilne brzine reprodukcije (npr. 30 FPS).

**2.    Automatski Loop**: Video se automatski vraća na početak kada stigne do kraja.

**3.    Dinamički Grid**: HTML šablon automatski pravi onoliko video prozora koliko ima portova definisanih u config.py.

**4.    Multithreading**: Svaka "kamera" (port) ima svoju nit koja ne blokira rad ostalih.

**5.    FPS Control:** Uveden `FPSClock` unutar svakog stream-a kako bi se sprečilo zagušenje mreže i CPU-a.

**6.    State vs Video Separation:** Sistem razlikuje portove za telemetriju (String) i portove za video (Image).

**7.    Asynchronous Updates:** Stanje (State) se na frontendu osvežava putem AJAX-a (100ms) bez prekidanja video strima.