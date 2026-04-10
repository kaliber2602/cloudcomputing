CloudComputing MiniCloud Setup (Restructured)

1. Chạy Docker Compose
   - Mở PowerShell hoặc CMD tại thư mục gốc của dự án.
   - Chạy lệnh để xây dựng và khởi động tất cả các dịch vụ:
       docker compose up -d --build --force-recreate

2. Các server và địa chỉ truy cập
   Hệ thống đã được tái cấu trúc để sử dụng API Gateway làm điểm truy cập duy nhất.

   - API Gateway / Điểm truy cập chính:
       http://localhost
       (Tất cả các request của người dùng đều đi qua đây)

   - Web Frontend (Phục vụ qua Gateway):
       Trang chủ: http://localhost/
       Trang blog: http://localhost/blogs/blog1.html
       Trang database: http://localhost/database.html

   - Application Backend API (Phục vụ qua Gateway):
       API chào mừng: http://localhost/api/hello
       API sinh viên (JSON): http://localhost/api/student
       API sinh viên (DB): http://localhost/api/students-db
       API bảo mật: http://localhost/api/secure (Cần Access Token)

   - Keycloak Auth Server:
       Server URL: http://localhost:8081
       Admin console: http://localhost:8081/admin/master/console/
       + Username: admin
       + Password: admin

   - MinIO Object Storage Console:
       http://localhost:9001
       + Access Key: minioadmin
       + Secret Key: minioadmin

   - MariaDB Database (Truy cập từ ứng dụng hoặc client DB):
       Host: localhost
       Port: 3306
       User: root
       Password: root
       Database: studentdb

   - Dịch vụ giám sát (Monitoring):
       http://localhost:9090
       http://localhost:3000

   - Dịch vụ khác:
       UDP port 1053
       Node Exporter: http://localhost:9100

3. Hướng dẫn Assignment & Bài Tập Lab
   - Keycloak Identity Provider & SSO:
       Xem hướng dẫn chi tiết trong file: keycloak-assignment.md
       (Yêu cầu: tạo realm, user, client, lấy token và truy cập API bảo mật)

   - Kiểm tra API bảo mật (/secure):
       Sau khi lấy được access_token từ Keycloak (theo hướng dẫn trong keycloak-assignment.md), sử dụng lệnh cURL sau:

       curl -X GET "http://localhost/api/secure" -H "Authorization: Bearer <your_access_token>"

       Lưu ý: Endpoint đã được chuyển vào Application Backend Server và truy cập qua Gateway tại /api/secure.
