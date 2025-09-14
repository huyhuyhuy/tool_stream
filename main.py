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
import win32gui
import win32ui
import pygetwindow as gw
import dxcam
import ctypes

class ScreenStreamTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stream Tool")
        self.root.geometry("400x400")
        self.root.configure(bg='#f0f0f0')
        
        # Biến lưu trữ cửa sổ đã chọn
        self.selected_window1 = None
        self.selected_window2 = None
        self.streaming1 = False
        self.streaming2 = False
        
        # Cài đặt chất lượng stream
        self.use_png = False  # True = PNG (chất lượng cao), False = JPEG (nhanh)
        
        # Biến cho streaming
        self.frame_queue1 = queue.Queue(maxsize=2)
        self.frame_queue2 = queue.Queue(maxsize=2)
        self.capture_thread1 = None
        self.capture_thread2 = None
        
        
        # Flask app
        self.app = Flask(__name__)
        self.setup_flask_routes()
        
        # DXCAM objects for window capture
        self.camera1 = None
        self.camera2 = None
        
        # Initialize DXCAM
        try:
            self.dxcam_camera = dxcam.create()
            self.status_label = None  # Will be set in setup_ui
        except Exception as e:
            print(f"Error initializing DXCAM: {e}")
            self.dxcam_camera = None
        
        self.setup_ui()
        self.setup_flask_thread()
        
    def setup_ui(self):
      
        # Main container với layout dọc
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame cho Window 1
        frame1 = tk.Frame(main_frame, bg='#e0e0e0', relief='raised', bd=2)
        frame1.pack(fill='x', pady=5)
        
        tk.Label(frame1, text="Window 1", font=("Arial", 12, "bold"), bg='#e0e0e0').pack(pady=5)
        
        # Window selection frame
        window_frame1 = tk.Frame(frame1, bg='#e0e0e0')
        window_frame1.pack(fill='x', pady=5)
        
        tk.Label(window_frame1, text="Select Chrome Window:", bg='#e0e0e0', font=("Arial", 9)).pack(anchor='w')
        
        self.window_var1 = tk.StringVar()
        self.window_combo1 = ttk.Combobox(window_frame1, textvariable=self.window_var1, 
                                         state='readonly', width=50)
        self.window_combo1.pack(fill='x', pady=2)
        self.window_combo1.bind('<<ComboboxSelected>>', lambda e: self.select_window(1))
        
        btn_frame1 = tk.Frame(frame1, bg='#e0e0e0')
        btn_frame1.pack(pady=5)
        
        self.refresh_windows_btn1 = tk.Button(btn_frame1, text="Refresh", 
                                            command=self.refresh_windows, 
                                            font=("Arial", 9))
        self.refresh_windows_btn1.pack(side='left', padx=2)
        
        self.start_stream1_btn = tk.Button(btn_frame1, text="Start Stream 1", 
                                          command=self.toggle_stream1, 
                                          font=("Arial", 9),
                                          state='disabled')
        self.start_stream1_btn.pack(side='left', padx=2)
        
        # Quality toggle button
        self.quality_btn = tk.Button(btn_frame1, text="Quality: JPEG", 
                                    command=self.toggle_quality, 
                                    font=("Arial", 8))
        self.quality_btn.pack(side='right', padx=2)
        
        # Link cho Window 1
        self.link1_frame = tk.Frame(frame1, bg='#e0e0e0')
        self.link1_frame.pack(fill='x', pady=5)
        
        self.link1_label = tk.Label(self.link1_frame, text="Link: Not available", 
                                   bg='#e0e0e0', font=("Arial", 9), 
                                   cursor="hand2", fg="blue")
        self.link1_label.pack(side='left')
        self.link1_label.bind("<Button-1>", lambda e: self.copy_link1())
        
        # Frame cho Window 2
        frame2 = tk.Frame(main_frame, bg='#e0e0e0', relief='raised', bd=2)
        frame2.pack(fill='x', pady=5)
        
        tk.Label(frame2, text="Window 2", font=("Arial", 12, "bold"), bg='#e0e0e0').pack(pady=5)
        
        # Window selection frame
        window_frame2 = tk.Frame(frame2, bg='#e0e0e0')
        window_frame2.pack(fill='x', pady=5)
        
        tk.Label(window_frame2, text="Select Chrome Window:", bg='#e0e0e0', font=("Arial", 9)).pack(anchor='w')
        
        self.window_var2 = tk.StringVar()
        self.window_combo2 = ttk.Combobox(window_frame2, textvariable=self.window_var2, 
                                         state='readonly', width=50)
        self.window_combo2.pack(fill='x', pady=2)
        self.window_combo2.bind('<<ComboboxSelected>>', lambda e: self.select_window(2))
        
        btn_frame2 = tk.Frame(frame2, bg='#e0e0e0')
        btn_frame2.pack(pady=5)
        
        self.refresh_windows_btn2 = tk.Button(btn_frame2, text="Refresh", 
                                            command=self.refresh_windows, 
                                            font=("Arial", 9))
        self.refresh_windows_btn2.pack(side='left', padx=2)
        
        self.start_stream2_btn = tk.Button(btn_frame2, text="Start Stream 2", 
                                          command=self.toggle_stream2, 
                                          font=("Arial", 9),
                                          state='disabled')
        self.start_stream2_btn.pack(side='left', padx=2)
        
        # Link cho Window 2
        self.link2_frame = tk.Frame(frame2, bg='#e0e0e0')
        self.link2_frame.pack(fill='x', pady=5)
        
        self.link2_label = tk.Label(self.link2_frame, text="Link: Not available", 
                                   bg='#e0e0e0', font=("Arial", 9),
                                   cursor="hand2", fg="blue")
        self.link2_label.pack(side='left')
        self.link2_label.bind("<Button-1>", lambda e: self.copy_link2())
        
        # Status bar
        capture_method = "PrintWindow API + DXCAM" if self.dxcam_camera else "PrintWindow API + Fallback"
        self.status_label = tk.Label(self.root, text=f"Ready - {capture_method} - Click Refresh to load Chrome windows", 
                                    bg='#f0f0f0', font=("Arial", 10))
        self.status_label.pack(side='bottom', pady=5)
        
        # Load Chrome windows on startup
        self.refresh_windows()
        
        # Add window validation timer
        self.window_validation_timer()
        
    def refresh_windows(self):
        """Refresh danh sách các cửa sổ Chrome"""
        try:
            chrome_windows = []
            windows = gw.getWindowsWithTitle('')
            
            for window in windows:
                if 'chrome' in window.title.lower() and window.visible:
                    chrome_windows.append(f"{window.title} (HWND: {window._hWnd})")
            
            # Update comboboxes
            self.window_combo1['values'] = chrome_windows
            self.window_combo2['values'] = chrome_windows
            
            if chrome_windows:
                self.status_label.config(text=f"Found {len(chrome_windows)} Chrome windows")
            else:
                self.status_label.config(text="No Chrome windows found - Please open Chrome first")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error refreshing windows: {str(e)}")
            self.status_label.config(text="Error refreshing windows")
    
    def window_validation_timer(self):
        """Kiểm tra định kỳ xem cửa sổ đã chọn có còn tồn tại không"""
        try:
            # Check if selected windows are still valid
            if self.selected_window1:
                if not self.is_window_valid(self.selected_window1):
                    self.selected_window1 = None
                    self.start_stream1_btn.config(state='disabled')
                    if self.streaming1:
                        self.stop_stream1()
                        
            if self.selected_window2:
                if not self.is_window_valid(self.selected_window2):
                    self.selected_window2 = None
                    self.start_stream2_btn.config(state='disabled')
                    if self.streaming2:
                        self.stop_stream2()
                        
        except Exception as e:
            print(f"Error in window validation: {e}")
        
        # Schedule next check in 2 seconds
        self.root.after(2000, self.window_validation_timer)
    
    def is_window_valid(self, window):
        """Kiểm tra xem cửa sổ có còn tồn tại và hợp lệ không"""
        try:
            # Check if window handle is still valid
            if not win32gui.IsWindow(window._hWnd):
                return False
                
            # Check if window is still visible
            if not win32gui.IsWindowVisible(window._hWnd):
                return False
                
            # Check if window title still contains 'chrome'
            title = win32gui.GetWindowText(window._hWnd)
            if 'chrome' not in title.lower():
                return False
                
            return True
            
        except Exception as e:
            print(f"Error validating window: {e}")
            return False
    
        
    def select_window(self, window_num):
        """Chọn cửa sổ Chrome từ combobox"""
        try:
            if window_num == 1:
                selected_text = self.window_var1.get()
                combo = self.window_combo1
            else:
                selected_text = self.window_var2.get()
                combo = self.window_combo2
                
            if not selected_text:
                messagebox.showwarning("Warning", f"Please select a Chrome window first!")
                return
                
            # Extract HWND from selected text
            hwnd_str = selected_text.split('(HWND: ')[1].rstrip(')')
            hwnd = int(hwnd_str)
            
            # Get window object
            window = None
            for w in gw.getWindowsWithTitle(''):
                if w._hWnd == hwnd:
                    window = w
                    break
                    
            if not window:
                messagebox.showerror("Error", "Selected window not found!")
                return
                
            # Store selected window
            if window_num == 1:
                self.selected_window1 = window
                self.start_stream1_btn.config(state='normal')
            else:
                self.selected_window2 = window
                self.start_stream2_btn.config(state='normal')
            
            self.status_label.config(text=f"Window {window_num} selected: {window.title}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting window: {str(e)}")
            self.status_label.config(text="Error selecting window")
            
            
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
            
    def toggle_quality(self):
        """Toggle between PNG (high quality) and JPEG (fast)"""
        self.use_png = not self.use_png
        if self.use_png:
            self.quality_btn.config(text="Quality: PNG")
            self.status_label.config(text="Quality set to PNG (high quality, slower)")
        else:
            self.quality_btn.config(text="Quality: JPEG")
            self.status_label.config(text="Quality set to JPEG (fast, good quality)")
            
    def capture_window(self, window):
        """Capture cửa sổ Chrome cụ thể sử dụng PrintWindow API - hoạt động ngay cả khi cửa sổ bị che"""
        try:
            hwnd = window._hWnd
            
            # Get window rectangle
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            # Check if window is valid
            if width <= 0 or height <= 0:
                return None
            
            # Method 1: Try PrintWindow API (works even if window is covered)
            try:
                img = self.capture_window_printwindow(hwnd, width, height)
                if img is not None:
                    return img
            except Exception as e:
                print(f"PrintWindow capture failed: {e}")
            
            # Method 2: Try DXCAM as fallback
            if self.dxcam_camera:
                try:
                    # Check if region is within screen bounds
                    screen_width, screen_height = pyautogui.size()
                    if (left >= 0 and top >= 0 and right <= screen_width and bottom <= screen_height and 
                        right > left and bottom > top):
                        img = self.dxcam_camera.grab(region=(left, top, right, bottom))
                        if img is not None:
                            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                            return img
                except Exception as e:
                    print(f"DXCAM capture failed: {e}")
            
            # Method 3: Fallback to pyautogui (only works if window is visible)
            try:
                screenshot = pyautogui.screenshot(region=(left, top, width, height))
                img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                return img
            except Exception as e:
                print(f"All capture methods failed: {e}")
                return None
            
        except Exception as e:
            print(f"Error capturing window: {e}")
            return None
    
    def capture_window_printwindow(self, hwnd, width, height):
        """Capture cửa sổ sử dụng PrintWindow API - hoạt động ngay cả khi cửa sổ bị che"""
        try:
            # Check if window is still valid
            if not win32gui.IsWindow(hwnd):
                return None
                
            # Load user32.dll and get PrintWindow function
            user32 = ctypes.windll.user32
            
            # Get device context of the window
            hwndDC = win32gui.GetWindowDC(hwnd)
            if not hwndDC:
                return None
                
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # Use PrintWindow to capture the window
            # PW_RENDERFULLCONTENT = 3
            result = user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
            
            if result:
                # Get bitmap data
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                
                # Convert to numpy array
                img = np.frombuffer(bmpstr, dtype='uint8')
                img.shape = (height, width, 4)  # BGRA format
                
                # Convert BGRA to BGR
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                # Clean up
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
                
                return img
            else:
                # Clean up on failure
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
                return None
                
        except Exception as e:
            print(f"PrintWindow capture error: {e}")
            return None
    
    def start_stream1(self):
        if not self.selected_window1:
            messagebox.showerror("Error", "Please select Window 1 first!")
            return
            
        self.streaming1 = True
        self.start_stream1_btn.config(text="Stop Stream 1")
        self.capture_thread1 = threading.Thread(target=self.capture_window1, daemon=True)
        self.capture_thread1.start()
        self.status_label.config(text="Stream 1 started")
        
        # Update link display
        self.link1_label.config(text="Link: http://localhost:5000/stream1")
        
    def start_stream2(self):
        if not self.selected_window2:
            messagebox.showerror("Error", "Please select Window 2 first!")
            return
            
        self.streaming2 = True
        self.start_stream2_btn.config(text="Stop Stream 2")
        self.capture_thread2 = threading.Thread(target=self.capture_window2, daemon=True)
        self.capture_thread2.start()
        self.status_label.config(text="Stream 2 started")
        
        # Update link display
        self.link2_label.config(text="Link: http://localhost:5000/stream2")
        
    def stop_stream1(self):
        self.streaming1 = False
        self.start_stream1_btn.config(text="Start Stream 1")
        self.status_label.config(text="Stream 1 stopped")
        
    def stop_stream2(self):
        self.streaming2 = False
        self.start_stream2_btn.config(text="Start Stream 2")
        self.status_label.config(text="Stream 2 stopped")
        
    def capture_window1(self):
        while self.streaming1:
            try:
                if self.selected_window1:
                    # Capture Chrome window
                    img = self.capture_window(self.selected_window1)
                    
                    if img is not None:
                        # Add to queue for streaming only
                        if not self.frame_queue1.full():
                            self.frame_queue1.put(img)
                        
            except Exception as e:
                print(f"Error capturing window 1: {e}")
                
            time.sleep(1/15)  # 15 FPS cho mượt hơn
            
    def capture_window2(self):
        while self.streaming2:
            try:
                if self.selected_window2:
                    # Capture Chrome window
                    img = self.capture_window(self.selected_window2)
                    
                    if img is not None:
                        # Add to queue for streaming only
                        if not self.frame_queue2.full():
                            self.frame_queue2.put(img)
                        
            except Exception as e:
                print(f"Error capturing window 2: {e}")
                
            time.sleep(1/15)  # 15 FPS cho mượt hơn
            
            
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
                        <h2>Chrome Window 1 Stream</h2>
                        <div id="status1" class="status offline">Offline</div>
                        <img id="stream1" src="/stream1" style="display: none;">
                    </div>
                    
                    <div class="stream-box">
                        <h2>Chrome Window 2 Stream</h2>
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
            
    def generate_frames(self, window_num):
        while True:
            try:
                frame = None
                
                # Check if streaming is active
                if window_num == 1 and self.streaming1:
                    if not self.frame_queue1.empty():
                        frame = self.frame_queue1.get()
                    else:
                        # If no frame in queue, capture directly
                        if self.selected_window1:
                            frame = self.capture_window(self.selected_window1)
                elif window_num == 2 and self.streaming2:
                    if not self.frame_queue2.empty():
                        frame = self.frame_queue2.get()
                    else:
                        # If no frame in queue, capture directly
                        if self.selected_window2:
                            frame = self.capture_window(self.selected_window2)
                
                if frame is not None:
                    # Resize frame for web streaming - tăng kích thước để rõ nét hơn
                    h, w = frame.shape[:2]
                    max_width, max_height = 1200, 900  # Tăng kích thước từ 800x600
                    
                    # Calculate scaling factor
                    scale = min(max_width/w, max_height/h)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    
                    # Sử dụng INTER_LANCZOS4 để resize chất lượng cao
                    frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
                    
                    # Encode frame based on quality setting
                    if self.use_png:
                        # PNG - chất lượng cao nhất, không nén lossy
                        ret, buffer = cv2.imencode('.png', frame)
                        content_type = b'image/png'
                    else:
                        # JPEG - nhanh hơn, chất lượng tốt
                        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        content_type = b'image/jpeg'
                    
                    frame_bytes = buffer.tobytes()
                    
                    yield (b'--frame\r\n'
                           b'Content-Type: ' + content_type + b'\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    # Send a test frame if no data
                    frame = np.zeros((200, 200, 3), dtype=np.uint8)
                    cv2.putText(frame, f"No data for window {window_num}", (10, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    frame_bytes = buffer.tobytes()
                    
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                       
            except Exception as e:
                print(f"Error generating frames for window {window_num}: {e}")
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
        else:
            self.link1_label.config(text="Link: Not available - Start stream first")
            
    def copy_link2(self):
        if self.streaming2:
            link = "http://localhost:5000/stream2"
            pyperclip.copy(link)
            self.link2_label.config(text=f"Link: {link}")
        else:
            self.link2_label.config(text="Link: Not available - Start stream first")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenStreamTool()
    app.run()
