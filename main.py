from Logger import Logger
import time

running = True
Logger()

services = [Logger]

counter = 0
while running:
	try:
		Logger.logi("Ovo je neka poruka")
		time.sleep(2)

		Logger.log("Ovo je poruka od static metode", counter % 3)
		counter = counter + 1

	except KeyboardInterrupt:
		running = False
		for service in reversed(services):
			try:
				print("Trying to stop service: " + str(service))
				service.stop()
			except Exception as e:
				print(f"Error stopping {type(service).__name__}: {e}")

	except:
		running = False
		for service in reversed(services):
			try:
				print("Trying to stop service: " + str(type(service)))
				service.stop()
			except Exception as e:
				print(f"Error stopping {type(service).__name__}: {e}")