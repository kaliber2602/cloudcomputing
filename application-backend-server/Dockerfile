# Sử dụng image Python chính thức, phiên bản slim nhẹ
FROM python:3.9-slim

# Đặt thư mục làm việc bên trong container
WORKDIR /app

# Sao chép file dependencies vào thư mục làm việc
COPY requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ code của ứng dụng vào
COPY . .

# Lệnh để chạy ứng dụng FastAPI bằng server Uvicorn
# --host 0.0.0.0 để có thể truy cập từ bên ngoài container
# --port 8081 khớp với cổng nội bộ đã định nghĩa trong docker-compose.yml
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]