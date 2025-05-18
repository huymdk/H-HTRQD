Dọn dẹp thư mục dự án:
Xóa thư mục môi trường ảo venv/ (hoặc .venv/) khỏi thư mục dự án của bạn.
Xóa các thư mục __pycache__/ (nếu có).
Kiểm tra lại file .gitignore để đảm bảo nó bao gồm venv/ và __pycache__/.
Tạo file requirements.txt:
Mở terminal/command prompt trong thư mục dự án của bạn (đã kích hoạt môi trường ảo venv của bạn).
Chạy lệnh:
pip freeze > requirements.txt
Use code with caution.
Bash
Lệnh này sẽ liệt kê tất cả các thư viện Python bạn đã cài đặt trong môi trường ảo (bao gồm Flask, PyMySQL, numpy, openpyxl) và phiên bản của chúng vào file requirements.txt.
Viết file Hướng Dẫn Chi Tiết (ví dụ: README.md hoặc INSTRUCTIONS.txt):
File này cực kỳ quan trọng. Nội dung nên bao gồm:

# Hướng Dẫn Chạy Demo Ứng Dụng Web Hỗ Trợ Quyết Định AHP

Ứng dụng này giúp thực hiện phân tích AHP để hỗ trợ quyết định mua đồ điện tử.

## Yêu Cầu Hệ Thống:

*   Python 3.8 trở lên (Khuyến nghị sử dụng cùng phiên bản Python mà dự án được phát triển nếu có thể).
*   XAMPP (đã cài đặt và chạy module Apache & MySQL).
*   Trình duyệt web (Chrome, Firefox, Edge,...).
*   Git (Tùy chọn, nếu bạn chia sẻ qua Git repository).

## Các Bước Cài Đặt và Chạy Ứng Dụng:

1.  **Tải hoặc Clone Dự Án:**
    *   Nếu nhận được file .zip, hãy giải nén vào một thư mục trên máy của bạn.
    *   Nếu dự án được chia sẻ qua Git, hãy clone repository: `git clone <URL_CUA_REPOSITORY>`

2.  **Cài Đặt và Cấu Hình XAMPP (MySQL/MariaDB):**
    *   Tải và cài đặt XAMPP từ [https://www.apachefriends.org/index.html](https://www.apachefriends.org/index.html) nếu chưa có.
    *   Mở **XAMPP Control Panel**.
    *   Nhấn nút **Start** cho module **Apache** và module **MySQL**.
    *   Nhấp vào nút **Admin** bên cạnh module MySQL để mở **phpMyAdmin** trong trình duyệt.
    *   **Tạo Database:**
        *   Trong phpMyAdmin, nhấp vào tab "Databases".
        *   Trong ô "Create database", nhập tên là `ahp_db`.
        *   Chọn Collation là `utf8mb4_unicode_ci`.
        *   Nhấp "Create".
    *   **Tạo Bảng:**
        *   Chọn database `ahp_db` vừa tạo từ danh sách bên trái.
        *   Nhấp vào tab "SQL".
        *   Copy và dán toàn bộ đoạn mã SQL sau vào ô lệnh, sau đó nhấp "Go":
            ```sql
            -- Dán toàn bộ nội dung SQL CREATE TABLE và ALTER TABLE mà bạn đã dùng để tạo CSDL vào đây
            -- (Bao gồm CREATE TABLE decisions, criteria, alternatives, alternative_scores)
            -- (Và ALTER TABLE decisions ADD COLUMN criteria_cr FLOAT DEFAULT NULL;)
            -- (Và ALTER TABLE decisions ADD COLUMN criteria_comparison_json TEXT DEFAULT NULL;)
            ```
        *   Đảm bảo tất cả các bảng được tạo thành công.

3.  **Thiết Lập Môi Trường Python:**
    *   Mở Terminal (Command Prompt, PowerShell, Git Bash, hoặc Terminal của VS Code) trong thư mục gốc của dự án (thư mục bạn vừa giải nén hoặc clone).
    *   **Tạo môi trường ảo:**
        ```bash
        python -m venv venv
        ```
    *   **Kích hoạt môi trường ảo:**
        *   **Windows (PowerShell/CMD):**
          ```powershell
          .\venv\Scripts\activate
          ```
          *(Lưu ý: Nếu dùng PowerShell và gặp lỗi Execution Policy, mở PowerShell với quyền Administrator và chạy: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`, sau đó thử lại.)*
        *   **macOS/Linux (Bash/Zsh):**
          ```bash
          source venv/bin/activate
          ```
        *   Bạn sẽ thấy `(venv)` xuất hiện ở đầu dòng lệnh.
    *   **Cài đặt các thư viện cần thiết:**
        ```bash
        pip install -r requirements.txt
        ```

4.  **Kiểm Tra Cấu Hình Kết Nối CSDL:**
    *   Mở file `db_manager.py` trong dự án.
    *   Kiểm tra biến `DB_CONFIG` ở đầu file. Đảm bảo các thông tin sau là đúng với cài đặt XAMPP của bạn:
        ```python
        DB_CONFIG = {
            'host': 'localhost',
            'user': 'root',
            'password': '',  # Mật khẩu rỗng cho root XAMPP mặc định
            'database': 'ahp_db',
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        ```
        Nếu bạn đã đặt mật khẩu cho user `root` trong XAMPP, hãy thay đổi giá trị `password` cho phù hợp.

5.  **Chạy Ứng Dụng Web:**
    *   Trong Terminal (đã kích hoạt `venv` và đang ở thư mục gốc của dự án), chạy lệnh:
        ```bash
        python app.py
        ```
    *   Bạn sẽ thấy các thông báo từ server Flask, bao gồm các địa chỉ mà ứng dụng đang chạy (ví dụ: `http://127.0.0.1:5000/`).

6.  **Truy Cập Ứng Dụng:**
    *   Mở trình duyệt web.
    *   Truy cập địa chỉ: `http://localhost:5000` hoặc `http://127.0.0.1:5000`.
    *   Bạn sẽ thấy giao diện của ứng dụng AHP.

## Gỡ Lỗi Cơ Bản:

*   **Không kết nối được CSDL:**
    *   Kiểm tra xem XAMPP (MySQL) có đang chạy không.
    *   Kiểm tra lại thông tin trong `DB_CONFIG` của `db_manager.py`.
    *   Đảm bảo database `ahp_db` và các bảng đã được tạo đúng.
*   **Lỗi `ModuleNotFoundError`:** Đảm bảo bạn đã kích hoạt môi trường ảo (`venv`) trước khi chạy `pip install -r requirements.txt` và `python app.py`.
*   **Trang web không hiển thị đúng:** Kiểm tra Console của trình duyệt (nhấn F12) xem có lỗi JavaScript hoặc CSS không.

