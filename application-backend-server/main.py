from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import mysql.connector
from typing import Optional
import jwt
import requests
from pydantic import BaseModel, constr
from jwt import algorithms

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for DB Operations ---
class Student(BaseModel):
    student_id: constr(strip_whitespace=True, min_length=1, max_length=10)
    fullname: constr(strip_whitespace=True, min_length=1, max_length=100)
    dob: constr(strip_whitespace=True, min_length=10, max_length=10)
    major: constr(strip_whitespace=True, min_length=1, max_length=50)

class StudentUpdate(BaseModel):
    student_id: Optional[constr(strip_whitespace=True, min_length=1, max_length=10)] = None
    fullname: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None
    dob: Optional[constr(strip_whitespace=True, min_length=10, max_length=10)] = None
    major: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None

# --- Keycloak/OIDC Configuration ---
# NOTE: URL này sử dụng tên container và cổng nội bộ.
# Realm 'realm_sv001' dựa trên 'keycloak-assignment.md'.
# Vui lòng cập nhật 'realm_sv001' nếu bạn dùng tên realm khác.
KEYCLOAK_URL = "http://authentication-identity-server:8080"
REALM_NAME = "realm_sv001" 
KEYCLOAK_CERTS_URL = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/certs"
# Audience nên khớp với 'Client ID' trong Keycloak.
AUDIENCE = "flask-app" 

# --- Database Configuration ---
DB_CONFIG = {
    "host": "relational-database-server",
    "user": "root",
    "password": "root",
    "database": "studentdb",
    "port": 3306,
}

# --- Helper Functions ---
def get_db_connection():
    """Thiết lập kết nối tới MariaDB."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        print(f"Lỗi kết nối tới MariaDB: {e}")
        raise HTTPException(status_code=503, detail="Không thể kết nối tới database.")

_keycloak_public_keys = []
def get_keycloak_public_keys():
    """Lấy và cache public keys của Keycloak để xác thực token."""
    global _keycloak_public_keys
    if not _keycloak_public_keys:
        try:
            resp = requests.get(KEYCLOAK_CERTS_URL, timeout=5)
            resp.raise_for_status()
            _keycloak_public_keys = resp.json()["keys"]
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi lấy Keycloak public keys: {e}")
            raise HTTPException(status_code=503, detail="Không thể lấy public keys để xác thực token.")
    return _keycloak_public_keys

def get_token_verifier(authorization: Optional[str] = Header(None)):
    """Dependency của FastAPI để xác thực Keycloak JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Thiếu hoặc sai định dạng Authorization header")

    token = authorization.split(" ")[1]
    keys = get_keycloak_public_keys()

    try:
        token_header = jwt.get_unverified_header(token)
        kid = token_header.get("kid")
        if not kid:
            raise jwt.InvalidTokenError("Token header thiếu 'kid'")

        key_data = next((k for k in keys if k["kid"] == kid), None)
        if not key_data:
            # Keys có thể đã được xoay vòng, thử lấy lại một lần.
            global _keycloak_public_keys
            _keycloak_public_keys = []
            keys = get_keycloak_public_keys()
            key_data = next((k for k in keys if k["kid"] == kid), None)
            if not key_data:
                raise jwt.InvalidTokenError("Không tìm thấy public key cho 'kid' của token")

        public_key = algorithms.RSAAlgorithm.from_jwk(json.dumps(key_data))
        
        payload = jwt.decode(token, public_key, algorithms=["RS256"], audience=AUDIENCE)
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token đã hết hạn")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token không hợp lệ: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xác thực token thất bại: {e}")

# --- API Endpoints ---

@app.get("/hello")
async def hello():
    """Trả về một tin nhắn chào mừng đơn giản."""
    return {"message": "Welcome to the Application Backend Server!"}

@app.get("/student")
async def get_students_from_json():
    """Trả về danh sách sinh viên từ file JSON cục bộ."""
    json_path = os.path.join(BASE_DIR, "students.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/students-db")
def get_students_from_db():
    """Trả về danh sách sinh viên từ database MariaDB."""
    conn = get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, student_id, fullname, dob, major FROM students ORDER BY id")
            students = cursor.fetchall()
            return students
    except mysql.connector.Error as exc:
        raise HTTPException(status_code=500, detail=f"Truy vấn database thất bại: {exc}")
    finally:
        if conn.is_connected():
            conn.close()

@app.get("/secure")
def secure_endpoint(token_payload: dict = Depends(get_token_verifier)):
    """Endpoint bảo mật yêu cầu access token hợp lệ từ Keycloak."""
    return {"message": f"Access granted to secure endpoint for user: {token_payload.get('preferred_username')}"}

# --- CRUD Endpoints for MariaDB ---

@app.post("/students-db", status_code=201)
def create_student(student: Student):
    """Tạo một sinh viên mới trong database."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO students (student_id, fullname, dob, major) VALUES (%s, %s, %s, %s)",
                (student.student_id, student.fullname, student.dob, student.major),
            )
            conn.commit()
            inserted_id = cursor.lastrowid
            return {"id": inserted_id, **student.dict()}
    except mysql.connector.Error as exc:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo sinh viên: {exc}")
    finally:
        if conn.is_connected():
            conn.close()

@app.put("/students-db/{student_id}")
def update_student(student_id: int, student: StudentUpdate):
    """Cập nhật thông tin sinh viên dựa trên ID."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Kiểm tra xem sinh viên có tồn tại không
            cursor.execute("SELECT id FROM students WHERE id = %s", (student_id,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")

            updates = []
            values = []
            student_data = student.dict(exclude_unset=True)
            if not student_data:
                raise HTTPException(status_code=400, detail="Không có trường nào để cập nhật")

            for key, value in student_data.items():
                updates.append(f"{key} = %s")
                values.append(value)

            values.append(student_id)
            query = f"UPDATE students SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, tuple(values))
            conn.commit()
            return {"message": f"Đã cập nhật sinh viên có ID {student_id}"}
    except mysql.connector.Error as exc:
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật: {exc}")
    finally:
        if conn.is_connected():
            conn.close()

@app.delete("/students-db/{student_id}")
def delete_student(student_id: int):
    """Xóa một sinh viên khỏi database dựa trên ID."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
            conn.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên để xóa")
            return {"message": f"Đã xóa sinh viên có ID {student_id}"}
    except mysql.connector.Error as exc:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa: {exc}")
    finally:
        if conn.is_connected():
            conn.close()