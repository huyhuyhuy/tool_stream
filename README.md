# Screen Stream Tool

Một công cụ Python để quay màn hình theo vùng được chọn và tạo livestream web real-time.

## Tính năng

- ✅ Chọn 2 vùng màn hình khác nhau bằng cách kéo thả
- ✅ Giao diện đơn giản với 2 nút Set Region và 2 nút Start Stream
- ✅ Preview trực tiếp 2 vùng đã chọn
- ✅ Tạo link web để xem livestream từ xa
- ✅ Copy link dễ dàng với 1 click
- ✅ Chạy trên localhost (port 5000)

## Cài đặt

1. **Cài đặt Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Chạy ứng dụng:**
```bash
python main.py
```

## Hướng dẫn sử dụng

### Bước 1: Chọn vùng màn hình
1. Nhấn nút **"Set Region 1"** hoặc **"Set Region 2"**
2. Cửa sổ sẽ ẩn đi và hiển thị màn hình đen với hướng dẫn
3. **Click và kéo** để chọn vùng màn hình muốn quay
4. **Nhấn ESC** để hủy bỏ
5. Vùng đã chọn sẽ hiển thị kích thước trong preview

### Bước 2: Bắt đầu streaming
1. Sau khi chọn vùng, nút **"Start Stream"** sẽ được kích hoạt
2. Nhấn **"Start Stream 1"** hoặc **"Start Stream 2"** để bắt đầu
3. Preview sẽ hiển thị video real-time của vùng đã chọn
4. Nút sẽ chuyển thành **"Stop Stream"** để dừng

### Bước 3: Lấy link chia sẻ
1. Sau khi bắt đầu stream, nhấn nút **"Copy"** bên cạnh link
2. Link sẽ được copy vào clipboard
3. Chia sẻ link cho người khác để họ xem livestream

## Truy cập livestream

- **Region 1:** http://localhost:5000/stream1
- **Region 2:** http://localhost:5000/stream2
- **Trang chủ:** http://localhost:5000 (xem cả 2 stream)

## Cấu trúc file

```
stream_tool/
├── main.py              # File chính chứa toàn bộ ứng dụng
├── requirements.txt     # Danh sách thư viện Python cần thiết
└── README.md           # Hướng dẫn sử dụng
```

## Yêu cầu hệ thống

- Python 3.7+
- Windows/macOS/Linux
- Webcam hoặc màn hình để capture

## Thư viện sử dụng

- **tkinter**: Giao diện desktop
- **opencv-python**: Xử lý video và hình ảnh
- **flask**: Web server cho livestream
- **mss**: Capture màn hình nhanh
- **pyautogui**: Chọn vùng màn hình
- **Pillow**: Xử lý hình ảnh
- **numpy**: Xử lý dữ liệu số

## Lưu ý

- Ứng dụng chạy trên localhost, chỉ có thể truy cập từ máy local
- Để chia sẻ cho người khác, cần cấu hình port forwarding hoặc deploy lên server
- Performance phụ thuộc vào kích thước vùng chọn và tốc độ mạng
- Nhấn ESC trong quá trình chọn vùng để hủy bỏ

## Troubleshooting

**Lỗi "Module not found":**
```bash
pip install -r requirements.txt
```

**Không thể chọn vùng:**
- Đảm bảo không có ứng dụng nào chặn quyền truy cập màn hình
- Thử chạy với quyền Administrator (Windows)

**Stream không hiển thị:**
- Kiểm tra xem đã bắt đầu stream chưa
- Refresh trang web
- Kiểm tra console để xem lỗi

## Phát triển thêm

Để mở rộng tính năng:
- Thêm nhiều vùng hơn (Region 3, 4...)
- Lưu cấu hình vùng đã chọn
- Thêm ghi âm và lưu video
- Cải thiện giao diện web
- Thêm authentication cho bảo mật
