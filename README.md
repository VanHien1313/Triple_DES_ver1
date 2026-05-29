# Triple DES Web App

## Tên đề tài

Xây dựng ứng dụng web mã hóa và giải mã văn bản, tập tin bằng thuật toán Triple DES.

## Mục tiêu project

Project này là một ứng dụng Flask phục vụ mục đích học tập và thực hành mã hóa đối xứng. Ứng dụng cho phép người dùng nhập khóa, chọn chế độ mã hóa, nhập IV khi cần, sau đó mã hóa hoặc giải mã dữ liệu text và file bằng Triple DES.

## Công nghệ sử dụng

- Python 3
- Flask 3.0.2
- Jinja2 template
- HTML, CSS, JavaScript
- Web Crypto API trên trình duyệt để sinh IV ngẫu nhiên phía client

Lưu ý: phần DES/Triple DES trong project được tự implement trong thư mục `crypto/`, không gọi thư viện mã hóa bên ngoài cho logic mã hóa chính.

## Chức năng chính

- Mã hóa và giải mã văn bản.
- Mã hóa và giải mã tập tin upload.
- Hỗ trợ các chế độ ECB, CBC và CFB.
- Hỗ trợ khóa hex 16 byte hoặc 24 byte.
- Hỗ trợ passphrase; backend sẽ dẫn xuất khóa bằng SHA-256 và lấy 24 byte đầu.
- Tự sinh khóa Triple DES 24 byte.
- Tự sinh IV 8 byte cho CBC/CFB khi mã hóa nếu người dùng để trống.
- Hiển thị hint định dạng khóa 2-key/3-key/passphrase và hỗ trợ sao chép khóa, IV, kết quả text.
- Hiển thị IV đã dùng và thời gian xử lý.
- Ghi log thao tác vào `logs/operations.log`.
- Giới hạn upload file mặc định 16MB cho môi trường demo/lab.

## Cấu trúc thư mục

```text
Lab_Triple_DES/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── base.html
│   ├── index.html
│   └── guide.html
├── static/
│   ├── app.js
│   └── styles.css
├── crypto/
│   ├── __init__.py
│   ├── des.py
│   ├── triple_des.py
│   └── modes.py
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   └── logger.py
└── logs/
    └── .gitkeep
```

Mô tả nhanh:

- `app.py`: entry point Flask, khai báo routes và điều phối request/response.
- `crypto/des.py`: thuật toán DES cấp block, gồm bảng hoán vị, S-box và sinh subkey.
- `crypto/triple_des.py`: thuật toán Triple DES theo mô hình EDE.
- `crypto/modes.py`: xử lý các chế độ ECB, CBC, CFB và padding PKCS#7.
- `utils/validators.py`: kiểm tra và chuẩn bị khóa, IV.
- `utils/logger.py`: ghi log thao tác vào thư mục `logs/`.
- `templates/base.html`: layout dùng chung cho các trang.
- `templates/index.html`: giao diện chính để mã hóa/giải mã text và file.
- `templates/guide.html`: trang hướng dẫn sử dụng.
- `static/app.js`: xử lý tương tác UI, submit form qua Fetch API, hiển thị kết quả.
- `static/styles.css`: style giao diện.
- `logs/.gitkeep`: giữ thư mục `logs/` trong Git.
- `logs/*.log`: file log runtime, không nên commit.

## Hướng dẫn tạo môi trường ảo

Trên Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Nếu dùng Command Prompt:

```bat
python -m venv venv
venv\Scripts\activate.bat
```

Trên macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

## Hướng dẫn cài dependencies

Sau khi kích hoạt môi trường ảo, cài dependencies:

```bash
pip install -r requirements.txt
```

## Hướng dẫn chạy ứng dụng

Chạy trực tiếp bằng Python:

```bash
python app.py
```

Mặc định Flask sẽ chạy ở địa chỉ:

```text
http://127.0.0.1:5000
```

Mở trình duyệt và truy cập địa chỉ trên để sử dụng ứng dụng.

### Bật/tắt debug

Khi chạy bằng `python app.py`, chế độ debug mặc định tắt. Để bật debug trong môi trường demo/lab, đặt biến môi trường `FLASK_DEBUG=1` trước khi chạy.

Trên Windows PowerShell:

```powershell
$env:FLASK_DEBUG="1"
python app.py
```

Để tắt debug:

```powershell
$env:FLASK_DEBUG="0"
python app.py
```

Trên macOS/Linux:

```bash
FLASK_DEBUG=1 python app.py
```

## Hướng dẫn chạy test

Project dùng `pytest` cho bộ test tự động. Sau khi cài dependencies, chạy test bằng:

```bash
python -m pytest -q
```

Khuyến nghị dùng `python -m pytest -q` để đảm bảo pytest chạy đúng theo Python/môi trường ảo hiện tại. Project cũng có `tests/conftest.py` để thêm project root vào `sys.path`, giúp lệnh `pytest` trực tiếp import được `app.py`, `crypto/` và `utils/` ổn định hơn.

## Hướng dẫn sử dụng mã hóa/giải mã text

### Mã hóa text

1. Mở trang chính của ứng dụng.
2. Chọn chế độ mã hóa: nên dùng `CBC` cho hầu hết trường hợp.
3. Nhập khóa:
   - Hex 32 ký tự cho khóa 16 byte.
   - Hex 48 ký tự cho khóa 24 byte.
   - Hoặc nhập passphrase bất kỳ để hệ thống dẫn xuất khóa.
4. Nhập IV nếu dùng `CBC` hoặc `CFB`; có thể để trống khi mã hóa để hệ thống tự sinh.
5. Nhập nội dung cần mã hóa vào ô văn bản.
6. Chọn thao tác `Mã hóa`.
7. Bấm `Xử lý văn bản`.
8. Lưu lại kết quả Base64 và IV đã hiển thị nếu có.

### Giải mã text

1. Dán chuỗi Base64 đã mã hóa vào ô văn bản.
2. Chọn đúng chế độ đã dùng khi mã hóa.
3. Nhập đúng khóa ban đầu.
4. Nếu dùng `CBC` hoặc `CFB`, nhập đúng IV đã được sinh/lưu khi mã hóa.
5. Chọn thao tác `Giải mã`.
6. Bấm `Xử lý văn bản`.

## Hướng dẫn sử dụng mã hóa/giải mã file

### Mã hóa file

1. Chọn chế độ mã hóa.
2. Nhập khóa hoặc bấm `Tạo khóa ngẫu nhiên`.
3. Nhập IV nếu cần, hoặc để trống với `CBC`/`CFB` để hệ thống tự sinh.
4. Chọn file cần mã hóa. Kích thước file upload tối đa mặc định là 16MB.
5. Chọn thao tác `Mã hóa`.
6. Bấm `Xử lý tập tin`.
7. Tải file kết quả có đuôi `.des3`.
8. Lưu lại khóa và IV để có thể giải mã sau này.

### Giải mã file

1. Chọn file đã mã hóa.
2. Chọn đúng chế độ đã dùng khi mã hóa.
3. Nhập đúng khóa.
4. Nhập đúng IV nếu file được mã hóa bằng `CBC` hoặc `CFB`.
5. Chọn thao tác `Giải mã`.
6. Bấm `Xử lý tập tin`.
7. Tải file kết quả có đuôi `.dec`.

## Lưu ý về khóa, IV, ECB, CBC, CFB

- Triple DES làm việc với block 8 byte.
- Khóa hex 16 byte sẽ được xử lý theo dạng 2-key Triple DES: `K1, K2, K1`.
- Khóa hex 24 byte sẽ được xử lý theo dạng 3-key Triple DES: `K1, K2, K3`.
- Nếu nhập passphrase, project dùng SHA-256 để tạo digest và lấy 24 byte đầu làm khóa.
- IV phải dài 8 byte, tương đương 16 ký tự hex.
- `CBC` cần IV và có padding PKCS#7; phù hợp hơn `ECB` cho dữ liệu có nhiều block.
- `CFB` cần IV và không cần padding; phù hợp dữ liệu dạng luồng.
- `ECB` không cần IV nhưng có thể làm lộ mẫu dữ liệu lặp lại, không nên dùng cho dữ liệu nhạy cảm.
- Khi giải mã, cần dùng đúng khóa, IV và chế độ mã hóa ban đầu.

## Hạn chế hiện tại

- Bộ test hiện tại mới ở mức cơ bản, chưa bao phủ đầy đủ test vector chuẩn DES/Triple DES và các trường hợp lỗi phức tạp.
- Giới hạn upload mặc định là 16MB và chưa có cấu hình động trên giao diện.
- Chưa có cơ chế xác thực người dùng.
- Chưa có quản lý khóa an toàn; người dùng phải tự bảo quản khóa và IV.
- Ứng dụng đang phù hợp cho học tập/lab, chưa phải cấu hình production.
- Triple DES là thuật toán cũ; hệ thống mới nên ưu tiên AES hoặc các cơ chế mã hóa hiện đại hơn.

## Hướng phát triển

- Tách thêm route Flask thành blueprint nếu project mở rộng nhiều trang/API hơn.
- Thêm unit test với test vector DES/Triple DES chuẩn.
- Cho phép cấu hình giới hạn upload bằng biến môi trường hoặc file cấu hình riêng.
- Thêm cấu hình production bằng biến môi trường.
- Bổ sung Dockerfile hoặc script khởi chạy nhanh.
- Bổ sung tùy chọn xuất metadata gồm mode, IV và thời gian mã hóa.
- Nghiên cứu thêm AES-GCM hoặc các chế độ mã hóa có xác thực.
