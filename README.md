# UDP Broadcast Biblioteka

Jednostavna biblioteka za slanje i primanje podataka preko UDP-a sa podrškm za slike, stringove, brojeve i boolean vrednosti.

## Instalacija

```bash
pip install -r requirements.txt
```

## Brza Upotreba

### Slanje podataka (Sender)

```python
from udp.udp_sender import UDP_Sender
from udp.types import DATA_TYPES, BROADCAST_MODE

# Kreiraj sender (BROADCAST mod)
sender = UDP_Sender(mode=BROADCAST_MODE.BROADCAST)

# Pošalji različite tipove podataka
sender.send("Hello World", DATA_TYPES.STRING)
sender.send(42, DATA_TYPES.INTEGER)
sender.send(3.14, DATA_TYPES.FLOAT)
sender.send(True, DATA_TYPES.BOOLEAN)
sender.send(image, DATA_TYPES.IMAGE)  # numpy array
```

### Primanje podataka (Receiver)

```python
from udp.udp_receiver import UDP_Receiver
from udp.types import DATA_TYPES

# Kreiraj receiver
receiver = UDP_Receiver()

# Čitaj podatke u petlji
while True:
    data, data_type = receiver.recv()
    
    if data is not None:
        print(f"Primljena poruka ({data_type}): {data}")
```

## Primjeri

Pogledaj folder `examples/`:

- `examples/basic/sender.py` - Osnovna primjena slanja
- `examples/basic/receiver.py` - Osnovna primjena primanja
- `examples/video/senderVideo.py` - Slanje video strima
- `examples/video/receiverVideo.py` - Primanje video strima

## API Referenca

### UDP_Sender

```python
sender = UDP_Sender(mode=BROADCAST_MODE.BROADCAST, 
                    addresses=None, 
                    port=9990)

# Pošalji podatak
sender.send(data, data_type)
```

**Parametri:**
- `mode`: `BROADCAST_MODE.BROADCAST` ili `BROADCAST_MODE.UNICAST`
- `addresses`: Lista IP adresa za UNICAST (npr. `["192.168.1.100", "192.168.1.101"]`)
- `port`: UDP port (default: 9990)

### UDP_Receiver

```python
receiver = UDP_Receiver(address="", port=9990)

# Pročitaj jednu poruku (vraća (data, data_type) ili (None, None))
data, data_type = receiver.recv()
```

**Parametri:**
- `address`: IP adresa za slušanje (default: "" za sve interfejse)
- `port`: UDP port (default: 9990)

## Tipovi podataka

Dostupni tipovi za slanje:

```python
from udp.types import DATA_TYPES

DATA_TYPES.IMAGE      # numpy array (slike)
DATA_TYPES.STRING     # Python string
DATA_TYPES.INTEGER    # Python int
DATA_TYPES.FLOAT      # Python float
DATA_TYPES.BOOLEAN    # Python bool
```

## Primjer: Video Stream

**Sender:**
```python
import cv2
from udp.udp_sender import UDP_Sender
from udp.types import DATA_TYPES

sender = UDP_Sender()
cap = cv2.VideoCapture("video.mp4")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    sender.send(frame, DATA_TYPES.IMAGE)

cap.release()
```

**Receiver:**
```python
import cv2
from udp.udp_receiver import UDP_Receiver
from udp.types import DATA_TYPES

receiver = UDP_Receiver()

while True:
    data, data_type = receiver.recv()
    
    if data is not None and data_type == DATA_TYPES.IMAGE:
        cv2.imshow("Video Stream", data)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
```

## Napomena

Biblioteka je namenjena isključivo za **razmenu podataka** preko UDP-a. Sve logike vezane za prikaz, obradu ili transformaciju podataka treba da bude na strani korisnika biblioteke.
