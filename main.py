import time
from config import SERVER_IP, SERVER_PORT, SPEED_VALUES, STEER_VALUES
from src.localizationModul import localizationRPi

def main():
    # Inicijalizacija bez listi
    sim = localizationRPi(ip=SERVER_IP, port=SERVER_PORT)
    while not sim.start():
        print("Waiting on initMSG...", end="\r")
        time.sleep(0.1)

    index = 0
    last_change_time = time.time()
    change_interval = 1.5

    try:
        while True:
            # promena vrednosti iz niza na 1.5 sekundi 
            current_time = time.time()
            if current_time - last_change_time > change_interval:
                index = (index + 1) % len(SPEED_VALUES)
                last_change_time = current_time

            current_v = SPEED_VALUES[index]
            current_s = STEER_VALUES[index]

            status = sim.update(speed=current_v, steer=current_s)

            if status:
                print(f"Index: {index} | Speed: {status['speed']:>5} | Steer: {status['steer']:>5.2f}", end="\r")

            time.sleep(0.05) #20 poruka u sekundi

    except KeyboardInterrupt:
        print("\nPrekid tastaturom.")
    finally:
        sim.shutdown()

if __name__ == "__main__":
    main()