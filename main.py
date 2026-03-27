from flask import Flask
import config
from src.frontendUDP import FrontendUDP

app = Flask(__name__)
# Inicijalizacija menadžera
video_manager = FrontendUDP()

@app.route('/')
def homePage():
    return video_manager.get_html_template()

@app.route('/videoFeed/<int:id>')
def videoFeed(id):
    response = video_manager.get_streaming_response(id)
    return response if response else ("Invalid ID", 404)

if __name__ == "__main__":
    # start UDP threads
    video_manager.start_receivers()
    
    print(f"Sistem pokrenut na http://127.0.0.1:{config.FLASK_PORT}")
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, threaded=True)