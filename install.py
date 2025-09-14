#!/usr/bin/env python3
"""
Stream Tool - Auto Installer
Tự động cài đặt dependencies và build file exe
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(command, description):
    """Chạy lệnh và hiển thị tiến trình"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Hoàn thành!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Lỗi: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🚀 Stream Tool - Auto Installer")
    print("=" * 50)
    
    # Kiểm tra Python version
    if sys.version_info < (3, 8):
        print("❌ Cần Python 3.8 trở lên!")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    
    # Cài đặt dependencies
    if not run_command("pip install -r requirements.txt", "Cài đặt dependencies"):
        print("❌ Không thể cài đặt dependencies!")
        sys.exit(1)
    
    # Xóa thư mục build và dist cũ (nếu có)
    print("🧹 Dọn dẹp thư mục build cũ...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   Đã xóa thư mục {folder}")
    
    # Xóa file .spec cũ
    for spec_file in ['main.spec', 'StreamTool.spec', 'stream_tool.spec']:
        if os.path.exists(spec_file):
            os.remove(spec_file)
            print(f"   Đã xóa file {spec_file}")
    
    # Build exe với PyInstaller
    print("🔨 Bắt đầu build file exe...")
    build_command = [
        "python", "-m", "PyInstaller",
        "--onefile",                    # Tạo file exe duy nhất
        "--windowed",                   # Ẩn console window
        "--name", "StreamTool",         # Tên file exe
        "--clean",                      # Dọn dẹp cache
        "main.py"
    ]
    
    if not run_command(" ".join(build_command), "Build file exe"):
        print("❌ Không thể build file exe!")
        sys.exit(1)
    
    # Kiểm tra file exe đã được tạo
    exe_path = Path("dist/StreamTool.exe")
    if exe_path.exists():
        file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ File exe đã được tạo thành công!")
        print(f"   📁 Vị trí: {exe_path.absolute()}")
        print(f"   📏 Kích thước: {file_size:.1f} MB")
        
        # Tạo shortcut script
        create_shortcut_script()
        
        print("\n🎉 HOÀN THÀNH!")
        print("=" * 50)
        print("📋 Hướng dẫn sử dụng:")
        print("   1. Chạy file: dist/StreamTool.exe")
        print("   2. Hoặc chạy: python run.py")
        print("   3. Chọn cửa sổ Chrome muốn stream")
        print("   4. Truy cập: http://localhost:5000")
        
    else:
        print("❌ File exe không được tạo!")
        sys.exit(1)

def create_shortcut_script():
    """Tạo file run.py để chạy exe dễ dàng"""
    run_script = '''#!/usr/bin/env python3
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
        print("\\n👋 Tạm biệt!")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
'''
    
    with open("run.py", "w", encoding="utf-8") as f:
        f.write(run_script)
    
    print("   📝 Đã tạo file run.py")

if __name__ == "__main__":
    main()
