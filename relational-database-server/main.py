import os
from typing import Optional

import mysql.connector
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, constr

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

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

DB_CONFIG = {
    "host": "relational-database-server",
    "user": "root",
    "password": "root",
    "database": "studentdb",
    "port": 3306,
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.get("/", response_class=FileResponse)
def serve_ui():
    return os.path.join(BASE_DIR, "index.htm")


@app.get("/api/students-db")
def read_students():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students ORDER BY id")
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        return students
    except mysql.connector.Error as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/students-db/{student_id}")
def read_student(student_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    except mysql.connector.Error as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/students-db")
def create_student(student: Student):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (student_id, fullname, dob, major) VALUES (%s, %s, %s, %s)",
            (student.student_id, student.fullname, student.dob, student.major),
        )
        conn.commit()
        inserted_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return {"id": inserted_id, "message": "Student created"}
    except mysql.connector.Error as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.put("/api/students-db/{student_id}")
def update_student(student_id: int, student: StudentUpdate):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM students WHERE id = %s", (student_id,))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Student not found")

        updates = []
        values = []
        if student.student_id is not None:
            updates.append("student_id = %s")
            values.append(student.student_id)
        if student.fullname is not None:
            updates.append("fullname = %s")
            values.append(student.fullname)
        if student.dob is not None:
            updates.append("dob = %s")
            values.append(student.dob)
        if student.major is not None:
            updates.append("major = %s")
            values.append(student.major)

        if not updates:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="No fields to update")

        values.append(student_id)
        query = f"UPDATE students SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, tuple(values))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Student updated"}
    except mysql.connector.Error as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/api/students-db/{student_id}")
def delete_student(student_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        conn.commit()
        deleted = cursor.rowcount
        cursor.close()
        conn.close()
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"message": "Student deleted"}
    except mysql.connector.Error as exc:
        raise HTTPException(status_code=500, detail=str(exc))
