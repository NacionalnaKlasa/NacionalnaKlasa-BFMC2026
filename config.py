#nek svaki sender ima zaseban port
#odvojen je lista za sting portove, za ostale se podrazumeva da su video portovi
#bitno je koliko prozora cu da prikazujem u frontendu
PORTS = [8000, 9990, 9991, 9992, 9993]
STATE_PORTS = [8000]

FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000

APP_TITLE = "Nacionalna Klasa - Video Surveillance"

FPS_LOCALCLOCK = 30 #da ne baguje server, precesto frejmova salje i bafer se prepuni