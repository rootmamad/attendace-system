import os
from flask import Flask
from routes_rest import bp as rest_bp
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.register_blueprint(rest_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("ATTENDANCE_PORT", 8002)))