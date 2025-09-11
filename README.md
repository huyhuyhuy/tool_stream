# Chrome Window Stream Tool

Một công cụ Python để stream cửa sổ Chrome browser và tạo livestream web real-time.

## Tính năng mới

- ✅ **Chọn cửa sổ Chrome cụ thể** thay vì vùng màn hình tùy ý
- ✅ **Tự động phát hiện** tất cả cửa sổ Chrome đang mở
- ✅ **Dropdown menu** để chọn cửa sổ muốn stream
- ✅ **Preview real-time** của cửa sổ đã chọn
- ✅ **Thông tin chi tiết** về cửa sổ (title, kích thước, vị trí)
- ✅ **Stream 2 cửa sổ Chrome** đồng thời
- ✅ **Giao diện web** để xem livestream từ xa
- ✅ **Copy link** dễ dàng với 1 click
- 🔥 **Capture cửa sổ bị che khuất** - giống OBS Studio
- 🔥 **PrintWindow API** - capture chuyên nghiệp
- 🔥 **Tự động validation** cửa sổ đã chọn

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

### Bước 1: Mở Chrome và chuẩn bị
1. Mở **Chrome browser** với các tab/cửa sổ muốn stream
2. Ví dụ: mở YouTube, Google Meet, hoặc bất kỳ trang web nào

### Bước 2: Chọn cửa sổ Chrome
1. Nhấn nút **"Refresh"** để tải danh sách cửa sổ Chrome
2. Chọn cửa sổ từ **dropdown menu** (hiển thị title của tab)
3. Nhấn **"Select Window 1"** hoặc **"Select Window 2"**
4. Preview sẽ hiển thị ảnh tĩnh của cửa sổ đã chọn

### Bước 3: Bắt đầu streaming
1. Sau khi chọn cửa sổ, nút **"Start Stream"** sẽ được kích hoạt
2. Nhấn **"Start Stream 1"** hoặc **"Start Stream 2"** để bắt đầu
3. Preview sẽ hiển thị video real-time của cửa sổ đã chọn
4. Nút sẽ chuyển thành **"Stop Stream"** để dừng

### Bước 4: Lấy link chia sẻ
1. Sau khi bắt đầu stream, nhấn nút **"Copy"** bên cạnh link
2. Link sẽ được copy vào clipboard
3. Chia sẻ link cho người khác để họ xem livestream

## Truy cập livestream

- **Chrome Window 1:** http://localhost:5000/stream1
- **Chrome Window 2:** http://localhost:5000/stream2
- **Trang chủ:** http://localhost:5000 (xem cả 2 stream)

## Ưu điểm so với phiên bản cũ

| Tính năng | Phiên bản cũ | Phiên bản mới |
|-----------|--------------|---------------|
| Chọn vùng | Kéo thả tùy ý | Chọn cửa sổ Chrome cụ thể |
| Phát hiện | Thủ công | Tự động phát hiện tất cả cửa sổ |
| Giao diện | Đơn giản | Dropdown + thông tin chi tiết |
| Độ chính xác | Có thể sai lệch | Chính xác 100% theo cửa sổ |
| Dễ sử dụng | Cần kỹ năng | Chỉ cần click chọn |
| **Capture bị che** | ❌ Không được | ✅ **Hoạt động hoàn hảo** |
| **Chất lượng** | Tùy thuộc vùng | **Luôn nét và đầy đủ** |
| **Giống OBS** | ❌ Không | ✅ **100% giống OBS Studio** |

## 🔥 Tính năng đặc biệt: Capture cửa sổ bị che khuất

**PrintWindow API** cho phép capture cửa sổ Chrome ngay cả khi:
- ✅ Cửa sổ bị che bởi ứng dụng khác
- ✅ Cửa sổ nằm dưới nền (background)
- ✅ Cửa sổ bị minimize (thu nhỏ)
- ✅ Cửa sổ bị kéo ra ngoài màn hình

**Giống hệt OBS Studio!** 🎯

## Yêu cầu hệ thống

- Python 3.7+
- Windows (sử dụng Windows API)
- Chrome browser
- Web browser để xem stream

## Thư viện sử dụng

- **tkinter**: Giao diện desktop
- **opencv-python**: Xử lý video và hình ảnh
- **flask**: Web server cho livestream
- **pygetwindow**: Quản lý cửa sổ Windows
- **pywin32**: Windows API
- **pyautogui**: Capture màn hình
- **Pillow**: Xử lý hình ảnh
- **numpy**: Xử lý dữ liệu số

## Lưu ý quan trọng

- **Chỉ hỗ trợ Chrome browser** - các trình duyệt khác sẽ không hiển thị
- **Cửa sổ phải visible** - không thể stream cửa sổ đã minimize
- **Performance tốt hơn** - chỉ capture cửa sổ cần thiết thay vì toàn màn hình
- **FPS 10fps** - tối ưu cho web streaming
- **Chất lượng tự động** - resize phù hợp với web

## Troubleshooting

**Không thấy cửa sổ Chrome:**
- Đảm bảo Chrome đang mở và visible
- Nhấn "Refresh" để tải lại danh sách
- Kiểm tra Chrome có đang chạy không

**Stream không hiển thị:**
- Kiểm tra đã chọn cửa sổ chưa
- Đảm bảo cửa sổ không bị minimize
- Refresh trang web

**Lỗi "Module not found":**
```bash
pip install -r requirements.txt
```

## Phát triển thêm

Để mở rộng tính năng:
- ✅ **Capture âm thanh** của cửa sổ Chrome
- ✅ **Hỗ trợ nhiều trình duyệt** (Firefox, Edge...)
- ✅ **Lưu cấu hình** cửa sổ đã chọn
- ✅ **Ghi âm và lưu video**
- ✅ **Authentication** cho bảo mật
- ✅ **Stream qua internet** (không chỉ localhost)