CloudComputing MiniCloud Setup

1. Chạy Docker Compose
   - Mở PowerShell hoặc CMD tại thư mục
   - Chạy:
       docker compose up -d --build

2. Các server và địa chỉ truy cập
   - Web Frontend:
       http://localhost:8080
   - API Gateway / Reverse Proxy:
       http://localhost

   - Application Backend Server (FastAPI):
       UI trực tiếp: http://localhost:8085/
       API trực tiếp: http://localhost:8085/student
       API qua proxy: http://localhost/api/student
       UI qua proxy: http://localhost/student-dashboard/
       (nếu dùng proxy, `http://localhost/api/student` sẽ đến backend route `/student`)

   - Relational Database Dashboard Server:
       UI: http://localhost:8082
       API JSON direct: http://localhost:8082/api/students-db
       API JSON via proxy: http://localhost/api/students-db

   - Keycloak Auth Server:
       Server URL: http://localhost:8081
       Admin console: http://localhost:8081/admin/master/console/
       + Username: admin
       + Password: admin
       (Lưu ý: với Keycloak này, `http://localhost:8081/auth/` không phải trang login chung và có thể trả 404.)
       Login/auth request thường là:
       http://localhost:8081/realms/master/protocol/openid-connect/auth?client_id=security-admin-console&redirect_uri=...

   - Flask Secure App (Demo /secure endpoint):
       URL: http://localhost:8086/secure
       (Cần Authorization: Bearer <token> từ Keycloak)

   - MinIO Object Storage Console:
       http://localhost:9001
       + Access Key: minioadmin
       + Secret Key: minioadmin

   - MariaDB Database:
       Host: localhost
       Port: 3306
       User: root
       Password: root
       Database: studentdb

   - Prometheus:
       http://localhost:9090
   - Grafana:
       http://localhost:3000
   - Internal DNS Server:
       UDP port 1053
       (dùng `nslookup` hoặc `dig` để test nếu cần)

3. Các endpoint kiểm tra nhanh
   - Web frontend root:
       http://localhost:8080
   - Backend App qua proxy:
       http://localhost/api/student
   - Backend App trực tiếp:
       http://localhost:8085/student
   - Backend App UI trực tiếp:
       http://localhost:8085/
   - Backend App UI qua proxy:
       http://localhost/student-dashboard/
   - Database Dashboard UI:
       http://localhost:8082
   - Database API:
       http://localhost:8082/api/students-db

4. Hướng dẫn Assignment & Bài Tập Lab
   - Keycloak Identity Provider & SSO:
       Xem file: keycloak-assignment.md
       (Yêu cầu: tạo realm, user, client, lấy token endpoint, truy cập /secure)
   - Flask Secure App Demo:
       URL: http://localhost:8086/secure
       Test với: curl -H "Authorization: Bearer <token>" http://localhost:8086/secure

