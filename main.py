from Logger import Logger
import time

running = True
logger = Logger()

services = [logger]

while running:
	try:
		logger.logi("Ovo je neka poruka")
		time.sleep(2)

		Logger.logi("Ovo je poruka od static metode")

	except KeyboardInterrupt:
		running = False
		for service in reversed(services):
			try:
				print("Trying to stop service: " + str(type(service)))
				service.stop()
			except Exception as e:
				print(f"Error stopping {type(service).__name__}: {e}")