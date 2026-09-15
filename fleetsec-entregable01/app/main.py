from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import sqlite3

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from passlib.context import CryptContext

app = FastAPI(title="FleetSec API", version="1.0.0")
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-secret-change-me")
JWT_ALGORITHM = "HS256"
DB_PATH = Path(os.getenv("FLEETSEC_DB", "fleetsec.db"))

class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)

class Vehicle(BaseModel):
    id: int
    plate: str
    status: str


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT NOT NULL, role TEXT NOT NULL)")
        conn.execute("CREATE TABLE IF NOT EXISTS vehicles (id INTEGER PRIMARY KEY, plate TEXT UNIQUE, status TEXT NOT NULL)")
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            conn.execute("INSERT INTO users(username,password_hash,role) VALUES (?,?,?)", ("demo", pwd_context.hash("DemoPass123!"), "user"))
        if conn.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0] == 0:
            conn.executemany("INSERT INTO vehicles(plate,status) VALUES (?,?)", [("FSC001", "active"), ("FSC002", "maintenance")])

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/login")
def login(payload: LoginRequest):
    with db() as conn:
        user = conn.execute("SELECT * FROM users WHERE username = ?", (payload.username,)).fetchone()
    if not user or not pwd_context.verify(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    now = datetime.now(timezone.utc)
    token = jwt.encode({"sub": user["username"], "role": user["role"], "iat": now, "exp": now + timedelta(minutes=30)}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


def current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        return jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

@app.get("/vehicles", response_model=list[Vehicle])
def vehicles(_: dict = Depends(current_user)):
    with db() as conn:
        rows = conn.execute("SELECT id, plate, status FROM vehicles").fetchall()
    return [dict(row) for row in rows]
