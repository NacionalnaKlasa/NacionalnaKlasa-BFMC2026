import cv2
import threading
from flask import Flask, Response, render_template_string
from udp.udp_receiver import UDP_Receiver
from udp.types import DATA_TYPES

app = Flask(__name__)

#nek svaki sender ima zaseban port
PORTS = [9990, 9991, 9992]
N = len(PORTS)

#recnik da cuvam poslednji frejm za svaki port
# Format: { port: frame_data }
shared_frames = {port: None for port in PORTS}

def udp_reader_worker(port):
    """nit slusa samo po jedan port"""
    receiver = UDP_Receiver(port=port)
    print(f"Slušam port {port}...")
    
    while True:
        data, data_type = receiver.recv()
        if data is not None and data_type == DATA_TYPES.IMAGE:
            shared_frames[port] = data

def streamingEngine(camera_index):
    """inf petlja salje slike browseru,
    uzima frejm sa porta koji odgovara indeksu kamere"""
    port = PORTS[camera_index]
    
    while True:
        frame = shared_frames.get(port)
        
        if frame is not None:
            #jpg slika da je browser razume, pa u bajtove da mogu da saljem preko neta
            _, jpeg_image = cv2.imencode('.jpg', frame)
            image_bytes = jpeg_image.tobytes()

            #yield is most useful in situations where you need to iterate over data 
            # but don't want to store everything in memory
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + image_bytes + b'\r\n')
        else:
            # Ako frejm jos nije stigao, mala pauza da ne opteretimo procesor
            cv2.waitKey(10)

@app.route('/')
def homePage():
    html = """
    <body style="background: black; color: white; font-family: Helvetica, Arial, sans-serif; margin: 20px;">
        <h1 style="text-align: left;">Nacionalna Klasa - Video Surveillance</h1>

        <div style="display: flex; flex-wrap: wrap; gap: 20px;">
            {% for i in range(broj) %}
                <div style="border: 2px solid grey; padding: 10px; background: #111; width: 420px;">
                    <h3 style="text-align: left; margin-top: 0;">Receiver {{ i+1 }} (Port: {{ portovi[i] }})</h3>
                    <img src="/videoFeed/{{ i }}" style="width: 100%; border: 1px solid #444;">
                </div>
            {% endfor %}
        </div>
    </body>
    """
    return render_template_string(html, broj=N, portovi=PORTS)

@app.route('/videoFeed/<int:id>')
def videoFeed(id):
    # Kada browser trazi sliku, mi pokrećemo motor striminga za tu kameru
    if 0 <= id < N:
        return Response(streamingEngine(id), 
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    return "Invalid Camera ID", 404

if __name__ == "__main__":
    # jednu nit za svaki port
    for p in PORTS:
        t = threading.Thread(target=udp_reader_worker, args=(p,), daemon=True)
        t.start()
    
    print(f"Sistem na http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, threaded=True)