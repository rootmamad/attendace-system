from datetime import datetime,timezone
ts = "2025-09-29T08:30:00Z"
ts_dt = datetime.fromisoformat(ts) if ts else datetime.now(timezone.utc)
print(datetime.now())