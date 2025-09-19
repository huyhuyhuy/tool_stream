# GIẢI PHÁP WEBSOCKET - ĐƠN GIẢN HƠN

## WINDOWS PC - websocket_client.py
"""
import cv2
import numpy as np
import base64
import websocket
import json
import threading
import time

# Capture screen và gửi qua WebSocket
def capture_and_send():
    ws = websocket.WebSocket()
    ws.connect("ws://45.76.190.6:8080/stream")
    
    while True:
        # Capture Chrome window (sử dụng code cũ)
        img = capture_chrome_window()
        
        if img is not None:
            # Encode to base64
            _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Send via WebSocket
            data = {
                "type": "frame",
                "data": img_base64
            }
            ws.send(json.dumps(data))
        
        time.sleep(1/15)  # 15 FPS
"""

## VPS - websocket_server.py
"""
import websocket_server
import base64
import threading
from flask import Flask, Response

class StreamServer:
    def __init__(self):
        self.latest_frame = None
        self.websocket_server = websocket_server.WebsocketServer(8080)
        self.flask_app = Flask(__name__)
        
    def new_client(self, client, server):
        print(f"New client connected: {client['id']}")
    
    def message_received(self, client, server, message):
        try:
            data = json.loads(message)
            if data['type'] == 'frame':
                self.latest_frame = data['data']
        except:
            pass
    
    def generate_frames(self):
        while True:
            if self.latest_frame:
                frame_bytes = base64.b64decode(self.latest_frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(1/15)
    
    def setup_flask(self):
        @self.flask_app.route('/')
        def index():
            return '''
            <html>
                <body>
                    <h1>Stream from Windows PC</h1>
                    <img src="/stream" style="width:100%;">
                </body>
            </html>
            '''
        
        @self.flask_app.route('/stream')
        def stream():
            return Response(self.generate_frames(),
                          mimetype='multipart/x-mixed-replace; boundary=frame')
    
    def run(self):
        # Start WebSocket server
        self.websocket_server.set_fn_new_client(self.new_client)
        self.websocket_server.set_fn_message_received(self.message_received)
        
        ws_thread = threading.Thread(target=self.websocket_server.serve_forever)
        ws_thread.start()
        
        # Start Flask server
        self.setup_flask()
        self.flask_app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    server = StreamServer()
    server.run()
"""

## ƯU ĐIỂM:
# ✅ Không cần ngrok
# ✅ Real-time streaming
# ✅ Đơn giản setup
# ✅ Stable connection

## CÁCH SETUP:
# 1. VPS: pip install websocket-server flask
# 2. Windows: pip install websocket-client
# 3. VPS: python websocket_server.py
# 4. Windows: python websocket_client.py
# 5. Truy cập: http://45.76.190.6:5000
