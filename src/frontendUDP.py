import cv2
import sys
import threading
from flask import Response, render_template_string
sys.path.insert(0, r'C:\Users\User\Desktop\bfmc\frontendUDP')
from udp.udp_receiver import UDP_Receiver
from udp.types import DATA_TYPES
import config

class FrontendUDP:
    def __init__(self):
        self.ports = config.PORTS
        self.num_cameras = len(self.ports)
        #recnik da cuvam poslednji frejm za svaki port
        # Format: { port: frame_data }
        self.shared_frames = {port: None for port in self.ports}
        self.current_state = "Waiting..."

    def _udp_reader_worker(self, port):
        """nit slusa samo po jedan port"""
        receiver = UDP_Receiver(port=port)
        print(f"[UDP] Slušam port {port}...")
        while True:
            data, data_type = receiver.recv()
            if data is not None:
                if data_type == DATA_TYPES.IMAGE:
                    self.shared_frames[port] = data
                elif data_type == DATA_TYPES.STRING:
                    self.current_state = data

    def start_receivers(self):
        """ jednu nit za svaki port"""
        for p in self.ports:
            t = threading.Thread(target=self._udp_reader_worker, args=(p,), daemon=True)
            t.start()

    def get_streaming_response(self, camera_index):
        """slanje frejmova lad ih browser trazi"""
        if not (0 <= camera_index < self.num_cameras):
            return None
        
        port = self.ports[camera_index]
        
        def generate():
            while True:
                frame = self.shared_frames.get(port)
                if frame is not None:
                    _, jpeg = cv2.imencode('.jpg', frame)
                    image_bytes = jpeg.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + image_bytes + b'\r\n')
                else:
                    cv2.waitKey(10) # Kratka pauza ako nema frejma
        
        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def get_html_template(self):
        return render_template_string("""
        <body style="background: black; color: white; font-family: Helvetica, Arial, sans-serif; margin: 20px;">
            <h1 style="text-align: left;">{{ title }}</h1>
            <h2 style="text-align: left; color: #aaa; margin-top: 0; margin-bottom: 20px;">State: {{ stanje }}</h2>
                                      
            <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                {% for i in range(broj) %}
                    <div style="border: 2px solid grey; padding: 10px; background: #111; width: 420px;">
                        <h3 style="text-align: left; margin-top: 0;">Receiver {{ i+1 }} (Port: {{ portovi[i] }})</h3>
                        <img src="/videoFeed/{{ i }}" style="width: 100%; border: 1px solid #444;">
                    </div>
                {% endfor %}
            </div>
        </body>
        """, title=config.APP_TITLE, broj=self.num_cameras, portovi=self.ports, stanje=self.current_state)