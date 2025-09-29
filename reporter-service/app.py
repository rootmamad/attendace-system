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




user_clients = {}  # employee_id -> set of sockets

@sock.route('/ws')
def ws(ws):
    token = ws.environ.get("QUERY_STRING", "").replace("token=", "")
    claims = verify_token(token)
    emp_id = claims.get("employee_id")

    if emp_id not in user_clients:
        user_clients[emp_id] = set()
    user_clients[emp_id].add(ws)

    try:
        while True:
            if ws.receive() is None:
                break
    finally:
        user_clients[emp_id].remove(ws)




@app.post("/hook/new-record")
def new_record():
    secret = request.headers.get("X-Hook-Secret")
    expected = os.getenv("INTERNAL_HOOK_SECRET", "hook-secret")
    if secret != expected:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json() or {}
    emp_id = data.get("employee_id")

    # فقط به کلاینت‌های همون کارمند بفرست
    for ws in user_clients.get(emp_id, []):
        try:
            ws.send(str(data))
        except Exception:
            user_clients[emp_id].remove(ws)

    return jsonify({"status": "ok"})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8103, debug=True)
