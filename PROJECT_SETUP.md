# IoT Botnet and Malware Attack Detection System - Setup Guide

## Overview

This is a comprehensive web-based IoT security monitoring system that detects botnet and malware attacks in real-time using machine learning-based classification. The system monitors IoT device telemetry, identifies attack patterns, and sends instant email alerts.

## Features

- User authentication with Supabase Auth
- IoT device registration with secure token generation
- Real-time telemetry data ingestion API
- ML-based attack classification (Mirai, UDP Flood, SYN Flood, ICMP Flood, Port Scan)
- Automatic email alerts for detected threats
- Interactive dashboard with statistics and visualizations
- Detection log with filtering and CSV export
- Device management (enable/disable, delete)
- Responsive design for desktop and mobile

## Technology Stack

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: Supabase (PostgreSQL database + Edge Functions)
- **Authentication**: Supabase Auth (email/password)
- **Icons**: Lucide React
- **ML Classification**: Rule-based system (can be upgraded to trained model)

## Prerequisites

- Node.js 18+ installed
- A Supabase account (free tier works)
- Git (for version control)

## Setup Instructions

### 1. Supabase Project Setup

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait for the database to be provisioned
3. Navigate to Project Settings > API
4. Copy your project URL and anon key

### 2. Environment Configuration

1. Create a `.env` file in the project root:

```bash
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. Database Setup

The database tables have already been created via migration. Your database should have:

- **devices** - Stores registered IoT devices
- **detections** - Records all attack detections
- **alerts** - Tracks sent email alerts

### 4. Edge Functions

Two Edge Functions are deployed:

1. **iot-ingest** - Receives telemetry data and performs ML classification
2. **send-alert** - Sends email notifications for detected attacks

These are already deployed and ready to use.

### 5. Install Dependencies

```bash
npm install
```

### 6. Run Development Server

```bash
npm run dev
```

The application will start at `http://localhost:5173`

### 7. Build for Production

```bash
npm run build
```

## Usage Guide

### Step 1: Create an Account

1. Open the application in your browser
2. Click "Sign up" to create a new account
3. Enter your email and password (minimum 6 characters)
4. Sign in with your credentials

### Step 2: Register IoT Device

1. Navigate to the "Devices" tab
2. Click "Register Device"
3. Enter a Device ID (e.g., `esp32_001`)
4. Enter a Device Name (e.g., `Living Room Sensor`)
5. Click "Register"
6. Copy the generated device token (you'll need this for your IoT device)

### Step 3: Configure Your IoT Device

Use the device token to send telemetry data from your IoT device. See `IOT_DEVICE_GUIDE.md` for detailed integration instructions.

### Step 4: Monitor Dashboard

1. View real-time statistics on the Dashboard tab
2. Check the Detections tab for attack logs
3. Filter detections by attack type
4. Export detection logs to CSV

### Step 5: Receive Email Alerts

When an attack is detected, you'll automatically receive an email alert containing:
- Attack type
- Device information
- Severity level
- Confidence score
- Timestamp
- Recommended actions

## Attack Detection

The system uses a rule-based ML classifier that analyzes network telemetry:

### Detection Rules

- **UDP Flood**: High UDP rate (>500) + high packet rate (>1000)
- **SYN Flood**: High TCP flags (>10) + many failed connections (>20)
- **Mirai Botnet**: High packets (>800) + high bytes (>50000) + failed connections (>15)
- **ICMP Flood**: High ICMP rate (>200)
- **Port Scan**: Many failed connections (>30)
- **Suspicious Activity**: Elevated metrics that don't match specific attacks
- **Normal**: All other traffic patterns

### Severity Levels

- **Critical**: Mirai Botnet
- **High**: UDP Flood, SYN Flood
- **Medium**: ICMP Flood, Port Scan
- **Low**: Suspicious Activity, Normal

## Testing the System

### Test with Python Script

```python
import requests
import time

API_ENDPOINT = "https://your-project.supabase.co/functions/v1/iot-ingest"
DEVICE_TOKEN = "your_device_token"

headers = {
    "Content-Type": "application/json",
    "X-Device-Token": DEVICE_TOKEN
}

telemetry = {
    "device_id": "test_device",
    "packets_per_sec": 1500,
    "failed_conn": 10,
    "bytes_sent": 45000,
    "tcp_flags": 3,
    "udp_rate": 800,
    "icmp_rate": 2
}

response = requests.post(API_ENDPOINT, json=telemetry, headers=headers)
print(response.json())
```

This will trigger a UDP Flood detection and send an email alert.

## Project Structure

```
project/
├── src/
│   ├── components/
│   │   ├── Auth.tsx              # Login/signup UI
│   │   ├── Layout.tsx            # Main layout with navigation
│   │   ├── Dashboard.tsx         # Statistics dashboard
│   │   ├── DeviceManager.tsx     # Device registration/management
│   │   └── DetectionLog.tsx      # Detection history table
│   ├── contexts/
│   │   └── AuthContext.tsx       # Authentication state management
│   ├── lib/
│   │   └── supabase.ts          # Supabase client configuration
│   ├── App.tsx                   # Main application component
│   └── main.tsx                  # Application entry point
├── supabase/
│   └── functions/
│       ├── iot-ingest/          # Telemetry ingestion function
│       └── send-alert/          # Email alert function
├── IOT_DEVICE_GUIDE.md          # IoT device integration guide
└── PROJECT_SETUP.md             # This file
```

## API Endpoints

### Ingest Telemetry
```
POST /functions/v1/iot-ingest
Headers: X-Device-Token
Body: Telemetry JSON
```

### Send Alert (Internal)
```
POST /functions/v1/send-alert
Body: Alert data
```

## Security Features

- Row Level Security (RLS) enabled on all tables
- Users can only access their own devices and detections
- Device token authentication for API access
- Password hashing via Supabase Auth
- Secure Edge Functions with CORS headers

## Upgrading the ML Model

To replace the rule-based classifier with a trained ML model:

1. Train your model using a dataset (e.g., CICIoT2023, IoT-23)
2. Export the model (e.g., as ONNX or TensorFlow.js)
3. Update the `classifyAttack` function in `iot-ingest/index.ts`
4. Redeploy the Edge Function

## Troubleshooting

### Issue: Can't sign up
- Check Supabase project is active
- Verify environment variables are correct
- Check browser console for errors

### Issue: Device registration fails
- Ensure you're logged in
- Check network connection
- Verify Supabase database is accessible

### Issue: Telemetry not being received
- Verify device token is correct
- Check API endpoint URL
- Ensure device has internet connection
- Review Edge Function logs in Supabase dashboard

### Issue: Email alerts not sending
- Email functionality logs to console (Supabase Edge Functions don't support SMTP by default)
- For production email, integrate with services like SendGrid, Resend, or AWS SES

## Future Enhancements

- Integration with real SMTP service for production email alerts
- Advanced ML model with TensorFlow.js or ONNX
- WebSocket support for real-time dashboard updates
- Multi-user roles (admin, viewer, operator)
- Historical trend analysis and reporting
- Device health monitoring
- Automated device onboarding via QR codes
- Mobile app (React Native)

## Support

For issues or questions:
1. Check the documentation
2. Review Supabase logs
3. Inspect browser console for errors
4. Check device logs for connectivity issues

## License

This project is for educational and defensive security purposes only.
