from flask import Flask, Response, render_template_string, request
import requests
import threading
import time
import queue
import cv2
import numpy as np
import base64
import io

class VPSRelayServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()
        
        # Store streams from Windows PC
        self.windows_pc_ip = None  # Will be set when Windows PC connects
        self.stream1_active = False
        self.stream2_active = False
        
        # Frame queues for each stream
        self.frame_queue1 = queue.Queue(maxsize=5)
        self.frame_queue2 = queue.Queue(maxsize=5)
        
        # Threads for fetching from Windows PC
        self.fetch_thread1 = None
        self.fetch_thread2 = None
        
    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Screen Stream Relay</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .stream-box { 
                        background: white; 
                        border-radius: 10px; 
                        padding: 20px; 
                        margin: 20px 0; 
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    h1 { text-align: center; color: #333; }
                    h2 { color: #666; }
                    img { 
                        max-width: 100%; 
                        height: auto; 
                        border: 2px solid #ddd; 
                        border-radius: 5px;
                    }
                    .status { 
                        padding: 10px; 
                        margin: 10px 0; 
                        border-radius: 5px; 
                        text-align: center;
                    }
                    .online { background: #d4edda; color: #155724; }
                    .offline { background: #f8d7da; color: #721c24; }
                    .info { background: #d1ecf1; color: #0c5460; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🖥️ Screen Stream Relay Server</h1>
                    
                    <div class="stream-box">
                        <h2>Chrome Window 1 Stream</h2>
                        <div id="status1" class="status offline">Waiting for Windows PC connection...</div>
                        <img id="stream1" src="/stream1" style="display: none;">
                    </div>
                    
                    <div class="stream-box">
                        <h2>Chrome Window 2 Stream</h2>
                        <div id="status2" class="status offline">Waiting for Windows PC connection...</div>
                        <img id="stream2" src="/stream2" style="display: none;">
                    </div>
                    
                    <div class="stream-box">
                        <div class="status info">
                            <strong>Server Status:</strong> Running on VPS<br>
                            <strong>Windows PC IP:</strong> <span id="windows_ip">Not connected</span><br>
                            <strong>Public URL:</strong> <span id="public_url">http://45.76.190.6:5000</span>
                        </div>
                    </div>
                </div>
                
                <script>
                    function checkStream(streamId) {
                        const img = document.getElementById('stream' + streamId);
                        const status = document.getElementById('status' + streamId);
                        
                        img.onload = function() {
                            status.textContent = 'Online - Stream from Windows PC';
                            status.className = 'status online';
                            img.style.display = 'block';
                        };
                        
                        img.onerror = function() {
                            status.textContent = 'Offline - Waiting for Windows PC';
                            status.className = 'status offline';
                            img.style.display = 'none';
                        };
                        
                        img.src = '/stream' + streamId + '?t=' + new Date().getTime();
                    }
                    
                    // Check streams every 2 seconds
                    setInterval(() => checkStream(1), 2000);
                    setInterval(() => checkStream(2), 2000);
                    
                    // Initial check
                    checkStream(1);
                    checkStream(2);
                </script>
            </body>
            </html>
            """)
        
        @self.app.route('/register', methods=['POST'])
        def register_windows_pc():
            """Windows PC đăng ký IP để VPS biết nơi lấy stream"""
            data = request.get_json()
            self.windows_pc_ip = data.get('ip')
            print(f"Windows PC registered: {self.windows_pc_ip}")
            return {"status": "success", "message": "Windows PC registered"}
        
        @self.app.route('/stream1')
        def stream1():
            return Response(self.generate_frames(1), 
                          mimetype='multipart/x-mixed-replace; boundary=frame')
        
        @self.app.route('/stream2')
        def stream2():
            return Response(self.generate_frames(2), 
                          mimetype='multipart/x-mixed-replace; boundary=frame')
    
    def generate_frames(self, stream_num):
        """Generate frames for public streaming"""
        while True:
            try:
                frame = None
                
                # Get frame from queue
                if stream_num == 1 and not self.frame_queue1.empty():
                    frame = self.frame_queue1.get()
                elif stream_num == 2 and not self.frame_queue2.empty():
                    frame = self.frame_queue2.get()
                
                if frame is not None:
                    # Resize frame for web streaming
                    h, w = frame.shape[:2]
                    max_width, max_height = 1200, 900
                    
                    scale = min(max_width/w, max_height/h)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    
                    frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
                    
                    # Encode as JPEG
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    frame_bytes = buffer.tobytes()
                    
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    # Send placeholder frame
                    frame = np.zeros((200, 200, 3), dtype=np.uint8)
                    cv2.putText(frame, f"Waiting for Windows PC...", (10, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    frame_bytes = buffer.tobytes()
                    
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                       
            except Exception as e:
                print(f"Error generating frames for stream {stream_num}: {e}")
                time.sleep(0.1)
    
    def start_fetching_from_windows(self, stream_num):
        """Fetch frames from Windows PC and add to queue"""
        while True:
            try:
                if not self.windows_pc_ip:
                    time.sleep(1)
                    continue
                
                # Check if it's an ngrok URL or IP
                if 'ngrok.io' in self.windows_pc_ip or 'ngrok-free.app' in self.windows_pc_ip:
                    # It's an ngrok URL - add header to skip warning
                    url = f"https://{self.windows_pc_ip}/stream{stream_num}"
                    headers = {'ngrok-skip-browser-warning': 'true'}
                else:
                    # It's an IP address
                    url = f"http://{self.windows_pc_ip}:5000/stream{stream_num}"
                    headers = {}
                
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    # Parse the multipart response
                    content = response.content
                    if b'--frame' in content:
                        # Extract image data
                        parts = content.split(b'--frame')
                        for part in parts[1:]:  # Skip first empty part
                            if b'Content-Type: image' in part:
                                # Find image data
                                img_start = part.find(b'\r\n\r\n') + 4
                                img_end = part.rfind(b'\r\n')
                                if img_start > 3 and img_end > img_start:
                                    img_data = part[img_start:img_end]
                                    
                                    # Decode image
                                    nparr = np.frombuffer(img_data, np.uint8)
                                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                                    
                                    if frame is not None:
                                        # Add to appropriate queue
                                        if stream_num == 1 and not self.frame_queue1.full():
                                            self.frame_queue1.put(frame)
                                        elif stream_num == 2 and not self.frame_queue2.full():
                                            self.frame_queue2.put(frame)
                                        break
                
            except Exception as e:
                print(f"Error fetching from Windows PC for stream {stream_num}: {e}")
                time.sleep(1)
    
    def run(self, host='0.0.0.0', port=5000):
        # Start fetching threads
        self.fetch_thread1 = threading.Thread(target=self.start_fetching_from_windows, args=(1,), daemon=True)
        self.fetch_thread2 = threading.Thread(target=self.start_fetching_from_windows, args=(2,), daemon=True)
        
        self.fetch_thread1.start()
        self.fetch_thread2.start()
        
        print(f"🚀 VPS Relay Server starting on {host}:{port}")
        print(f"🌐 Public URL: http://45.76.190.6:{port}")
        print("⏳ Waiting for Windows PC to connect...")
        
        self.app.run(host=host, port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    server = VPSRelayServer()
    server.run()
