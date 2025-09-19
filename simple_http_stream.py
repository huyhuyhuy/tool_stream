# GIẢI PHÁP HTTP PUSH - SIÊU ĐƠN GIẢN

## WINDOWS PC - http_client.py
"""
import cv2
import requests
import base64
import time
import threading

class WindowsStreamClient:
    def __init__(self, vps_url="http://45.76.190.6:5000"):
        self.vps_url = vps_url
        self.streaming = False
    
    def capture_chrome_window(self):
        # Sử dụng code capture cũ
        # Return captured image
        pass
    
    def start_streaming(self):
        self.streaming = True
        thread = threading.Thread(target=self.stream_loop)
        thread.start()
    
    def stream_loop(self):
        while self.streaming:
            try:
                img = self.capture_chrome_window()
                if img is not None:
                    # Encode to base64
                    _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    img_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Send to VPS
                    data = {"frame": img_base64}
                    response = requests.post(f"{self.vps_url}/upload_frame", 
                                           json=data, timeout=2)
                    
                    if response.status_code != 200:
                        print("Upload failed")
                
            except Exception as e:
                print(f"Error: {e}")
            
            time.sleep(1/10)  # 10 FPS
    
    def stop_streaming(self):
        self.streaming = False

# Usage:
# client = WindowsStreamClient()
# client.start_streaming()
"""

## VPS - http_server.py
"""
from flask import Flask, request, Response, render_template_string
import base64
import threading
import time

class VPSStreamServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Windows PC Stream</title>
                <style>
                    body { font-family: Arial; text-align: center; background: #f0f0f0; }
                    .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                    img { max-width: 100%; border: 2px solid #ddd; border-radius: 10px; }
                    h1 { color: #333; }
                    .status { 
                        padding: 10px; margin: 20px 0; border-radius: 5px;
                        background: {{ '#d4edda' if latest_frame else '#f8d7da' }};
                        color: {{ '#155724' if latest_frame else '#721c24' }};
                    }
                </style>
                <script>
                    setInterval(() => {
                        const img = document.getElementById('stream');
                        img.src = '/stream?t=' + new Date().getTime();
                    }, 100); // Refresh every 100ms
                </script>
            </head>
            <body>
                <div class="container">
                    <h1>🖥️ Live Stream from Windows PC</h1>
                    <div class="status">
                        Status: {{ 'Online - Receiving stream' if latest_frame else 'Offline - Waiting for Windows PC' }}
                    </div>
                    <img id="stream" src="/stream" alt="Stream will appear here">
                    <p><strong>Public URL:</strong> http://45.76.190.6:5000</p>
                </div>
            </body>
            </html>
            ''', latest_frame=self.latest_frame)
        
        @self.app.route('/upload_frame', methods=['POST'])
        def upload_frame():
            try:
                data = request.get_json()
                frame_data = data.get('frame')
                
                if frame_data:
                    with self.frame_lock:
                        self.latest_frame = frame_data
                    return {'status': 'success'}, 200
                else:
                    return {'status': 'no_frame'}, 400
                    
            except Exception as e:
                return {'status': 'error', 'message': str(e)}, 500
        
        @self.app.route('/stream')
        def stream():
            if self.latest_frame:
                try:
                    frame_bytes = base64.b64decode(self.latest_frame)
                    return Response(frame_bytes, mimetype='image/jpeg')
                except:
                    pass
            
            # Return placeholder image
            import numpy as np
            import cv2
            placeholder = np.zeros((200, 400, 3), dtype=np.uint8)
            cv2.putText(placeholder, "Waiting for stream...", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            _, buffer = cv2.imencode('.jpg', placeholder)
            return Response(buffer.tobytes(), mimetype='image/jpeg')
    
    def run(self):
        print("🚀 VPS Stream Server starting...")
        print("🌐 Public URL: http://45.76.190.6:5000")
        print("⏳ Waiting for Windows PC to connect...")
        self.app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    server = VPSStreamServer()
    server.run()
"""

## ƯU ĐIỂM CÁCH NÀY:
# ✅ SIÊU ĐƠN GIẢN - chỉ cần HTTP POST
# ✅ Không cần ngrok, WebSocket hay gì phức tạp
# ✅ Chỉ cần requests + flask
# ✅ Hoạt động qua mọi firewall
# ✅ Dễ debug

## CÁCH SETUP:
# 1. VPS: python http_server.py
# 2. Windows: python http_client.py  
# 3. Truy cập: http://45.76.190.6:5000
# 4. XONG! Đơn giản vậy thôi!
