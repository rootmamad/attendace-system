from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_conn
from jwt_utils import issue_token, jwt_required

bp = Blueprint("auth", __name__)

@bp.post("/register")
def register():
    data = request.get_json() or {}
    username, password = data.get("username"), data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT 1 FROM employees WHERE username=%s", (username,))
    if cur.fetchone():
        cur.close(); conn.close()
        return jsonify({"error": "username already exists"}), 409

    cur.execute(
        "INSERT INTO employees (username, password_hash) VALUES (%s,%s)",
        (username, generate_password_hash(password))
    )
    conn.commit(); cur.close(); conn.close()

    token = issue_token(username)
    return jsonify({"message": "employee registered successfully", "token": token}), 201


@bp.post("/login")
def login():
    data = request.get_json() or {}
    username, password = data.get("username"), data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT password_hash FROM employees WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close(); conn.close()

    if not row or not check_password_hash(row[0], password):
        return jsonify({"error": "invalid credentials"}), 401

    token = issue_token(username)
    return jsonify({"token": token})


@bp.get("/employees")
@jwt_required
def list_employees():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT id, username FROM employees ORDER BY id ASC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    employees = [{"id": r[0], "username": r[1]} for r in rows]
    return jsonify(employees)