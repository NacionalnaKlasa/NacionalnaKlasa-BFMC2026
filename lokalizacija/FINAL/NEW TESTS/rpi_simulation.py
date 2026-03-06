import time
from tcpLib import FloydClient # Učitavamo klijent deo biblioteke

# Poveži se na PC (ako pokrećeš na istom kompjuteru koristi '127.0.0.1')
client = FloydClient(ip_pc='127.0.0.1', port=65432)

if client.connecting():
    print("Simulacija autića pokrenuta!")
    try:
        while True:
            # Slanje testnih podataka svakih par sekundi
            podaci = {
                "v": 25.0,
                "delta": 0.0
            }
            client.send_data(podaci)
            print(f"Poslato: {podaci}")
            
            # Pauza pre slanja sledeće komande
            time.sleep(0.1) 
    except KeyboardInterrupt:
        client.closing()