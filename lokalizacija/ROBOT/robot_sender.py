import paho.mqtt.client as mqtt
import time
import json
import random

# --- PODEŠAVANJA ---
BROKER = "test.mosquitto.org" # Javni server za testiranje (kasnije možete dići svoj)
PORT = 1883
TOPIC = "robot/telemetry"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Robot povezan na MQTT Broker!")
    else:
        print(f"❌ Greška pri povezivanju, kod: {rc}")

client = mqtt.Client()
client.on_connect = on_connect

print("Povezujem se na broker...")
client.connect(BROKER, PORT, 60)
client.loop_start() # Pokreće proces u pozadini

try:
    while True:
        # --- OVDE ČITATE PRAVE SENZORE ---
        # Primer: brzina = motor_driver.get_speed()
        # Primer: ugao = servo.get_angle()
        
        # Simuliramo podatke (zamenite ovo stvarnim podacima)
        realna_brzina = 5.0  
        realni_ugao = random.uniform(-0.1, 0.1) # Malo levo-desno
        
        # Pakujemo podatke u JSON (standardni format)
        payload = {
            "brzina": realna_brzina,
            "ugao": realni_ugao
        }
        
        # Šaljemo poruku
        client.publish(TOPIC, json.dumps(payload))
        
        print(f"📡 Poslato: {payload}")
        
        time.sleep(0.1) # Šaljemo 10 puta u sekundi (10Hz)

except KeyboardInterrupt:
    print("Prekid rada...")
    client.loop_stop()
    client.disconnect()