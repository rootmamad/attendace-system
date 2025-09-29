from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
import os, requests
import psycopg2, psycopg2.extras
from db import get_conn
from jwt_utils import jwt_required

bp = Blueprint("attendance_rest", __name__)

@bp.post("/attendance")
@jwt_required
def create_record():
    data = request.get_json() or {}

    emp_id = request.claims.get("employee_id")
    action = data.get("action")
    ts = data.get("timestamp")

    if action not in ("in", "out"):
        return jsonify({"error": "invalid action"}), 400

    ts_dt = datetime.fromisoformat(ts) if ts else datetime.utcnow()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
    "SELECT action FROM attendance WHERE employee_id=%s ORDER BY timestamp DESC LIMIT 1",
    (emp_id,)
    )
    row = cur.fetchone()
    last_action = row[0] if row else None

    if last_action == action:
        return jsonify({"error": f"امکان ثبت {action} پشت سر هم وجود ندارد"}), 400

    if last_action is None and action == "out":
        return jsonify({"error": "اولین عملیات باید ورود باشد"}), 400

    cur.execute(
        "INSERT INTO attendance (employee_id, action, timestamp) VALUES (%s,%s,%s) RETURNING id",
        (emp_id, action, ts_dt)
    )
    rec_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    try:
        payload = {
            "employee_id": emp_id,
            "action": action,
            "timestamp": ts_dt.isoformat()
        }
        reporter_url = os.getenv("REPORTER_INTERNAL_URL", "http://localhost:8103")
        secret = os.getenv("INTERNAL_HOOK_SECRET", "hook-secret")
        requests.post(
            f"{reporter_url}/hook/new-record",
            json=payload,
            headers={"X-Hook-Secret": secret},
            timeout=1.5
        )
    except Exception as e:
        print("Reporter hook error:", e)

    return jsonify({
        "id": rec_id,
        "employee_id": emp_id,
        "action": action,
        "timestamp": ts_dt.isoformat()
    })

@bp.get("/attendance/<employee_id>")
@jwt_required
def list_records(employee_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        """
        SELECT id, employee_id, action, timestamp
        FROM attendance
        WHERE employee_id=%s
          AND DATE(timestamp) = CURRENT_DATE
        ORDER BY timestamp DESC
        """,
        (employee_id,)
    )

    rows = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()
    rows = [{**r, "timestamp": r["timestamp"].isoformat()} for r in rows]
    return jsonify(rows)