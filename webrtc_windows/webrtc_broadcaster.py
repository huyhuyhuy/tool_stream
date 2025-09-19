#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# WebRTC Broadcaster for Windows
# Captures Chrome window and streams to VPS via WebRTC
# """

import asyncio
import websockets
import json
import cv2
import numpy as np
import base64
import threading
import time
import win32gui
import win32ui
import pygetwindow as gw
import ctypes
from tkinter import *
from tkinter import ttk, messagebox

class WebRTCBroadcaster:
    def __init__(self):
        # Cấu hình VPS - THAY ĐỔI IP VPS CỦA BẠN
        self.vps_ip = "45.76.190.6"  # Thay đổi IP này
        self.vps_port = 3000
        
        self.websocket = None
        self.broadcasting = False
        self.selected_window = None
        
        # Create GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Tạo giao diện người dùng"""
        self.root = Tk()
        self.root.title("🎥 WebRTC Broadcaster")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Main frame
        main_frame = Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = Label(main_frame, text="🎥 WebRTC Screen Broadcaster", 
                          font=("Arial", 18, "bold"), fg="#333")
        title_label.pack(pady=10)
        
        # VPS Info frame
        vps_frame = LabelFrame(main_frame, text="🌐 VPS Configuration", 
                              font=("Arial", 10, "bold"), padx=10, pady=10)
        vps_frame.pack(fill='x', pady=10)
        
        Label(vps_frame, text=f"VPS Server: {self.vps_ip}:{self.vps_port}", 
              font=("Arial", 10)).pack(anchor='w')
        Label(vps_frame, text=f"Public Stream: http://{self.vps_ip}:{self.vps_port}", 
              font=("Arial", 10), fg="blue").pack(anchor='w')
        
        # Chrome window selection frame
        window_frame = LabelFrame(main_frame, text="🖼️ Window Selection", 
                                 font=("Arial", 10, "bold"), padx=10, pady=10)
        window_frame.pack(fill='x', pady=10)
        
        Label(window_frame, text="Select Chrome Window:", 
              font=("Arial", 10)).pack(anchor='w', pady=(5,5))
        
        self.window_var = StringVar()
        self.window_combo = ttk.Combobox(window_frame, textvariable=self.window_var, 
                                        state='readonly', width=70, font=("Arial", 9))
        self.window_combo.pack(fill='x', pady=5)
        self.window_combo.bind('<<ComboboxSelected>>', self.select_window)
        
        # Buttons frame
        btn_frame = Frame(window_frame)
        btn_frame.pack(pady=10)
        
        self.refresh_btn = Button(btn_frame, text="🔄 Refresh Windows", 
                                 command=self.refresh_windows,
                                 font=("Arial", 10), bg="#f0f0f0")
        self.refresh_btn.pack(side='left', padx=5)
        
        self.broadcast_btn = Button(btn_frame, text="🚀 Start Broadcasting", 
                                   command=self.toggle_broadcast,
                                   font=("Arial", 10, "bold"),
                                   state='disabled', bg="#4CAF50", fg="white")
        self.broadcast_btn.pack(side='left', padx=5)
        
        # Status frame
        status_frame = LabelFrame(main_frame, text="📊 Status", 
                                 font=("Arial", 10, "bold"), padx=10, pady=10)
        status_frame.pack(fill='x', pady=10)
        
        self.status_label = Label(status_frame, text="🔵 Ready - Select a Chrome window to start", 
                                 font=("Arial", 11), fg="blue", wraplength=500)
        self.status_label.pack(pady=5)
        
        # Instructions
        instructions = """
🔧 HƯỚNG DẪN SỬ DỤNG:
1. Mở Chrome browser với tab/trang bạn muốn stream
2. Click "Refresh Windows" để tải danh sách cửa sổ Chrome
3. Chọn cửa sổ Chrome từ dropdown
4. Click "Start Broadcasting" để bắt đầu stream
5. Truy cập http://45.76.190.6:3000 để xem stream
        """
        
        instructions_label = Label(main_frame, text=instructions, 
                                  font=("Arial", 9), fg="#666", 
                                  justify='left', wraplength=550)
        instructions_label.pack(pady=10)
        
        # Load windows on start
        self.root.after(1000, self.refresh_windows)
        
    def refresh_windows(self):
        """Refresh Chrome windows list"""
        try:
            chrome_windows = []
            windows = gw.getWindowsWithTitle('')
            
            for window in windows:
                if ('chrome' in window.title.lower() and 
                    window.visible and 
                    len(window.title.strip()) > 0 and
                    window.title.strip() != 'Chrome'):
                    
                    # Truncate long titles
                    title = window.title[:60] + "..." if len(window.title) > 60 else window.title
                    chrome_windows.append(f"{title} (HWND: {window._hWnd})")
            
            self.window_combo['values'] = chrome_windows
            
            if chrome_windows:
                self.status_label.config(text=f"✅ Found {len(chrome_windows)} Chrome windows", fg="green")
            else:
                self.status_label.config(text="⚠️ No Chrome windows found - Please open Chrome browser", fg="orange")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error refreshing windows: {str(e)}")
            self.status_label.config(text="❌ Error refreshing windows", fg="red")
    
    def select_window(self, event=None):
        """Select Chrome window"""
        try:
            selected_text = self.window_var.get()
            if not selected_text:
                return
                
            # Extract HWND
            hwnd_str = selected_text.split('(HWND: ')[1].rstrip(')')
            hwnd = int(hwnd_str)
            
            # Get window object
            for w in gw.getWindowsWithTitle(''):
                if w._hWnd == hwnd:
                    self.selected_window = w
                    self.broadcast_btn.config(state='normal')
                    window_title = w.title[:50] + "..." if len(w.title) > 50 else w.title
                    self.status_label.config(text=f"🎯 Selected: {window_title}", fg="blue")
                    break
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting window: {str(e)}")
            self.status_label.config(text="❌ Error selecting window", fg="red")
    
    def capture_window(self):
        """Capture selected Chrome window using PrintWindow API"""
        if not self.selected_window:
            return None
            
        try:
            hwnd = self.selected_window._hWnd
            
            # Check if window still exists
            if not win32gui.IsWindow(hwnd):
                return None
                
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            if width <= 0 or height <= 0:
                return None
            
            # Use PrintWindow API for reliable capture
            user32 = ctypes.windll.user32
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # PW_RENDERFULLCONTENT = 3
            result = user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
            
            if result:
                bmpstr = saveBitMap.GetBitmapBits(True)
                img = np.frombuffer(bmpstr, dtype='uint8')
                img.shape = (height, width, 4)  # BGRA format
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                # Cleanup resources
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
                
                return img
            else:
                # Cleanup on failure
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
                return None
                
        except Exception as e:
            print(f"❌ Capture error: {e}")
            return None
    
    async def connect_websocket(self):
        """Connect to WebRTC signaling server"""
        try:
            uri = f"ws://{self.vps_ip}:{self.vps_port}/socket.io/?EIO=4&transport=websocket"
            print(f"🔗 Attempting to connect to: {uri}")
            
            self.websocket = await websockets.connect(uri, ping_interval=20, ping_timeout=10)
            
            # Register as broadcaster
            await self.websocket.send('40')  # Connect message
            await self.websocket.send('42["broadcaster"]')  # Register as broadcaster
            
            self.status_label.config(text="🟢 Connected to VPS - Broadcasting...", fg="green")
            print("✅ WebSocket connected successfully!")
            
            # Start capture and receive loops
            await asyncio.gather(
                self.broadcast_loop(),
                self.receive_messages()
            )
            
        except ConnectionRefusedError:
            self.status_label.config(text="❌ VPS Server is not running (Connection refused)", fg="red")
            print("❌ VPS Server is not running on port 3000. Please start the Node.js server first!")
        except Exception as e:
            self.status_label.config(text=f"❌ Connection failed: {str(e)}", fg="red")
            print(f"❌ WebSocket error: {e}")
        finally:
            # Reset broadcasting state on any error
            self.broadcasting = False
            self.broadcast_btn.config(text="🚀 Start Broadcasting", bg="#4CAF50")
            self.window_combo.config(state='readonly')
            self.refresh_btn.config(state='normal')
    
    async def receive_messages(self):
        """Receive messages from signaling server"""
        try:
            async for message in self.websocket:
                if message.startswith('42'):
                    # Parse Socket.IO message
                    try:
                        data = json.loads(message[2:])
                        if isinstance(data, list) and len(data) > 0:
                            event = data[0]
                            if event == "viewer-connected":
                                print(f"👀 Viewer connected: {data[1] if len(data) > 1 else 'Unknown'}")
                            elif event == "offer":
                                print("📨 Received WebRTC offer")
                            elif event == "answer":
                                print("📨 Received WebRTC answer")
                    except:
                        pass
        except Exception as e:
            print(f"❌ Error receiving messages: {e}")
    
    async def broadcast_loop(self):
        """Main broadcasting loop"""
        frame_count = 0
        while self.broadcasting:
            try:
                # Capture frame
                frame = self.capture_window()
                if frame is not None:
                    # Optimize frame size for streaming (smaller = faster)
                    h, w = frame.shape[:2]
                    max_width = 800  # Reduced from 1280 to 800
                    if w > max_width:
                        scale = max_width / w
                        new_w = int(w * scale)
                        new_h = int(h * scale)
                        frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)  # Faster interpolation
                    
                    # Encode to JPEG with lower quality for speed
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]  # Reduced from 85 to 60
                    _, buffer = cv2.imencode('.jpg', frame, encode_param)
                    frame_b64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Send frame via WebSocket
                    message = json.dumps({
                        "type": "video_frame",
                        "data": frame_b64,
                        "frame": frame_count,
                        "timestamp": time.time()
                    })
                    
                    if self.websocket and hasattr(self.websocket, 'closed') and not self.websocket.closed:
                        await self.websocket.send(f'42["video_frame",{message}]')
                        frame_count += 1
                        
                        # Update status every 10 frames (since we're at 5 FPS)
                        if frame_count % 10 == 0:
                            self.status_label.config(
                                text=f"🔴 LIVE - Broadcasting frame #{frame_count}", 
                                fg="red"
                            )
                else:
                    # No frame captured, window might be minimized/closed
                    if frame_count % 10 == 0:  # Check every 10 attempts
                        self.status_label.config(
                            text="⚠️ Cannot capture window - Is Chrome still open?", 
                            fg="orange"
                        )
                
                await asyncio.sleep(1/5)  # 5 FPS to reduce lag
                
            except Exception as e:
                print(f"❌ Broadcast error: {e}")
                await asyncio.sleep(1)
    
    def toggle_broadcast(self):
        """Start/stop broadcasting"""
        if not self.broadcasting:
            if not self.selected_window:
                messagebox.showerror("Error", "Please select a Chrome window first!")
                return
                
            self.broadcasting = True
            self.broadcast_btn.config(text="🛑 Stop Broadcasting", bg="#f44336")
            self.status_label.config(text="🟡 Connecting to VPS...", fg="orange")
            
            # Disable window selection while broadcasting
            self.window_combo.config(state='disabled')
            self.refresh_btn.config(state='disabled')
            
            # Start WebSocket in separate thread
            def run_websocket():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.connect_websocket())
                except Exception as e:
                    print(f"❌ WebSocket thread error: {e}")
                finally:
                    loop.close()
            
            self.websocket_thread = threading.Thread(target=run_websocket, daemon=True)
            self.websocket_thread.start()
            
        else:
            self.stop_broadcasting()
    
    def stop_broadcasting(self):
        """Stop broadcasting"""
        self.broadcasting = False
        self.broadcast_btn.config(text="🚀 Start Broadcasting", bg="#4CAF50")
        self.status_label.config(text="🔵 Broadcasting stopped", fg="blue")
        
        # Re-enable controls
        self.window_combo.config(state='readonly')
        self.refresh_btn.config(state='normal')
        
        # Close WebSocket
        if self.websocket and hasattr(self.websocket, 'closed') and not self.websocket.closed:
            try:
                asyncio.create_task(self.websocket.close())
            except Exception as e:
                print(f"❌ Error closing websocket: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        if self.broadcasting:
            self.stop_broadcasting()
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        print("🚀 WebRTC Broadcaster started")
        print(f"🌐 VPS Server: {self.vps_ip}:{self.vps_port}")
        print(f"📺 Public Stream: http://{self.vps_ip}:{self.vps_port}")
        self.root.mainloop()

if __name__ == "__main__":
    try:
        # Check if running as administrator (recommended)
        import ctypes
        if ctypes.windll.shell32.IsUserAnAdmin():
            print("✅ Running as Administrator")
        else:
            print("⚠️ Not running as Administrator - Some captures might fail")
        
        broadcaster = WebRTCBroadcaster()
        broadcaster.run()
        
    except Exception as e:
        print(f"❌ Failed to start broadcaster: {e}")
        input("Press Enter to exit...")