# Sử dụng image Nginx chính thức, phiên bản alpine cho dung lượng nhẹ
FROM nginx:alpine

# Xóa file cấu hình mặc định để tránh xung đột
RUN rm /etc/nginx/conf.d/default.conf

# Sao chép file cấu hình Nginx tùy chỉnh của chúng ta vào container
COPY nginx.conf /etc/nginx/conf.d/default.conf