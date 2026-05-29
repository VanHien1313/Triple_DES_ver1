# Tài liệu giải thích cấu trúc project Flask Triple DES

## I. Tổng quan project

Project Flask Triple DES là một ứng dụng web demo/học thuật dùng để minh họa quá trình mã hóa và giải mã dữ liệu bằng thuật toán Triple DES. Ứng dụng cho phép người dùng thao tác trực tiếp trên giao diện web với hai loại dữ liệu chính: văn bản và tập tin.

Công nghệ chính được sử dụng gồm Python, Flask, Jinja2 template, HTML, CSS, JavaScript và pytest. Flask đảm nhiệm phần backend, routing và API xử lý dữ liệu. Jinja2, HTML, CSS và JavaScript tạo nên giao diện người dùng. Pytest được dùng để kiểm thử tự động các thành phần mã hóa và route Flask.

Người dùng có thể thực hiện các chức năng sau:

- Sinh khóa Triple DES ngẫu nhiên.
- Nhập khóa dạng hex hoặc passphrase.
- Nhập hoặc tự sinh IV cho các mode cần IV.
- Chọn chế độ mã hóa ECB, CBC hoặc CFB.
- Mã hóa và giải mã văn bản.
- Mã hóa và giải mã tập tin.
- Tải file kết quả sau khi xử lý.
- Xem IV đã dùng và thời gian xử lý.

Ứng dụng phù hợp với mục tiêu demo/học thuật vì phần DES và Triple DES được tách ra thành các module riêng, dễ đọc và dễ giải thích. Project không khẳng định an toàn tuyệt đối cho môi trường production; mục tiêu chính là giúp người học hiểu cách DES, Triple DES, các mode vận hành, khóa và IV phối hợp với nhau trong một ứng dụng web hoàn chỉnh.

## II. Cây thư mục hiện tại

Cây thư mục chính của project:

```text
Lab_Triple_DES/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── PROJECT_STRUCTURE_EXPLANATION.md
├── crypto/
│   ├── __init__.py
│   ├── des.py
│   ├── triple_des.py
│   └── modes.py
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   └── logger.py
├── templates/
│   ├── base.html
│   ├── index.html
│   └── guide.html
├── static/
│   ├── app.js
│   └── styles.css
├── tests/
│   ├── conftest.py
│   ├── test_crypto.py
│   └── test_routes.py
└── logs/
    └── .gitkeep
```

Các thư mục và file như `hien_venv/`, `venv/`, `__pycache__/`, `.pytest_cache/` và file log runtime không được liệt kê vì không phải mã nguồn chính cần đưa vào báo cáo.

## III. Giải thích chi tiết từng file/thư mục

### 1. File gốc của project

#### `app.py`

`app.py` là entry point chính của Flask app. File này khởi tạo đối tượng `Flask`, khai báo cấu hình runtime cơ bản và định nghĩa các route phục vụ giao diện/API.

Các route chính:

- `GET /`: hiển thị trang chính `templates/index.html`.
- `GET /guide`: hiển thị trang hướng dẫn `templates/guide.html`.
- `POST /api/generate-key`: sinh khóa Triple DES 24 byte và trả về dạng hex/base64.
- `POST /process-text`: nhận dữ liệu văn bản, key, IV, mode và operation để mã hóa/giải mã.
- `POST /process-file`: nhận file upload, key, IV, mode và operation để mã hóa/giải mã file.

`app.py` không trực tiếp chứa thuật toán DES/Triple DES. Thay vào đó, nó gọi:

- `utils.validators.prepare_key()` để kiểm tra và chuẩn bị khóa.
- `utils.validators.prepare_iv()` để kiểm tra và chuẩn bị IV.
- `crypto.modes.crypt_bytes()` để mã hóa/giải mã dữ liệu byte theo mode đã chọn.
- `utils.logger.log_event()` để ghi log thao tác.

`app.config["MAX_CONTENT_LENGTH"]` được dùng để giới hạn kích thước upload file, hiện tại ở mức 16MB. Nếu người dùng upload file vượt giới hạn, Flask sinh lỗi `RequestEntityTooLarge` và ứng dụng trả về JSON thân thiện với status code `413`.

Khi chạy bằng `python app.py`, chế độ debug không bị hard-code cố định. `app.py` đọc biến môi trường `FLASK_DEBUG`; nếu đặt `FLASK_DEBUG=1`, ứng dụng chạy debug mode, ngược lại debug tắt. Cách này giữ thuận tiện cho demo nhưng an toàn hơn so với luôn bật `debug=True`.

#### `requirements.txt`

`requirements.txt` liệt kê các thư viện cần cài đặt để chạy và kiểm thử project:

- `Flask==3.0.2`: framework web dùng để xây dựng backend, routing, render template và xử lý request/response.
- `pytest==8.2.2`: framework kiểm thử tự động dùng để kiểm tra các hàm crypto và route Flask.

File này giúp các thành viên trong nhóm tạo môi trường giống nhau bằng lệnh:

```bash
pip install -r requirements.txt
```

#### `README.md`

`README.md` là tài liệu hướng dẫn sử dụng project. File này mô tả tên đề tài, mục tiêu, công nghệ sử dụng, chức năng chính, cấu trúc thư mục, cách tạo môi trường ảo, cách cài dependency, cách chạy ứng dụng, cách chạy test và các lưu ý khi dùng khóa/IV/mode.

README phù hợp cho người mới clone project vì nó đưa ra các bước cần thiết để chạy ứng dụng và hiểu các thao tác chính trên giao diện.

#### `.gitignore`

`.gitignore` quy định các file/thư mục không nên đưa vào Git. Trong project này, `.gitignore` loại bỏ các thành phần như:

- Môi trường ảo: `hien_venv/`, `venv/`, `.venv/`.
- Cache Python: `__pycache__/`, `*.pyc`.
- File môi trường: `.env`, `.flaskenv`.
- Log runtime: `logs/*.log`.
- Cache/test/build artifact: `.pytest_cache/`, `.coverage`, `build/`, `dist/`.

Điều này giúp repository chỉ chứa mã nguồn và tài liệu cần thiết, tránh commit các file sinh ra khi chạy chương trình.

### 2. Thư mục `crypto/`

#### `crypto/__init__.py`

`crypto/__init__.py` đánh dấu `crypto/` là một Python package. Nhờ đó, các module khác có thể import theo dạng:

```python
from crypto.modes import crypt_bytes
```

File này không chứa logic mã hóa chính, nhưng cần thiết để tổ chức code theo package rõ ràng.

#### `crypto/des.py`

`crypto/des.py` chứa phần lõi của thuật toán DES. Đây là module cấp thấp nhất trong chuỗi mã hóa của project.

Các thành phần chính trong file:

- `BLOCK_SIZE = 8`: DES làm việc trên block 8 byte, tương ứng 64 bit.
- Các bảng hoán vị và biến đổi như `IP`, `FP`, `E`, `P`, `PC1`, `PC2`.
- `SBOXES`: các S-box dùng trong hàm Feistel để tạo tính phi tuyến.
- `SHIFT_SCHEDULE`: lịch dịch trái dùng trong quá trình sinh khóa con.
- `bytes_to_bits()` và `bits_to_bytes()`: chuyển đổi giữa byte và bit.
- `permute()`: thực hiện hoán vị bit theo bảng cho trước.
- `xor_bits()`: XOR hai dãy bit.
- `left_shift()`: dịch trái vòng cho hai nửa khóa.
- `generate_subkeys()`: sinh 16 khóa con cho 16 vòng DES.
- `s_box_substitute()`: thay thế 48 bit đầu vào thành 32 bit đầu ra qua S-box.
- `f_function()`: hàm Feistel gồm mở rộng, XOR với subkey, S-box và hoán vị P.
- `des_block()`: xử lý một block 8 byte qua 16 vòng Feistel.
- `des_encrypt_block()` và `des_decrypt_block()`: mã hóa/giải mã một block DES.

Vai trò của `crypto/des.py` là cung cấp primitive DES cơ bản. Các module cao hơn không cần biết chi tiết bảng hoán vị hay S-box; chúng chỉ gọi hàm mã hóa/giải mã block.

#### `crypto/triple_des.py`

`crypto/triple_des.py` chứa phần cài đặt Triple DES ở cấp block. File này import `des_encrypt_block()` và `des_decrypt_block()` từ `crypto/des.py`.

Triple DES trong project dùng mô hình EDE:

```text
Encrypt K1 -> Decrypt K2 -> Encrypt K3
```

Khi giải mã, quá trình được đảo ngược:

```text
Decrypt K3 -> Encrypt K2 -> Decrypt K1
```

Project hỗ trợ hai dạng khóa Triple DES thông qua module validation:

- 2-key Triple DES: khóa 16 byte được tách thành `K1`, `K2`, sau đó dùng dạng `K1, K2, K1`.
- 3-key Triple DES: khóa 24 byte được tách thành `K1`, `K2`, `K3`.

Vai trò của `crypto/triple_des.py` là ghép các thao tác DES đơn lẻ thành một thao tác Triple DES trên một block 8 byte. Khi `crypto/modes.py` cần mã hóa từng block, nó gọi các hàm trong file này.

#### `crypto/modes.py`

`crypto/modes.py` xử lý cách áp dụng Triple DES lên dữ liệu nhiều block theo các mode ECB, CBC và CFB. Đây là lớp trung gian giữa route Flask và thuật toán block cipher.

Các thành phần chính:

- `pkcs7_pad()`: thêm padding PKCS#7 để dữ liệu đủ bội số của 8 byte.
- `pkcs7_unpad()`: loại bỏ padding sau khi giải mã.
- `_xor_bytes()`: XOR hai chuỗi byte, dùng trong CBC và CFB.
- `crypt_bytes()`: hàm chính xử lý mã hóa/giải mã theo mode.

Vai trò của PKCS#7 padding/unpadding:

- DES/Triple DES xử lý block 8 byte.
- Với ECB và CBC, dữ liệu phải đủ kích thước block, nên cần padding khi mã hóa và unpadding khi giải mã.
- Nếu padding không hợp lệ, hệ thống raise `ValidationError`.

ECB xử lý như sau:

- Chia dữ liệu thành các block 8 byte.
- Mỗi block được mã hóa độc lập bằng Triple DES.
- Không dùng IV.
- Không khuyến nghị cho dữ liệu có mẫu lặp vì các block giống nhau có thể tạo ra ciphertext giống nhau.

CBC xử lý như sau:

- Cần IV 8 byte cho block đầu tiên.
- Trước khi mã hóa, mỗi plaintext block được XOR với ciphertext block trước đó.
- Block đầu tiên XOR với IV.
- Khi giải mã, kết quả giải mã block được XOR lại với ciphertext block trước đó hoặc IV.
- CBC cần padding vì dữ liệu phải đủ bội số block.

CFB xử lý như sau:

- Cần IV 8 byte.
- IV hoặc ciphertext block trước đó được mã hóa để tạo keystream.
- Plaintext/ciphertext được XOR với keystream để tạo kết quả.
- CFB trong project có thể xử lý block cuối không đủ 8 byte, nên không cần padding.

### 3. Thư mục `utils/`

#### `utils/__init__.py`

`utils/__init__.py` đánh dấu `utils/` là Python package. Nhờ đó, các module có thể import helper theo dạng:

```python
from utils.validators import prepare_key
```

#### `utils/validators.py`

`utils/validators.py` chịu trách nhiệm kiểm tra và chuẩn bị dữ liệu đầu vào liên quan đến khóa và IV.

Các chức năng chính:

- `ValidationError`: exception tùy chỉnh dùng để báo lỗi validation cho route Flask.
- `is_hex_string()`: kiểm tra chuỗi có phải hex hợp lệ hay không.
- `prepare_key()`: chuẩn bị khóa Triple DES.
- `prepare_iv()`: chuẩn bị IV cho các mode cần IV.

Cách xử lý khóa:

- Nếu người dùng nhập chuỗi hex 32 ký tự, hệ thống chuyển thành 16 byte và dùng dạng 2-key Triple DES: `K1, K2, K1`.
- Nếu người dùng nhập chuỗi hex 48 ký tự, hệ thống chuyển thành 24 byte và dùng dạng 3-key Triple DES: `K1, K2, K3`.
- Nếu người dùng nhập chuỗi không phải hex, hệ thống xem đó là passphrase, băm bằng SHA-256 và lấy 24 byte đầu làm khóa Triple DES.

Cách xử lý IV:

- Với ECB, IV không cần dùng nên trả về `None`.
- Với CBC và CFB, IV phải dài 8 byte, tương ứng 16 ký tự hex.
- Khi mã hóa CBC/CFB mà người dùng để trống IV, hệ thống tự sinh IV bằng `os.urandom(8)`.
- Khi giải mã CBC/CFB, người dùng bắt buộc phải nhập đúng IV đã dùng khi mã hóa.

`ValidationError` giúp tách lỗi đầu vào khỏi các lỗi xử lý khác. Route Flask bắt exception này và trả JSON lỗi thân thiện cho frontend.

#### `utils/logger.py`

`utils/logger.py` chịu trách nhiệm ghi log thao tác vào `logs/operations.log`.

Mỗi dòng log gồm các thông tin:

- Thời điểm xử lý.
- Loại dữ liệu: `text` hoặc `file`.
- Thao tác: `encrypt` hoặc `decrypt`.
- Mode: `ECB`, `CBC` hoặc `CFB`.
- Kích thước dữ liệu đầu vào.
- Thời gian xử lý tính bằng millisecond.

Logging hữu ích trong demo và kiểm tra hệ thống vì nhóm có thể quan sát ứng dụng đã xử lý thao tác nào, dữ liệu có kích thước bao nhiêu và thời gian xử lý ra sao. File log không chứa key hoặc plaintext, nhưng vẫn là dữ liệu runtime nên không nên commit lên Git.

### 4. Thư mục `templates/`

#### `templates/base.html`

`base.html` là layout chung cho các trang. File này định nghĩa cấu trúc HTML cơ bản gồm:

- Phần `<head>` với charset, viewport, title, link CSS và script JS.
- Header chứa thương hiệu `Triple DES Vault`.
- Navigation đến trang chính và trang hướng dẫn.
- Khối `{% block content %}` để các template con chèn nội dung riêng.
- Footer hiển thị tên ứng dụng và năm hiện tại.

`base.html` giúp tránh lặp lại header/footer/script/style ở nhiều trang.

#### `templates/index.html`

`index.html` là giao diện chính của ứng dụng. File này extend `base.html` và chứa các khu vực chính:

- Hero giới thiệu ngắn về Triple DES và các mode hỗ trợ.
- Panel thiết lập khóa, mode và IV.
- Panel xử lý file.
- Panel xử lý văn bản.

Các form trên giao diện không tự xử lý mã hóa. JavaScript trong `static/app.js` đọc dữ liệu từ form và gửi request đến backend:

- Sinh khóa: gọi `POST /api/generate-key`.
- Xử lý văn bản: gọi `POST /process-text`.
- Xử lý file: gọi `POST /process-file`.

Giao diện cũng hiển thị hint về khóa 2-key/3-key/passphrase, cảnh báo ECB, IV đã dùng, thời gian xử lý và kết quả mã hóa/giải mã.

#### `templates/guide.html`

`guide.html` là trang hướng dẫn sử dụng. Nội dung chính gồm:

- Các bước chọn mode, nhập khóa, nhập IV và xử lý dữ liệu.
- Lưu ý bảo mật cơ bản: lưu IV, không chia sẻ khóa qua kênh không an toàn, Triple DES phù hợp học tập hoặc hệ thống cũ.
- Mục định dạng khóa Triple DES, giải thích 2-key và 3-key.
- Mục định dạng kết quả văn bản, giải thích ciphertext text được trả về dạng Base64.

Trang này giúp người dùng hiểu thao tác cần thiết trước khi sử dụng chức năng mã hóa/giải mã.

### 5. Thư mục `static/`

#### `static/app.js`

`app.js` xử lý tương tác frontend. Các nhiệm vụ chính:

- Cập nhật hint theo mode đang chọn.
- Hiển thị cảnh báo rõ hơn khi chọn ECB.
- Ẩn/hiện trường IV khi chọn ECB hoặc CBC/CFB.
- Sinh IV ngẫu nhiên phía client bằng Web Crypto API.
- Gọi API sinh khóa `/api/generate-key`.
- Hiển thị hint động cho khóa:
  - 32 ký tự hex: 2-key Triple DES.
  - 48 ký tự hex: 3-key Triple DES.
  - Passphrase: dẫn xuất bằng SHA-256.
- Gửi form text đến `/process-text` bằng Fetch API.
- Gửi form file đến `/process-file` bằng Fetch API.
- Nhận kết quả, IV, thời gian xử lý và hiển thị lên giao diện.
- Hỗ trợ sao chép khóa, IV và kết quả text.

File này không thực hiện thuật toán DES/Triple DES. Nó chỉ điều phối giao diện và gọi API Flask.

#### `static/styles.css`

`styles.css` định dạng giao diện của ứng dụng. File này quy định:

- Bảng màu nền tối.
- Header, navigation, footer.
- Layout hero và grid panel.
- Form input, select, textarea.
- Button chính, button phụ, chip radio.
- Vùng kết quả, metadata, hint, cảnh báo.
- Responsive layout cho màn hình nhỏ.

Vai trò của file này là giúp giao diện demo rõ ràng, dễ thao tác và phù hợp trình bày đồ án.

### 6. Thư mục `tests/`

#### `tests/conftest.py`

`conftest.py` cấu hình môi trường test cho pytest. File này thêm project root vào `sys.path`, giúp test import được các module như `app.py`, `crypto/` và `utils/` ổn định hơn khi chạy bằng:

```bash
python -m pytest -q
```

hoặc:

```bash
pytest
```

#### `tests/test_crypto.py`

`test_crypto.py` kiểm thử các thành phần crypto cơ bản:

- PKCS#7 padding/unpadding với dữ liệu chưa đủ block.
- PKCS#7 padding khi dữ liệu đã đủ block.
- Trường hợp padding không hợp lệ.
- Triple DES encrypt rồi decrypt một block phải trả về block ban đầu.
- Round-trip cho các mode ECB, CBC và CFB: mã hóa rồi giải mã phải trả về dữ liệu ban đầu.

Các test này giúp phát hiện lỗi khi thay đổi module `crypto/`.

#### `tests/test_routes.py`

`test_routes.py` kiểm thử các route Flask quan trọng:

- `/api/generate-key`: kiểm tra route trả về khóa hex 48 ký tự và base64 decode đúng.
- `/process-text`: kiểm tra mã hóa CBC rồi giải mã ra lại plaintext ban đầu.
- `/process-file`: kiểm tra trường hợp upload vượt giới hạn trả về JSON lỗi với status `413`.

Trong test, logger được monkeypatch để không ghi log runtime khi chạy kiểm thử.

### 7. Thư mục `logs/`

#### `logs/.gitkeep`

`logs/.gitkeep` là file rỗng dùng để giữ thư mục `logs/` trong Git. Git không theo dõi thư mục rỗng, nên cần `.gitkeep` để đảm bảo khi clone project, thư mục `logs/` vẫn tồn tại.

#### `logs/operations.log`

`logs/operations.log` là file runtime được sinh ra khi ứng dụng chạy và ghi log thao tác. File này có thể thay đổi liên tục theo quá trình sử dụng ứng dụng.

Không nên commit file log thật lên Git vì:

- Nội dung log là dữ liệu runtime, không phải mã nguồn.
- File log thay đổi thường xuyên, gây nhiễu lịch sử commit.
- Log có thể chứa thông tin vận hành không cần chia sẻ trong repository.

## IV. Luồng hoạt động tổng quát của hệ thống

### Luồng xử lý mã hóa/giải mã văn bản

1. Người dùng nhập văn bản, chọn mode, nhập key và IV trên giao diện chính.
2. `static/app.js` thu thập dữ liệu form và gửi request đến route `/process-text`.
3. `app.py` nhận request, kiểm tra operation và lấy các field cần thiết.
4. `app.py` gọi `utils.validators.prepare_key()` để chuẩn bị khóa.
5. `app.py` gọi `utils.validators.prepare_iv()` để chuẩn bị IV nếu mode cần IV.
6. `app.py` chuyển plaintext/ciphertext thành bytes phù hợp.
7. `app.py` gọi `crypto.modes.crypt_bytes()`.
8. `crypto/modes.py` xử lý mode ECB/CBC/CFB, padding nếu cần.
9. `crypto/modes.py` gọi `crypto.triple_des.py` để xử lý từng block bằng Triple DES.
10. `crypto/triple_des.py` gọi `crypto.des.py` để mã hóa/giải mã DES cấp block.
11. Kết quả được trả về `app.py`, sau đó trả JSON cho frontend.
12. `static/app.js` hiển thị kết quả, IV đã dùng và thời gian xử lý.
13. `utils.logger.log_event()` ghi log thao tác.

### Luồng xử lý mã hóa/giải mã file

1. Người dùng chọn file trên giao diện.
2. `static/app.js` gửi file cùng key, IV, mode và operation đến route `/process-file`.
3. `app.py` kiểm tra operation, file upload, tên file, key và IV.
4. Backend đọc nội dung file dưới dạng bytes.
5. `app.py` gọi `crypto.modes.crypt_bytes()` để mã hóa/giải mã dữ liệu bằng Triple DES theo mode đã chọn.
6. `crypto/modes.py` gọi `crypto.triple_des.py`, và `crypto.triple_des.py` gọi `crypto.des.py`.
7. `app.py` đóng gói dữ liệu kết quả vào response download.
8. Frontend nhận file kết quả và hiển thị link tải xuống.
9. `utils.logger.log_event()` ghi log thao tác.

## V. Sơ đồ phụ thuộc giữa các file

Sơ đồ phụ thuộc backend chính:

```text
app.py
├── utils/validators.py
├── utils/logger.py
└── crypto/modes.py
    └── crypto/triple_des.py
        └── crypto/des.py
```

Sơ đồ frontend:

```text
templates/base.html
├── templates/index.html
│   └── static/app.js
│       └── gọi API Flask trong app.py
└── templates/guide.html

static/styles.css
└── định dạng giao diện cho các template
```

Sơ đồ test:

```text
tests/conftest.py
├── cấu hình import project root
├── tests/test_crypto.py
│   └── kiểm thử crypto/modes.py, crypto/triple_des.py, utils/validators.py
└── tests/test_routes.py
    └── kiểm thử Flask routes trong app.py
```

## VI. Đánh giá tổ chức project hiện tại

Ưu điểm:

- Code được tách theo trách nhiệm rõ ràng: Flask route, crypto core, validation, logging, frontend và test.
- Thuật toán DES nằm riêng trong `crypto/des.py`, giúp dễ giải thích từng bước của DES.
- Triple DES nằm riêng trong `crypto/triple_des.py`, giúp làm rõ mô hình EDE.
- Các mode ECB/CBC/CFB nằm trong `crypto/modes.py`, giúp phân biệt thuật toán block cipher và cách vận hành trên dữ liệu nhiều block.
- Validation và logging được tách khỏi route Flask, làm `app.py` gọn hơn.
- Có test tự động cơ bản cho crypto và route, hỗ trợ kiểm tra sau refactor.

So với việc để toàn bộ trong `app.py`, cách tách module hiện tại tốt hơn vì:

- Dễ đọc và dễ bảo trì hơn.
- Dễ phân công thành viên trong nhóm phụ trách từng phần.
- Dễ viết test cho từng lớp logic.
- Dễ trình bày trong báo cáo vì mỗi module có vai trò rõ ràng.

Điểm phù hợp với đồ án/demo:

- Cấu trúc đủ đơn giản để sinh viên giải thích được.
- Có giao diện web trực quan để demo mã hóa/giải mã.
- Có module crypto tự cài đặt để minh họa DES/Triple DES.
- Có hướng dẫn và test cơ bản để hỗ trợ chạy lại project.

Một số hạn chế còn lại:

- Bộ test mới ở mức cơ bản, chưa bao phủ đầy đủ test vector chuẩn của DES/Triple DES.
- Chưa có cơ chế xác thực người dùng.
- Chưa có quản lý khóa an toàn; người dùng phải tự lưu key và IV.
- Triple DES là thuật toán cũ, không nên xem là lựa chọn mặc định cho hệ thống mới.
- Cấu hình runtime mới ở mức demo/lab, chưa phải cấu hình production hoàn chỉnh.

Hướng phát triển nếu có thêm thời gian:

- Bổ sung test vector chuẩn cho DES và Triple DES.
- Cho phép cấu hình giới hạn upload qua biến môi trường.
- Thêm blueprint nếu API và giao diện mở rộng nhiều hơn.
- Thêm Dockerfile để triển khai demo dễ hơn.
- Bổ sung cơ chế xuất metadata gồm mode, IV và thời gian xử lý.
- Nghiên cứu thêm AES-GCM hoặc các cơ chế mã hóa có xác thực để so sánh với Triple DES.

## VII. Đoạn tóm tắt ngắn để đưa vào báo cáo

Project được tổ chức theo kiến trúc Flask đơn giản, trong đó `app.py` đóng vai trò entry point và xử lý các route chính của ứng dụng. Phần thuật toán được tách riêng vào thư mục `crypto/`, gồm DES cấp block, Triple DES theo mô hình EDE và các mode ECB, CBC, CFB. Các chức năng hỗ trợ như kiểm tra khóa, kiểm tra IV và ghi log được đặt trong thư mục `utils/`. Giao diện người dùng được xây dựng bằng Jinja2 template trong `templates/` và JavaScript/CSS trong `static/`.

Cách tổ chức này giúp mã nguồn rõ ràng, dễ theo dõi và phù hợp với mục tiêu học thuật của đồ án. Ứng dụng có thể minh họa đầy đủ luồng mã hóa/giải mã văn bản và tập tin bằng Triple DES, đồng thời vẫn giữ từng thành phần đủ tách biệt để nhóm có thể giải thích, kiểm thử và mở rộng trong quá trình trình bày demo.
