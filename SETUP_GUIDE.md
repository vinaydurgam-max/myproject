# IoT Network Attack Detection System - Complete Setup Guide

## System Overview

This is a comprehensive IoT security system that detects network attacks, sends email alerts, and communicates with Arduino LCD displays in real-time.

### Architecture

```
┌──────────────────────┐
│  React Dashboard     │
│  (Vite + TypeScript) │
└──────────┬───────────┘
           │
           ├── HTTP/REST ──────────┐
           │                       │
           ▼                       ▼
┌──────────────────────┐  ┌──────────────────────┐
│  Flask Backend       │  │  SQLite Database     │
│  (Python 3.10+)      │  │  (Local Storage)     │
└──────────┬───────────┘  └──────────────────────┘
           │
           ├── Serial/USB ─────────┐
           │                       │
           ▼                       ▼
    ┌─────────────┐        ┌──────────────────┐
    │   Email     │        │  Arduino + LCD   │
    │   SMTP      │        │  Display System  │
    └─────────────┘        └──────────────────┘
```

---

## Prerequisites

### System Requirements

- **Processor**: Intel i3 or equivalent (or above)
- **RAM**: Minimum 4 GB
- **Storage**: 500 MB free space
- **OS**: Windows, macOS, or Linux
- **Python**: 3.10 or higher
- **Node.js**: 16.0 or higher

### Hardware Requirements

- **Arduino**: UNO, Nano, or Mega
- **LCD Display**: 16x2 or 20x4 (I2C module recommended)
- **USB Cable**: USB-A to USB-B for Arduino programming and communication

---

## Installation & Setup

### Step 1: Clone or Download Project

```bash
cd /tmp/cc-agent/59545832/project
```

### Step 2: Install Frontend Dependencies

```bash
npm install
npm run build
```

### Step 3: Install Backend Dependencies

```bash
pip install -r backend_requirements.txt
```

### Step 4: Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set your configuration:

```env
# Flask Configuration
SECRET_KEY=your-very-secure-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False

# Email Configuration (Gmail Example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-specific-password
ADMIN_EMAIL=admin@example.com

# Arduino Configuration
ARDUINO_BAUDRATE=9600
ARDUINO_PORT=/dev/ttyUSB0  # Change based on your system

# Database
DATABASE_PATH=./database.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
```

**Important: Gmail Setup**
1. Enable 2-Factor Authentication on your Gmail account
2. Create an App Password: https://myaccount.google.com/apppasswords
3. Use the generated password in `SENDER_PASSWORD`

### Step 5: Setup SQLite Database

The database is automatically created on first backend startup.

```bash
# Verify database initialization
python -c "from backend.database import init_db; init_db(); print('Database initialized')"
```

### Step 6: Upload Arduino Sketch

1. Open Arduino IDE
2. Install required libraries:
   - `LiquidCrystal_I2C` (by Frank de Brabander)
   - `ArduinoJson` (by Benoit Blanchon)
3. Open `arduino/arduino_iot_security.ino`
4. Select your Arduino board and COM port
5. Click "Upload"

---

## Running the System

### Terminal 1: Start Flask Backend

```bash
cd backend
python app.py
```

Expected output:
```
Starting IoT Security System Backend...
Database initialized at: backend/database.db
API endpoints available at: http://localhost:5000/api/*
Running on http://0.0.0.0:5000
```

### Terminal 2: Start React Frontend (Development)

```bash
npm run dev
```

Access the dashboard at: `http://localhost:5173`

### Terminal 3: (Optional) Connect Arduino

Ensure Arduino is connected via USB. The system will auto-detect it when you click "Connect Arduino" in the dashboard.

---

## API Endpoints

### Authentication

**POST** `/api/auth/register`
```json
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "secure_password"
}
```

**POST** `/api/auth/login`
```json
{
  "email": "admin@example.com",
  "password": "secure_password"
}
```

### Devices

**GET** `/api/devices?user_id=1` - Get all devices

**POST** `/api/devices/register` - Register new device
```json
{
  "user_id": 1,
  "device_id": "iot_001",
  "device_name": "Office Router",
  "ip_address": "192.168.1.1",
  "sbytes": 1000,
  "dbytes": 500,
  "rate": 100,
  "dinpkt": 50,
  "tcprtt": 50,
  "synack": 10,
  "ackdat": 20,
  "smean": 0.5,
  "dmean": 0.4
}
```

### Detection & Analysis

**POST** `/api/detection/analyze` - Analyze network parameters
```json
{
  "device_id": 1,
  "sbytes": 95000,
  "dbytes": 500,
  "rate": 5500,
  "dinpkt": 850,
  "tcprtt": 1600,
  "synack": 210,
  "ackdat": 600,
  "smean": 0.2,
  "dmean": 0.8
}
```

**GET** `/api/detections/<device_id>?limit=20` - Get detections

### Arduino Management

**GET** `/api/arduino/ports` - List available Arduino ports

**POST** `/api/arduino/connect`
```json
{
  "port": "/dev/ttyUSB0",
  "device_id": 1
}
```

**POST** `/api/arduino/display`
```json
{
  "device_name": "Office Router",
  "ip_address": "192.168.1.1"
}
```

**POST** `/api/arduino/clear` - Clear LCD display

---

## Detection Logic

### Attack Types (12 Categories)

1. **Normal** - Safe traffic pattern
2. **Malware** - High source bytes, low destination response
3. **Phishing** - High destination entropy, low source entropy
4. **DoS** - High TCPRTT with high destination packets
5. **DDoS** - High rate with multiple SYN-ACK packets
6. **Man-in-the-Middle** - High ACK packets, low SYN-ACK, high rate
7. **SQL Injection** - High destination packets, low TCPRTT
8. **Cross-Site Scripting** - High entropy in both directions
9. **Social Engineering** - Low rate with high TCPRTT
10. **Zero-Day Exploit** - Extreme values across multiple metrics
11. **Insider Threat** - Anomalous entropy patterns
12. **Spoofing/Password Attack** - Very high SYN-ACK or fast rate with low latency

### Risk Score Calculation

- Each suspicious metric adds points (0-100 scale)
- Higher score = higher threat level
- Used for prioritization and alerting

---

## Arduino LCD Behavior

### Display States

1. **Disconnected**: "Waiting for / Connection..."
2. **Connected**: "Connected to / IoT Security"
3. **Normal**: "Device Name / IP Address"
4. **Attack Alert**: Flashing "ATTACK:" display, shows attack type
5. **Clearing**: Returns to normal display

### Communication Protocol

Arduino receives JSON commands via serial:

```json
{
  "cmd": "DISPLAY",
  "data": {
    "line1": "Device: Router",
    "line2": "192.168.1.1"
  },
  "timestamp": 1234567890
}
```

Arduino responds with:
```json
{
  "ack": true,
  "display_updated": true
}
```

---

## Troubleshooting

### Arduino Not Connecting

1. **Check USB Connection**:
   - Verify USB cable is properly connected
   - Check device manager for COM port recognition

2. **Identify Correct Port**:
   ```bash
   # Linux/Mac
   ls /dev/tty*

   # Windows
   mode  # List COM ports
   ```

3. **Update Arduino Drivers**:
   - Install CH340 drivers if using clone boards
   - Download from: https://www.wch.cn/downloads/CH341SER_ZIP.html

4. **Verify Baud Rate**:
   - Default: 9600
   - Match in both Arduino sketch and `.env`

### Email Alerts Not Sending

1. **Check SMTP Configuration**:
   - Verify SMTP server and port
   - Test credentials with: `telnet smtp.gmail.com 587`

2. **Gmail Specific**:
   - Enable "Less secure app access" OR use App Password
   - Check 2FA is enabled
   - Verify app-specific password in `.env`

3. **Check Logs**:
   - Backend will print email errors to console
   - Check firewall/antivirus blocking SMTP

### Database Issues

1. **Reset Database**:
   ```bash
   rm backend/database.db
   python -c "from backend.database import init_db; init_db()"
   ```

2. **Check Permissions**:
   - Ensure write permissions to `backend/` directory

### Frontend Build Issues

1. **Clear Node Cache**:
   ```bash
   rm -rf node_modules
   npm install
   npm run build
   ```

2. **Update Dependencies**:
   ```bash
   npm update
   npm run build
   ```

---

## Security Recommendations

### Production Deployment

1. **Change Secret Key**:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Use output in `.env` `SECRET_KEY`

2. **Set FLASK_ENV to Production**:
   ```env
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

3. **Use Environment Variables**:
   - Never commit `.env` file
   - Add `.env` to `.gitignore`

4. **Enable HTTPS**:
   - Use reverse proxy (Nginx/Apache)
   - Install SSL certificate

5. **Database Security**:
   - Regular backups of `database.db`
   - Restrict file permissions: `chmod 600 database.db`

6. **Email Security**:
   - Use app-specific passwords
   - Consider using SendGrid or Mailgun for production

7. **Arduino Security**:
   - Secure serial port access
   - Validate all incoming JSON
   - Implement timeout mechanisms

---

## Performance Optimization

### Backend Optimization

- Use connection pooling for database
- Implement caching for device lists
- Optimize detection algorithm

### Frontend Optimization

- Enable production build
- Implement lazy loading
- Use React suspense for async components

### System Monitoring

Monitor these resources:
- CPU usage during detection
- Memory usage (especially for large device lists)
- Disk I/O for database operations

---

## Testing

### Manual Testing

1. **Register Test Device**:
   ```bash
   curl -X POST http://localhost:5000/api/devices/register \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 1,
       "device_id": "test_001",
       "device_name": "Test Device",
       "sbytes": 95000,
       "rate": 5500
     }'
   ```

2. **Simulate Attack**:
   Send parameters with high risk values to trigger detection

3. **Check Database**:
   ```bash
   sqlite3 backend/database.db "SELECT * FROM detections LIMIT 5;"
   ```

---

## Support & Resources

- **Arduino Libraries**: https://www.arduino.cc/reference/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **React Documentation**: https://react.dev/
- **SQLite Documentation**: https://www.sqlite.org/docs.html

---

## License & Credits

IoT Network Attack Detection System v3.0
Built with Python, Flask, React, TypeScript, SQLite, and Arduino

---

## Next Steps

1. Deploy frontend to production server
2. Configure firewall rules for port 5000
3. Set up automated backups
4. Implement additional ML models
5. Add support for multiple Arduino devices
6. Create mobile app version
