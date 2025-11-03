import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initialize the database with required tables."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Devices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                device_id TEXT UNIQUE NOT NULL,
                device_name TEXT,
                ip_address TEXT,
                status TEXT DEFAULT 'Normal',
                is_connected BOOLEAN DEFAULT 0,
                sbytes INTEGER DEFAULT 0,
                dbytes INTEGER DEFAULT 0,
                rate REAL DEFAULT 0,
                dinpkt INTEGER DEFAULT 0,
                tcprtt REAL DEFAULT 0,
                synack INTEGER DEFAULT 0,
                ackdat INTEGER DEFAULT 0,
                smean REAL DEFAULT 0,
                dmean REAL DEFAULT 0,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # Detections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                attack_type TEXT NOT NULL,
                confidence REAL DEFAULT 0.95,
                severity TEXT DEFAULT 'Medium',
                indicators TEXT,
                risk_score INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
            )
        ''')

        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                device_id INTEGER NOT NULL,
                attack_type TEXT NOT NULL,
                severity TEXT DEFAULT 'High',
                email_sent BOOLEAN DEFAULT 0,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
            )
        ''')

        # Arduino connections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arduino_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                port TEXT UNIQUE NOT NULL,
                device_id INTEGER,
                connection_status TEXT DEFAULT 'disconnected',
                last_heartbeat TIMESTAMP,
                connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE SET NULL
            )
        ''')

        # Models table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                accuracy REAL DEFAULT 0,
                precision REAL DEFAULT 0,
                recall REAL DEFAULT 0,
                is_current BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_device_user ON devices(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_detection_device ON detections(device_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_detection_timestamp ON detections(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alert_device ON alerts(device_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alert_user ON alerts(user_id)')

def get_user(email):
    """Get user by email."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        return dict(cursor.fetchone()) if cursor.fetchone() else None

def create_user(username, email, password_hash):
    """Create a new user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        return cursor.lastrowid

def get_user_devices(user_id):
    """Get all devices for a user."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM devices WHERE user_id = ? ORDER BY created_at DESC',
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def create_device(user_id, device_id, device_name, ip_address, **params):
    """Create a new device."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO devices
            (user_id, device_id, device_name, ip_address, sbytes, dbytes, rate,
             dinpkt, tcprtt, synack, ackdat, smean, dmean)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, device_id, device_name, ip_address,
            params.get('sbytes', 0),
            params.get('dbytes', 0),
            params.get('rate', 0),
            params.get('dinpkt', 0),
            params.get('tcprtt', 0),
            params.get('synack', 0),
            params.get('ackdat', 0),
            params.get('smean', 0),
            params.get('dmean', 0),
        ))
        return cursor.lastrowid

def update_device_status(device_id, status, is_connected=None):
    """Update device status."""
    with get_db() as conn:
        cursor = conn.cursor()
        if is_connected is not None:
            cursor.execute(
                'UPDATE devices SET status = ?, is_connected = ?, last_seen = CURRENT_TIMESTAMP WHERE id = ?',
                (status, is_connected, device_id)
            )
        else:
            cursor.execute(
                'UPDATE devices SET status = ?, last_seen = CURRENT_TIMESTAMP WHERE id = ?',
                (status, device_id)
            )

def create_detection(device_id, attack_type, confidence, severity, indicators, risk_score):
    """Create a new detection record."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO detections
            (device_id, attack_type, confidence, severity, indicators, risk_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (device_id, attack_type, confidence, severity, indicators, risk_score))
        return cursor.lastrowid

def create_alert(user_id, device_id, attack_type, severity):
    """Create a new alert."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (user_id, device_id, attack_type, severity, email_sent)
            VALUES (?, ?, ?, ?, 0)
        ''', (user_id, device_id, attack_type, severity))
        return cursor.lastrowid

def mark_alert_sent(alert_id):
    """Mark alert as email sent."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE alerts SET email_sent = 1, sent_at = CURRENT_TIMESTAMP WHERE id = ?', (alert_id,))

def get_recent_detections(device_id, limit=20):
    """Get recent detections for a device."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM detections
            WHERE device_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (device_id, limit))
        return [dict(row) for row in cursor.fetchall()]

def get_device_by_id(device_id):
    """Get device by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def register_arduino_connection(port, device_id=None):
    """Register Arduino connection."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO arduino_connections
            (port, device_id, connection_status, last_heartbeat)
            VALUES (?, ?, 'connected', CURRENT_TIMESTAMP)
        ''', (port, device_id))
        return cursor.lastrowid

def update_arduino_heartbeat(port):
    """Update Arduino heartbeat."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE arduino_connections SET last_heartbeat = CURRENT_TIMESTAMP WHERE port = ?',
            (port,)
        )
