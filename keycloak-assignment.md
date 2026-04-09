# Keycloak Demo - OIDC, Realm, Client, User và Access Token

## Mục tiêu kiến thức

- Hiểu mô hình OIDC trong cloud security
- Hiểu khái niệm `realm`, `client`, `user`
- Hiểu `Access Token` và cách Keycloak cấp token
- Demo luôn mà không cần backend app sẵn

## Yêu cầu demo

- Tạo 2 user: `sv01`, `sv02`
- Tạo 1 client: `flask-app` (Access Type: public)
- Lấy URL token endpoint và test demo `/secure` bằng cách dùng token

---

## 1. Setup Keycloak

1. Mở browser và truy cập: `http://localhost:8081/admin/master/console/`
2. Login bằng:
   - Username: `admin`
   - Password: `admin`
3. Bạn đã vào **Keycloak Admin Console**.

> Đây là nơi quản lý xác thực, không phải app chính của bạn.

---

## 2. Tạo Realm mới

1. Nhấn vào dropdown `Master` ở góc trái trên.
2. Chọn `Create realm`.
3. Nhập tên realm: `realm_sv001` (thay bằng mã sinh viên nếu cần).
4. Nhấn `Create`.

---

## 3. Tạo 2 user trong realm

1. Trong menu trái, chọn `Users`.
2. Nhấn `Add user`.
3. Tạo user `sv01`:
   - Username: `sv01`
   - Email: `sv01@example.com`
   - First Name: `Sinh Viên`
   - Last Name: `01`
   - Nhấn `Create`.
4. Tạo user `sv02` tương tự:
   - Username: `sv02`
   - Email: `sv02@example.com`
   - First Name: `Sinh Viên`
   - Last Name: `02`
   - Nhấn `Create`.
5. Set password cho mỗi user:
   - Click vào một user
   - Chọn tab `Credentials`
   - Nhập password `password123`
   - Chọn `Temporary` = Off
   - Nhấn `Set Password`

---

## 4. Tạo client `flask-app`

1. Trong menu trái, chọn `Clients`.
2. Nhấn `Create client`.
3. Ở trang `General settings`:
   - `Client type`: chọn `OpenID Connect`
   - `Client ID`: nhập `flask-app`
   - Nhấn `Next`.
4. Ở trang `Capability config`:
   - `Client authentication`: Off
   - `Standard flow`: bật (dùng Authorization Code flow)
   - Những tùy chọn khác giữ mặc định
   - Nhấn `Next`.
5. Ở trang `Login settings` hoặc `Access settings` (tùy giao diện):
   - `Root URL`: `http://localhost`
   - `Home URL`: để trống hoặc `http://localhost`
   - `Valid redirect URIs`: thêm `http://localhost/callback`
   - `Web origins`: thêm `http://localhost`
   - Nhấn `Save`.

> Nếu bạn chưa có app backend, dùng `http://localhost` làm demo tạm thời.

---

## 5. Kiểm tra endpoint Keycloak

1. Truy cập **Realm Settings** trong admin console.
2. Tìm phần `Endpoints` hoặc `OpenID Endpoint Configuration`.
3. Ghi lại URL token endpoint:

```
http://localhost:8081/realms/realm_sv001/protocol/openid-connect/token
```

4. URL auth endpoint:

```
http://localhost:8081/realms/realm_sv001/protocol/openid-connect/auth
```

---

## 6. Demo lấy token ngay (không cần app)

1. Mở terminal.
2. Chạy lệnh:

```bash
curl -X POST "http://localhost:8081/realms/realm_sv001/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=flask-app" \
  -d "grant_type=password" \
  -d "username=sv01" \
  -d "password=password123" \
  -d "scope=openid"
```

3. Nếu thành công, bạn sẽ nhận được JSON có `access_token`.

4. Lưu lại `access_token` để demo bước tiếp theo.

---

## 7. Demo Authorization Code login page

1. Mở browser.
2. Dán URL:

```
http://localhost:8081/realms/realm_sv001/protocol/openid-connect/auth?
client_id=flask-app
&redirect_uri=http://localhost/callback
&response_type=code
&scope=openid%20profile%20email
&state=test123
```

3. Bạn sẽ thấy trang login Keycloak.
4. Đăng nhập với `sv01` / `password123`.
5. Browser sẽ redirect về `http://localhost/callback?code=...&state=test123`.

> Nếu bạn chưa có app, URL `/callback` có thể lỗi. Nhưng bạn đã chứng minh được phần login của Keycloak hoạt động.

---

## 8. Demo `/secure` bằng token (Flask app thật)

Dù bạn chưa có backend app, nhưng project đã có Flask app demo với endpoint `/secure`:

1. Flask app chạy trên: `http://localhost:8086`
2. Endpoint `/secure` cần `Authorization: Bearer <token>`

**Test với cURL:**

```bash
curl -X GET "http://localhost:8086/secure" \
  -H "Authorization: Bearer <access_token>"
```

**Response thành công:**

```json
{
  "message": "Access granted to /secure"
}
```

**Response lỗi (401):**

```json
{
  "error": "Invalid token"
}
```

> Đây là demo thực tế của `/secure` endpoint được bảo vệ bởi Keycloak JWT token.

---

## 9. Hiểu mô hình OIDC

- `realm`: vùng quản lý người dùng và client riêng biệt.
- `client`: ứng dụng muốn dùng Keycloak để xác thực (`flask-app`).
- `user`: tài khoản đăng nhập (`sv01`, `sv02`).
- `Access Token`: token JWT Keycloak cấp khi user đăng nhập thành công.

Model flow cơ bản:

1. App (`client`) chuyển user đến Keycloak login.
2. User nhập thông tin, Keycloak xác thực.
3. Nếu đúng, Keycloak cấp `code` hoặc `token`.
4. App đổi `code` lấy `access token` từ `token endpoint`.
5. App dùng `access token` để gọi API `/secure`.

---

## 10. Kết luận demo

Bạn đã thực hiện được:

- Tạo `realm_sv001`
- Tạo `sv01` và `sv02`
- Tạo client `flask-app`
- Lấy `token endpoint`
- Demo lấy token bằng curl
- Demo mở trang login Keycloak bằng browser
- Demo truy cập `/secure` với token thật

Bạn đã hoàn thành assignment Keycloak với demo thực tế!

---

## 11. Khi có backend app thật

Khi bạn có app backend, chỉ cần:

- thêm endpoint `/callback`
- cập nhật `Valid redirect URIs` với URL app thật
- dùng `access token` để bảo vệ `/secure`
