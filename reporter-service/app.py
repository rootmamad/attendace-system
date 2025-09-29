import os
import jwt
from flask import Flask, request, jsonify
from flask_sock import Sock

SECRET = os.getenv("JWT_SECRET", "dev-secret")
ALG = "HS256"

app = Flask(__name__)
sock = Sock(app)

clients = set()

def verify_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=[ALG])

@sock.route('/ws')
def ws(ws):
    token = ws.environ.get("QUERY_STRING", "").replace("token=", "")
    if not token:
        ws.close()
        return

    try:
        claims = verify_token(token)
    except Exception:
        ws.close()
        return

    clients.add(ws)
    try:
        while True:
            data = ws.receive()
            if data is None:
                break
    finally:
        clients.remove(ws)

@app.post("/hook/new-record")
def new_record():
    secret = request.headers.get("X-Hook-Secret")
    expected = os.getenv("INTERNAL_HOOK_SECRET", "hook-secret")
    if secret != expected:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json() or {}
    dead = []
    for c in clients:
        try:
            c.send(str(data))
        except Exception:
            dead.append(c)
    for d in dead:
        clients.remove(d)

    return jsonify({"status": "ok"})