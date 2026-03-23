from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
import mysql.connector

# ----------------------------
# FastAPI setup
# ----------------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# MySQL configuration
# ----------------------------
DB_HOST = "localhost"
DB_PORT = 3307  # adjust if needed
DB_USER = "swathi"
DB_PASSWORD = "1234"
DB_NAME = "olms"

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except mysql.connector.Error as e:
        print("❌ DB Error:", e)
        return None

# ----------------------------
# Pydantic Models
# ----------------------------
class User(BaseModel):
    id_number: str
    name: str
    email: str
    password: str
    role: str  # "student" or "teacher"

class Leave(BaseModel):
    id_number: str
    from_date: date
    to_date: date
    reason: str

class UpdateLeave(BaseModel):
    leave_id: int
    teacher_id: str
    status: str  # "Approved", "Rejected", "Pending"

# ----------------------------
# Register User
# ----------------------------
@app.post("/register")
def register_user(user: User):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="DB connection failed")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (id_number, name, email, password, role) VALUES (%s,%s,%s,%s,%s)",
            (user.id_number, user.name, user.email, user.password, user.role)
        )
        conn.commit()
        return {"message": "User registered successfully", "id_number": user.id_number, "role": user.role}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ----------------------------
# Apply Leave
# ----------------------------
@app.post("/applyleave")
def apply_leave(data: Leave):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="DB connection failed")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO leaves (id_number, from_date, to_date, reason) VALUES (%s,%s,%s,%s)",
            (data.id_number, data.from_date, data.to_date, data.reason)
        )
        conn.commit()
        return {"message": "Leave applied successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ----------------------------
# Get Leaves
# ----------------------------
@app.get("/getleaves")
def get_leaves(id_number: str = None):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="DB connection failed")
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT l.id, l.id_number, l.from_date, l.to_date, l.reason,
               COALESCE(t.status, 'Pending') AS teacher_status
        FROM leaves l
        LEFT JOIN teacher_approval t ON l.id = t.leave_id
        """
        if id_number:
            query += " WHERE l.id_number = %s"
            cursor.execute(query, (id_number,))
        else:
            cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ----------------------------
# Teacher Update Leave Status
# ----------------------------
@app.post("/updateleave")
def update_leave(data: UpdateLeave = Body(...)):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="DB connection failed")
    cursor = conn.cursor()
    try:
        # check if teacher approval already exists
        cursor.execute("SELECT * FROM teacher_approval WHERE leave_id=%s", (data.leave_id,))
        existing = cursor.fetchone()
        if existing:
            cursor.execute(
                "UPDATE teacher_approval SET status=%s, teacher_id=%s WHERE leave_id=%s",
                (data.status, data.teacher_id, data.leave_id)
            )
        else:
            cursor.execute(
                "INSERT INTO teacher_approval (leave_id, teacher_id, status) VALUES (%s,%s,%s)",
                (data.leave_id, data.teacher_id, data.status)
            )
        conn.commit()
        return {"message": "Status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()