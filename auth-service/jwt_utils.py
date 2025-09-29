import os
import jwt
import datetime
from functools import wraps
from flask import request, jsonify

SECRET = os.getenv("JWT_SECRET", "dev-secret")
ALG = "HS256"

def issue_token(employee_id: int, username: str, expires_in_hours: int = 1):
    payload = {
        "sub": username,
        "employee_id": employee_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expires_in_hours)
    }
    return jwt.encode(payload, SECRET, algorithm=ALG)

def verify_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=[ALG])

def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing Bearer token"}), 401
        token = auth_header.replace("Bearer ", "").strip()
        try:
            claims = verify_token(token)
            request.claims = claims
        except Exception as e :
            return jsonify({"error": "Invalid or expired token"+e}), 401
        return fn(*args, **kwargs)
    return wrapper