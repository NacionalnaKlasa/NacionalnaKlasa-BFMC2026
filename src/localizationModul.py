import math
import time
from src.tcpLibF import FloydClient

class localizationRPi:
    def __init__(self, ip, port):
        self.client = FloydClient(ip, port)
        self.initialized = False
        self.is_connected = self.client.connecting()

    def start(self):
        """da li je stigao init od servera"""
        if not self.is_connected:
            return False

        dolazne_poruke = self.client.get_data()
        for msg in dolazne_poruke:
            if msg.get("type") == "init":
                self.initialized = True
                print("\n[INIT] PC Server je poslao init.")
        
        return self.initialized

    def update(self, speed, steer):
        """Prima konkretnu brzinu i ugao i salje ih serveru."""
        if not self.is_connected or not self.initialized:
            return None

        # Slanje podataka preko send_data
        self.client.send_data({
            "type": "telemetry",
            "speed": speed,
            "steering_angle": steer
        })

        return {
            "speed": speed,
            "steer": steer
        }

    def shutdown(self):
        print("\nEND...")
        try:
            # Slanje nula za stop
            self.client.send_data({"type": "telemetry", "speed": 0.0, "steering_angle": 0.0})
            time.sleep(0.1)
        except:
            pass
        self.client.closing()