# Login, JWT y middleware
from fastapi import Request, HTTPException
from jose import jwt
import bcrypt
from datetime import datetime, timedelta
import os
from .db import get_connection

SECRET = os.getenv("JWT_SECRET")
ALGO = os.getenv("JWT_ALGORITHM")
EXPIRE = int(os.getenv("JWT_EXPIRE_MINUTES"))

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=EXPIRE)
    return jwt.encode(payload, SECRET, algorithm=ALGO)

async def auth_middleware(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Token missing")

    try:
        scheme, token = auth_header.split(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")

        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        request.state.user = payload

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def login(username: str, password: str):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="DB not connected")

#nada
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    id_user,
                    id_person,
                    username,
                    password_hash,
                    status
                FROM users
                WHERE username = %s
                """,
                (username,)
            )
            user = cur.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if user["status"] != "active":
            raise HTTPException(
                status_code=403,
                detail=f"User status: {user['status']}"
            )

        if not verify_password(password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return create_token({
            "id_user": user["id_user"],
            "id_person": user["id_person"],
            "username": user["username"],
            "status": user["status"]
        })

    finally:
        conn.close()
        