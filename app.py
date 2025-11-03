# app.py (final updated version)
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import json
import threading
import serial
import time
import sqlite3
import traceback

# token serializer (from itsdangerous)
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired

# Import project modules
from database import (
    init_db, get_user, create_user, get_user_devices, create_device,
    update_device_status, create_detection, create_alert, mark_alert_sent,
    get_device_by_id
)
from attack_detection import detect_attack, get_attack_recommendations
from email_alerts import send_attack_alert
from arduino_manager import (
    send_to_arduino_display, send_attack_to_arduino, clear_arduino_display
)

# ---------------------------------------------------------------------

load_dotenv()
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize local SQLite database
init_db()

# Serializer for tokens
serializer = Serializer(app.secret_key)

# Arduino settings
arduino = None
connected = False
arduino_port = os.getenv("ARDUINO_PORT", "COM5")
baud_rate = int(os.getenv("ARDUINO_BAUDRATE", "9600"))

# ---------------------------------------------------------------------
# Arduino Connection Management
# ---------------------------------------------------------------------

def connect_arduino():
    global arduino, connected
    try:
        arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
        print(f"✅ Connected to Arduino on {arduino_port}")
        time.sleep(2)
        threading.Thread(target=listen_serial, daemon=True).start()
    except Exception as e:
        print(f"❌ Could not connect to Arduino: {e}")
        connected = False


def listen_serial():
    global connected
    while True:
        try:
            if arduino and arduino.in_waiting > 0:
                line = arduino.readline().decode(errors='ignore').strip()
                if line:
                    print(f"⬅️ Arduino: {line}")
                    if '"arduino_ready"' in line or 'arduino_ready' in line:
                        connected = True
                        send_to_arduino({"cmd": "CONNECTED"})
                        print("🔗 Handshake complete — LCD should now say 'System Online'")
        except Exception as e:
            print(f"⚠️ Serial read error: {e}")
            connected = False
            time.sleep(2)


def send_to_arduino(data):
    global connected
    try:
        if arduino and getattr(arduino, "is_open", False):
            arduino.write((json.dumps(data) + "\n").encode())
            print(f"➡️ Sent to Arduino: {data}")
        else:
            connected = False
    except Exception as e:
        print(f"⚠️ Send error: {e}")
        connected = False

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "database.db")

def query_table(table: str, limit: int = 100):
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not cur.fetchone():
            return []
        cur.execute(f"SELECT * FROM {table} ORDER BY rowid DESC LIMIT ?", (limit,))
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        con.close()
        return rows
    except Exception as e:
        print("DB query error:", e)
        traceback.print_exc()
        return []

def generate_token(user_id: int):
    try:
        return serializer.dumps({"user_id": user_id})
    except Exception as e:
        print("Token generation error:", e)
        return None

def verify_token(token: str):
    try:
        data = serializer.loads(token, max_age=3600*24*7)
        return data.get("user_id")
    except SignatureExpired:
        print("Token expired")
        return None
    except BadSignature:
        print("Bad token signature")
        return None
    except Exception as e:
        print("Token verify error:", e)
        return None

def auth_required(fn):
    from functools import wraps
    from flask import g
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth.split(" ", 1)[1]
            uid = verify_token(token)
            if uid:
                g.user_id = uid
                return fn(*args, **kwargs)
        g.user_id = None
        return fn(*args, **kwargs)
    return wrapper

# ---------------------------------------------------------------------
# Authentication Routes
# ---------------------------------------------------------------------

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json(force=True) or {}
        username = data.get('username') or data.get('email', '').split('@')[0]
        email = data.get('email')
        password = data.get('password')

        if not all([username, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400

        if get_user(email):
            return jsonify({'error': 'Email already exists'}), 400

        password_hash = generate_password_hash(password)
        user_id = create_user(username, email, password_hash)

        return jsonify({
            'user': {'id': user_id, 'email': email, 'username': username},
            'message': 'Registration successful'
        }), 201

    except Exception as e:
        print("Register error:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json(force=True) or {}
        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({'error': 'Missing required fields'}), 400

        user = get_user(email)
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401

        token = generate_token(user['id'])
        return jsonify({
            'user': {'id': user['id'], 'email': user['email'], 'username': user['username']},
            'token': token,
            'message': 'Login successful'
        }), 200

    except Exception as e:
        print("Login error:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------
# Alternate routes for frontend compatibility
# ---------------------------------------------------------------------

@app.route('/api/register', methods=['POST'])
def register_alt():
    return register()

@app.route('/api/login', methods=['POST'])
def login_alt():
    return login()

@app.route('/api/logout', methods=['POST'])
def logout():
    try:
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        print("Logout error:", e)
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------------------
# Devices + Detection
# ---------------------------------------------------------------------

@app.route('/api/devices', methods=['GET'])
@auth_required
def get_devices():
    from flask import g
    try:
        user_id = g.get('user_id') or request.args.get('user_id', type=int)
        if not user_id:
            rows = query_table('devices', 1000)
            return jsonify(rows), 200
        return jsonify(get_user_devices(user_id) or []), 200
    except Exception as e:
        print("Get devices error:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices', methods=['POST'])
@auth_required
def post_device():
    try:
        data = request.get_json(force=True) or {}
        from flask import g
        user_id = g.get('user_id') or data.get('user_id')
        device_id = data.get('device_id') or data.get('id')
        device_name = data.get('device_name') or 'IoT Device'
        ip_address = data.get('ip_address') or '0.0.0.0'

        if not all([user_id, device_id]):
            return jsonify({'error': 'Missing required fields'}), 400

        params = {
            'sbytes': data.get('sbytes', 0),
            'dbytes': data.get('dbytes', 0),
            'rate': data.get('rate', 0),
            'dinpkt': data.get('dinpkt', 0),
            'tcprtt': data.get('tcprtt', 0),
            'synack': data.get('synack', 0),
            'ackdat': data.get('ackdat', 0),
            'smean': data.get('smean', 0),
            'dmean': data.get('dmean', 0),
        }

        device_db_id = create_device(user_id, device_id, device_name, ip_address, **params)
        attack_type, confidence, severity, risk_score, indicators = detect_attack(params)
        create_detection(device_db_id, attack_type, confidence, severity, json.dumps(indicators), risk_score)
        update_device_status(device_db_id, attack_type, True)

        if attack_type != 'Normal':
            alert_id = create_alert(user_id, device_db_id, attack_type, severity)
            recommendations = get_attack_recommendations(attack_type)
            send_attack_alert(device_name, attack_type, severity, indicators, recommendations)
            mark_alert_sent(alert_id)
            send_attack_to_arduino(attack_type, severity)
        else:
            send_to_arduino_display(device_name, ip_address)

        return jsonify({
            'device_id': device_db_id,
            'attack_type': attack_type,
            'confidence': confidence,
            'severity': severity,
            'risk_score': risk_score,
            'indicators': indicators
        }), 201
    except Exception as e:
        print("Post device error:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------------------
# Health / Arduino
# ---------------------------------------------------------------------

@app.route('/api/arduino/status', methods=['GET'])
def arduino_status():
    return jsonify({'connected': connected, 'port': arduino_port, 'baudrate': baud_rate}), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'IoT Security System Backend is running'}), 200

@app.route('/', methods=['GET'])
def index():
    return jsonify({'name': 'IoT Network Attack Detection System', 'version': '3.0', 'status': 'running'}), 200

# ---------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------

if __name__ == '__main__':
    print("🚀 Starting IoT Security System Backend...")
    print(f"📂 Database initialized at: {DB_PATH}")
    print("🌐 API endpoints available at: http://localhost:5000/api/*")
    connect_arduino()
    app.run(debug=False, host='0.0.0.0', port=5000)
