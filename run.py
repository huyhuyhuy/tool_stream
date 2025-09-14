#!/usr/bin/env python3
"""
Stream Tool - Launcher
Chạy file exe từ thư mục dist
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    exe_path = Path("dist/StreamTool.exe")
    
    if not exe_path.exists():
        print("❌ File StreamTool.exe không tồn tại!")
        print("   Hãy chạy: python install.py")
        sys.exit(1)
    
    print("🚀 Đang khởi động Stream Tool...")
    try:
        subprocess.run([str(exe_path)], check=True)
    except KeyboardInterrupt:
        print("\n👋 Tạm biệt!")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
