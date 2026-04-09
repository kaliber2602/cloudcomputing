from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import json

app = FastAPI()

# Cấu hình CORS cực kỳ chi tiết
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các nguồn (bao gồm cả port 5501 của bạn)
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép GET, POST, v.v.
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "students.json")

@app.get("/student")
async def get_students():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)