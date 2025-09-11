import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
import threading
import time
import mss
from PIL import Image, ImageTk
import pyautogui
import webbrowser
import pyperclip
from flask import Flask, Response, render_template_string
import queue
import io
import base64

class ScreenStreamTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen Stream Tool")
        self.root.geometry("900x430")
        self.root.configure(bg='#f0f0f0')
        
        # Biến lưu trữ vùng chọn
        self.region1 = None
        self.region2 = None
        self.streaming1 = False
        self.streaming2 = False
        
        # Biến cho streaming
        self.frame_queue1 = queue.Queue(maxsize=2)
        self.frame_queue2 = queue.Queue(maxsize=2)
        self.capture_thread1 = None
        self.capture_thread2 = None
        
        # Flask app
        self.app = Flask(__name__)
        self.setup_flask_routes()
        
        # MSS object for screen capture - create new instance for each thread
        self.sct1 = None
        self.sct2 = None
        
        self.setup_ui()
        self.setup_flask_thread()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="Screen Stream Tool", 
                              font=("Arial", 16, "bold"), bg='#f0f0f0')
        title_label.pack(pady=10)
        
        # Main container với layout ngang
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame cho Region 1 (bên trái)
        frame1 = tk.Frame(main_frame, bg='#e0e0e0', relief='raised', bd=2)
        frame1.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(frame1, text="Region 1", font=("Arial", 12, "bold"), bg='#e0e0e0').pack(pady=5)
        
        btn_frame1 = tk.Frame(frame1, bg='#e0e0e0')
        btn_frame1.pack(pady=5)
        
        self.set_region1_btn = tk.Button(btn_frame1, text="Set Region 1", 
                                        command=self.select_region1, 
                                        bg='#4CAF50', fg='white', font=("Arial", 10))
        self.set_region1_btn.pack(side='left', padx=5)
        
        self.start_stream1_btn = tk.Button(btn_frame1, text="Start Stream 1", 
                                          command=self.toggle_stream1, 
                                          bg='#2196F3', fg='white', font=("Arial", 10),
                                          state='disabled')
        self.start_stream1_btn.pack(side='left', padx=5)
        
        # Preview cho Region 1 (ảnh tĩnh)
        self.preview1 = tk.Label(frame1, text="No region selected", 
                                bg='black', fg='white')
        self.preview1.pack(pady=5)
        
        # Link cho Region 1
        self.link1_frame = tk.Frame(frame1, bg='#e0e0e0')
        self.link1_frame.pack(fill='x', pady=5)
        
        self.link1_label = tk.Label(self.link1_frame, text="Link: Not available", 
                                   bg='#e0e0e0', font=("Arial", 9))
        self.link1_label.pack(side='left')
        
        self.copy_link1_btn = tk.Button(self.link1_frame, text="Copy", 
                                       command=self.copy_link1, 
                                       bg='#FF9800', fg='white', font=("Arial", 8),
                                       state='disabled')
        self.copy_link1_btn.pack(side='right', padx=5)
        
        # Frame cho Region 2 (bên phải)
        frame2 = tk.Frame(main_frame, bg='#e0e0e0', relief='raised', bd=2)
        frame2.pack(side='right', fill='both', expand=True, padx=5)
        
        tk.Label(frame2, text="Region 2", font=("Arial", 12, "bold"), bg='#e0e0e0').pack(pady=5)
        
        btn_frame2 = tk.Frame(frame2, bg='#e0e0e0')
        btn_frame2.pack(pady=5)
        
        self.set_region2_btn = tk.Button(btn_frame2, text="Set Region 2", 
                                        command=self.select_region2, 
                                        bg='#4CAF50', fg='white', font=("Arial", 10))
        self.set_region2_btn.pack(side='left', padx=5)
        
        self.start_stream2_btn = tk.Button(btn_frame2, text="Start Stream 2", 
                                          command=self.toggle_stream2, 
                                          bg='#2196F3', fg='white', font=("Arial", 10),
                                          state='disabled')
        self.start_stream2_btn.pack(side='left', padx=5)
        
        # Preview cho Region 2 (ảnh tĩnh)
        self.preview2 = tk.Label(frame2, text="No region selected", 
                                bg='black', fg='white')
        self.preview2.pack(pady=5)
        
        # Link cho Region 2
        self.link2_frame = tk.Frame(frame2, bg='#e0e0e0')
        self.link2_frame.pack(fill='x', pady=5)
        
        self.link2_label = tk.Label(self.link2_frame, text="Link: Not available", 
                                   bg='#e0e0e0', font=("Arial", 9))
        self.link2_label.pack(side='left')
        
        self.copy_link2_btn = tk.Button(self.link2_frame, text="Copy", 
                                       command=self.copy_link2, 
                                       bg='#FF9800', fg='white', font=("Arial", 8),
                                       state='disabled')
        self.copy_link2_btn.pack(side='right', padx=5)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Ready", 
                                    bg='#f0f0f0', font=("Arial", 10))
        self.status_label.pack(side='bottom', pady=5)
        
    def select_region1(self):
        self.select_region(1)
        
    def select_region2(self):
        self.select_region(2)
        
    def select_region(self, region_num):
        self.root.withdraw()  # Ẩn cửa sổ chính
        time.sleep(0.5)  # Đợi một chút để cửa sổ ẩn hoàn toàn
        
        try:
            # Tạo cửa sổ chọn vùng đơn giản
            root_region = tk.Toplevel()
            root_region.title(f"Select Region {region_num}")
            root_region.attributes('-fullscreen', True)
            root_region.attributes('-alpha', 0.3)
            root_region.configure(bg='black')
            root_region.overrideredirect(True)  # Loại bỏ thanh tiêu đề
            
            # Tạo canvas để vẽ
            canvas = tk.Canvas(root_region, bg='black', highlightthickness=0)
            canvas.pack(fill='both', expand=True)
            
            # Thêm hướng dẫn
            canvas.create_text(root_region.winfo_screenwidth()//2, 50, 
                             text=f"Click and drag to select Region {region_num}\nPress ESC to cancel", 
                             fill='white', font=("Arial", 16), justify='center')
            
            # Biến để lưu vùng chọn
            start_x = start_y = end_x = end_y = 0
            selecting = False
            
            def on_click(event):
                nonlocal start_x, start_y, selecting
                start_x, start_y = event.x, event.y
                selecting = True
                
            def on_drag(event):
                nonlocal end_x, end_y
                if selecting:
                    end_x, end_y = event.x, event.y
                    # Vẽ hình chữ nhật
                    canvas.delete("rect")
                    canvas.create_rectangle(start_x, start_y, end_x, end_y, 
                                          outline='red', width=2, tags="rect")
            
            def on_release(event):
                nonlocal end_x, end_y, selecting
                if selecting:
                    end_x, end_y = event.x, event.y
                    selecting = False
                    # Lưu vùng chọn
                    region_coords = {
                        'left': min(start_x, end_x),
                        'top': min(start_y, end_y),
                        'width': abs(end_x - start_x),
                        'height': abs(end_y - start_y)
                    }
                    
                    if region_coords['width'] > 10 and region_coords['height'] > 10:
                        if region_num == 1:
                            self.region1 = region_coords
                            self.start_stream1_btn.config(state='normal')
                            self.capture_preview_image(1)
                        else:
                            self.region2 = region_coords
                            self.start_stream2_btn.config(state='normal')
                            self.capture_preview_image(2)
                        
                        self.status_label.config(text=f"Region {region_num} selected: {region_coords['width']}x{region_coords['height']}")
                    
                    root_region.destroy()
                    self.root.deiconify()  # Hiển thị lại cửa sổ chính
                    
            def on_escape(event):
                root_region.destroy()
                self.root.deiconify()
                
            # Bind events
            canvas.bind('<Button-1>', on_click)
            canvas.bind('<B1-Motion>', on_drag)
            canvas.bind('<ButtonRelease-1>', on_release)
            root_region.bind('<Escape>', on_escape)
            root_region.focus_set()
            
            # Đảm bảo cửa sổ ở trên cùng
            root_region.lift()
            root_region.attributes('-topmost', True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting region: {str(e)}")
            self.root.deiconify()
            
    def capture_preview_image(self, region_num):
        """Capture a static preview image after region selection"""
        try:
            if region_num == 1 and self.region1:
                img = self.capture_screen_region(self.region1)
                if img is not None:
                    # Resize for preview - maintain aspect ratio
                    h, w = img.shape[:2]
                    max_width, max_height = 300, 200  # Kích thước preview vừa phải
                    
                    # Calculate scaling factor
                    scale = min(max_width/w, max_height/h)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    
                    # Đảm bảo kích thước tối thiểu
                    if new_w < 80:
                        new_w = 80
                    if new_h < 60:
                        new_h = 60
                    
                    preview_img = cv2.resize(img, (new_w, new_h))
                    preview_img = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
                    preview_img = Image.fromarray(preview_img)
                    preview_img = ImageTk.PhotoImage(preview_img)
                    
                    self.preview1.config(image=preview_img, text="")
                    self.preview1.image = preview_img
                    
            elif region_num == 2 and self.region2:
                img = self.capture_screen_region(self.region2)
                if img is not None:
                    # Resize for preview - maintain aspect ratio
                    h, w = img.shape[:2]
                    max_width, max_height = 300, 200  # Kích thước preview vừa phải
                    
                    # Calculate scaling factor
                    scale = min(max_width/w, max_height/h)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    
                    # Đảm bảo kích thước tối thiểu
                    if new_w < 80:
                        new_w = 80
                    if new_h < 60:
                        new_h = 60
                    
                    preview_img = cv2.resize(img, (new_w, new_h))
                    preview_img = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
                    preview_img = Image.fromarray(preview_img)
                    preview_img = ImageTk.PhotoImage(preview_img)
                    
                    self.preview2.config(image=preview_img, text="")
                    self.preview2.image = preview_img
                    
        except Exception as e:
            print(f"Error capturing preview image for region {region_num}: {e}")
            
    def update_preview_image(self, region_num, preview_img):
        """Update preview image in main thread"""
        try:
            if region_num == 1:
                self.preview1.config(image=preview_img)
                self.preview1.image = preview_img
            elif region_num == 2:
                self.preview2.config(image=preview_img)
                self.preview2.image = preview_img
        except Exception as e:
            print(f"Error updating preview {region_num}: {e}")
            
    def toggle_stream1(self):
        if not self.streaming1:
            self.start_stream1()
        else:
            self.stop_stream1()
            
    def toggle_stream2(self):
        if not self.streaming2:
            self.start_stream2()
        else:
            self.stop_stream2()
            
    def start_stream1(self):
        if not self.region1:
            messagebox.showerror("Error", "Please select Region 1 first!")
            return
            
        self.streaming1 = True
        self.start_stream1_btn.config(text="Stop Stream 1", bg='#f44336')
        self.capture_thread1 = threading.Thread(target=self.capture_region1, daemon=True)
        self.capture_thread1.start()
        self.status_label.config(text="Stream 1 started")
        
        # Update link display
        self.link1_label.config(text="Link: http://localhost:5000/stream1")
        self.copy_link1_btn.config(state='normal')
        
    def start_stream2(self):
        if not self.region2:
            messagebox.showerror("Error", "Please select Region 2 first!")
            return
            
        self.streaming2 = True
        self.start_stream2_btn.config(text="Stop Stream 2", bg='#f44336')
        self.capture_thread2 = threading.Thread(target=self.capture_region2, daemon=True)
        self.capture_thread2.start()
        self.status_label.config(text="Stream 2 started")
        
        # Update link display
        self.link2_label.config(text="Link: http://localhost:5000/stream2")
        self.copy_link2_btn.config(state='normal')
        
    def stop_stream1(self):
        self.streaming1 = False
        self.start_stream1_btn.config(text="Start Stream 1", bg='#2196F3')
        self.status_label.config(text="Stream 1 stopped")
        
    def stop_stream2(self):
        self.streaming2 = False
        self.start_stream2_btn.config(text="Start Stream 2", bg='#2196F3')
        self.status_label.config(text="Stream 2 stopped")
        
    def capture_region1(self):
        while self.streaming1:
            try:
                if self.region1:
                    # Capture screen region using pyautogui
                    img = self.capture_screen_region(self.region1)
                    
                    if img is not None:
                        # Add to queue for streaming only
                        if not self.frame_queue1.full():
                            self.frame_queue1.put(img)
                        
            except Exception as e:
                print(f"Error capturing region 1: {e}")
                
            time.sleep(1/5)  # 5 FPS để tránh treo máy
            
    def capture_region2(self):
        while self.streaming2:
            try:
                if self.region2:
                    # Capture screen region using pyautogui
                    img = self.capture_screen_region(self.region2)
                    
                    if img is not None:
                        # Add to queue for streaming only
                        if not self.frame_queue2.full():
                            self.frame_queue2.put(img)
                        
            except Exception as e:
                print(f"Error capturing region 2: {e}")
                
            time.sleep(1/5)  # 5 FPS để tránh treo máy
            
    def capture_screen_region(self, region):
        """Capture screen region using pyautogui"""
        try:
            # Capture screenshot of the region
            screenshot = pyautogui.screenshot(region=(region['left'], region['top'], 
                                                    region['width'], region['height']))
            
            # Convert PIL to OpenCV format
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Debug: print region info
            print(f"Capturing region: {region['left']}, {region['top']}, {region['width']}, {region['height']}")
            print(f"Image shape: {img.shape}")
            
            return img
            
        except Exception as e:
            print(f"Error in capture_screen_region: {e}")
            return None
            
    def setup_flask_routes(self):
        @self.app.route('/')
        def index():
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Screen Stream</title>
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
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Screen Stream Tool</h1>
                    
                    <div class="stream-box">
                        <h2>Region 1 Stream</h2>
                        <div id="status1" class="status offline">Offline</div>
                        <img id="stream1" src="/stream1" style="display: none;">
                    </div>
                    
                    <div class="stream-box">
                        <h2>Region 2 Stream</h2>
                        <div id="status2" class="status offline">Offline</div>
                        <img id="stream2" src="/stream2" style="display: none;">
                    </div>
                </div>
                
                <script>
                    function checkStream(streamId) {
                        const img = document.getElementById('stream' + streamId);
                        const status = document.getElementById('status' + streamId);
                        
                        img.onload = function() {
                            status.textContent = 'Online';
                            status.className = 'status online';
                            img.style.display = 'block';
                        };
                        
                        img.onerror = function() {
                            status.textContent = 'Offline';
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
            
        @self.app.route('/stream1')
        def stream1():
            return Response(self.generate_frames(1), 
                          mimetype='multipart/x-mixed-replace; boundary=frame')
            
        @self.app.route('/stream2')
        def stream2():
            return Response(self.generate_frames(2), 
                          mimetype='multipart/x-mixed-replace; boundary=frame')
            
    def generate_frames(self, region_num):
        while True:
            try:
                frame = None
                
                # Check if streaming is active
                if region_num == 1 and self.streaming1:
                    if not self.frame_queue1.empty():
                        frame = self.frame_queue1.get()
                    else:
                        # If no frame in queue, capture directly
                        if self.region1:
                            frame = self.capture_screen_region(self.region1)
                elif region_num == 2 and self.streaming2:
                    if not self.frame_queue2.empty():
                        frame = self.frame_queue2.get()
                    else:
                        # If no frame in queue, capture directly
                        if self.region2:
                            frame = self.capture_screen_region(self.region2)
                
                if frame is not None:
                    # Resize frame for web streaming
                    h, w = frame.shape[:2]
                    max_width, max_height = 800, 600  # Kích thước vừa phải
                    
                    # Calculate scaling factor
                    scale = min(max_width/w, max_height/h)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    
                    frame = cv2.resize(frame, (new_w, new_h))
                    
                    # Encode frame as JPEG
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    frame_bytes = buffer.tobytes()
                    
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    # Send a test frame if no data
                    frame = np.zeros((200, 200, 3), dtype=np.uint8)
                    cv2.putText(frame, f"No data for region {region_num}", (10, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    frame_bytes = buffer.tobytes()
                    
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                       
            except Exception as e:
                print(f"Error generating frames for region {region_num}: {e}")
                time.sleep(0.1)
                
    def setup_flask_thread(self):
        flask_thread = threading.Thread(target=self.run_flask, daemon=True)
        flask_thread.start()
        
    def run_flask(self):
        self.app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        
    def copy_link1(self):
        if self.streaming1:
            link = "http://localhost:5000/stream1"
            pyperclip.copy(link)
            self.link1_label.config(text=f"Link: {link}")
            self.copy_link1_btn.config(state='normal')
            messagebox.showinfo("Link Copied", f"Stream 1 link copied to clipboard:\n{link}")
        else:
            messagebox.showwarning("Warning", "Please start Stream 1 first!")
            
    def copy_link2(self):
        if self.streaming2:
            link = "http://localhost:5000/stream2"
            pyperclip.copy(link)
            self.link2_label.config(text=f"Link: {link}")
            self.copy_link2_btn.config(state='normal')
            messagebox.showinfo("Link Copied", f"Stream 2 link copied to clipboard:\n{link}")
        else:
            messagebox.showwarning("Warning", "Please start Stream 2 first!")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenStreamTool()
    app.run()
