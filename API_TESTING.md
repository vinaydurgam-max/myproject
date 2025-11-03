# API Testing & Integration Guide

## Endpoint Reference

### IoT Data Ingestion Endpoint

```
POST https://{PROJECT_ID}.supabase.co/functions/v1/iot-ingest
```

**Required Headers:**
- `X-Device-Token`: Your device's authentication token
- `Content-Type: application/json`

**Request Body:**
```json
{
  "sbytes": 45000,
  "dbytes": 50000,
  "rate": 250,
  "dinpkt": 300,
  "tcprtt": 85,
  "synack": 42,
  "ackdat": 38,
  "smean": 0.45,
  "dmean": 0.52
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "detection_id": "uuid-string",
  "prediction": {
    "label": "Normal",
    "confidence": 0.99,
    "severity": "low",
    "risk_score": 0.0,
    "rules_fired": ["baseline_check"]
  },
  "timestamp": "2025-11-01T12:00:00.000Z"
}
```

**Response (Error - 401):**
```json
{
  "error": "Missing device token"
}
```

**Response (Error - 403):**
```json
{
  "error": "Invalid or inactive device token"
}
```

---

## Testing Scenarios

### Scenario 1: Normal Traffic

**Description**: Baseline normal network activity

```bash
curl -X POST \
  https://your-project.supabase.co/functions/v1/iot-ingest \
  -H "X-Device-Token: iot_abc123def456ghi789jkl012mno345pqr" \
  -H "Content-Type: application/json" \
  -d '{
    "sbytes": 45000,
    "dbytes": 50000,
    "rate": 250,
    "dinpkt": 300,
    "tcprtt": 85,
    "synack": 42,
    "ackdat": 38,
    "smean": 0.45,
    "dmean": 0.52
  }'
```

**Expected Result:**
```
Attack Type: Normal
Confidence: 0.99
Severity: low
Risk Score: 0.0
Rules Fired: baseline_check
```

---

### Scenario 2: DDoS Attack Detection

**Description**: Distributed Denial of Service with extreme packet rates and SYN flooding

```bash
curl -X POST \
  https://your-project.supabase.co/functions/v1/iot-ingest \
  -H "X-Device-Token: iot_abc123def456ghi789jkl012mno345pqr" \
  -H "Content-Type: application/json" \
  -d '{
    "sbytes": 450000,
    "dbytes": 350000,
    "rate": 5500,
    "dinpkt": 950,
    "tcprtt": 250,
    "synack": 250,
    "ackdat": 42,
    "smean": 0.48,
    "dmean": 0.51
  }'
```

**Expected Result:**
```
Attack Type: DDoS
Confidence: 0.98
Severity: critical
Risk Score: 0.95
Rules Fired: ["ddos_high_rate_synack"]
```

---

### Scenario 3: Malware (Command & Control)

**Description**: Highly asymmetric traffic typical of botnet C&C communication

```bash
curl -X POST \
  https://your-project.supabase.co/functions/v1/iot-ingest \
  -H "X-Device-Token: iot_abc123def456ghi789jkl012mno345pqr" \
  -H "Content-Type: application/json" \
  -d '{
    "sbytes": 125000,
    "dbytes": 450,
    "rate": 2200,
    "dinpkt": 650,
    "tcprtt": 580,
    "synack": 120,
    "ackdat": 25,
    "smean": 0.38,
    "dmean": 0.72
  }'
```

**Expected Result:**
```
Attack Type: Malware
Confidence: 0.97
Severity: critical
Risk Score: 0.88
Rules Fired: ["malware_asymmetric_traffic"]
```

---

### Scenario 4: DoS Attack

**Description**: Single-source denial of service with high latency and packet flooding

```bash
curl -X POST \
  https://your-project.supabase.co/functions/v1/iot-ingest \
  -H "X-Device-Token: iot_abc123def456ghi789jkl012mno345pqr" \
  -H "Content-Type: application/json" \
  -d '{
    "sbytes": 85000,
    "dbytes": 75000,
    "rate": 1800,
    "dinpkt": 900,
    "tcprtt": 1600,
    "synack": 150,
    "ackdat": 20,
    "smean": 0.42,
    "dmean": 0.58
  }'
```

**Expected Result:**
```
Attack Type: DoS
Confidence: 0.96
Severity: high
Risk Score: 0.85
Rules Fired: ["dos_high_rtt_packets"]
```

---

### Scenario 5: Man-in-the-Middle (MitM)

**Description**: Connection hijacking with ACK anomalies

```bash
curl -X POST \
  https://your-project.supabase.co/functions/v1/iot-ingest \
  -H "X-Device-Token: iot_abc123def456ghi789jkl012mno345pqr" \
  -H "Content-Type: application/json" \
  -d '{
    "sbytes": 55000,
    "dbytes": 60000,
    "rate": 800,
    "dinpkt": 400,
    "tcprtt": 1200,
    "synack": 180,
    "ackdat": 5,
    "smean": 0.50,
    "dmean": 0.55
  }'
```

**Expected Result:**
```
Attack Type: MitM
Confidence: 0.94
Severity: high
Risk Score: 0.82
Rules Fired: ["mitm_ack_missing"]
```

---

### Scenario 6: Phishing Attack

**Description**: Skewed data distribution suggesting credential harvesting

```bash
curl -X POST \
  https://your-project.supabase.co/functions/v1/iot-ingest \
  -H "X-Device-Token: iot_abc123def456ghi789jkl012mno345pqr" \
  -H "Content-Type: application/json" \
  -d '{
    "sbytes": 15000,
    "dbytes": 35000,
    "rate": 950,
    "dinpkt": 320,
    "tcprtt": 120,
    "synack": 25,
    "ackdat": 22,
    "smean": 0.25,
    "dmean": 0.80
  }'
```

**Expected Result:**
```
Attack Type: Phishing
Confidence: 0.92
Severity: medium
Risk Score: 0.65
Rules Fired: ["phishing_skewed_distribution"]
```

---

### Scenario 7: SQL Injection

**Description**: Database query manipulation attempt

```bash
curl -X POST \
  https://your-project.supabase.co/functions/v1/iot-ingest \
  -H "X-Device-Token: iot_abc123def456ghi789jkl012mno345pqr" \
  -H "Content-Type: application/json" \
  -d '{
    "sbytes": 28000,
    "dbytes": 75000,
    "rate": 2000,
    "dinpkt": 520,
    "tcprtt": 950,
    "synack": 120,
    "ackdat": 35,
    "smean": 0.38,
    "dmean": 0.65
  }'
```

**Expected Result:**
```
Attack Type: SQLInjection
Confidence: 0.90
Severity: high
Risk Score: 0.75
Rules Fired: ["sqli_high_rate_rtt"]
```

---

### Scenario 8: XSS (Cross-Site Scripting)

**Description**: Script injection with high-entropy payloads

```bash
curl -X POST \
  https://your-project.supabase.co/functions/v1/iot-ingest \
  -H "X-Device-Token: iot_abc123def456ghi789jkl012mno345pqr" \
  -H "Content-Type: application/json" \
  -d '{
    "sbytes": 18000,
    "dbytes": 42000,
    "rate": 1250,
    "dinpkt": 820,
    "tcprtt": 95,
    "synack": 35,
    "ackdat": 32,
    "smean": 0.32,
    "dmean": 0.75
  }'
```

**Expected Result:**
```
Attack Type: XSS
Confidence: 0.89
Severity: medium
Risk Score: 0.70
Rules Fired: ["xss_high_input_entropy"]
```

---

### Scenario 9: Spoofing / Password Attack

**Description**: IP spoofing or brute force login attempts

```bash
curl -X POST \
  https://your-project.supabase.co/functions/v1/iot-ingest \
  -H "X-Device-Token: iot_abc123def456ghi789jkl012mno345pqr" \
  -H "Content-Type: application/json" \
  -d '{
    "sbytes": 32000,
    "dbytes": 1500,
    "rate": 950,
    "dinpkt": 280,
    "tcprtt": 1800,
    "synack": 210,
    "ackdat": 8,
    "smean": 0.48,
    "dmean": 0.52
  }'
```

**Expected Result:**
```
Attack Type: SpoofingPasswordAttack
Confidence: 0.88
Severity: medium
Risk Score: 0.72
Rules Fired: ["spoofing_addr_spoofing"]
```

---

### Scenario 10: Zero-Day Exploit

**Description**: Extreme and anomalous parameter combination

```bash
curl -X POST \
  https://your-project.supabase.co/functions/v1/iot-ingest \
  -H "X-Device-Token: iot_abc123def456ghi789jkl012mno345pqr" \
  -H "Content-Type: application/json" \
  -d '{
    "sbytes": 200000,
    "dbytes": 180000,
    "rate": 3000,
    "dinpkt": 950,
    "tcprtt": 2500,
    "synack": 10,
    "ackdat": 8,
    "smean": 0.15,
    "dmean": 0.95
  }'
```

**Expected Result:**
```
Attack Type: ZeroDayExploit
Confidence: 0.85
Severity: critical
Risk Score: 0.90
Rules Fired: ["zeroday_extreme_parameters"]
```

---

### Scenario 11: Insider Threat

**Description**: Symmetric high-volume data exfiltration

```bash
curl -X POST \
  https://your-project.supabase.co/functions/v1/iot-ingest \
  -H "X-Device-Token: iot_abc123def456ghi789jkl012mno345pqr" \
  -H "Content-Type: application/json" \
  -d '{
    "sbytes": 95000,
    "dbytes": 92000,
    "rate": 1200,
    "dinpkt": 600,
    "tcprtt": 45,
    "synack": 85,
    "ackdat": 82,
    "smean": 0.50,
    "dmean": 0.51
  }'
```

**Expected Result:**
```
Attack Type: InsiderThreat
Confidence: 0.91
Severity: high
Risk Score: 0.78
Rules Fired: ["insider_high_symmetry"]
```

---

### Scenario 12: Social Engineering

**Description**: Atypical communication pattern

```bash
curl -X POST \
  https://your-project.supabase.co/functions/v1/iot-ingest \
  -H "X-Device-Token: iot_abc123def456ghi789jkl012mno345pqr" \
  -H "Content-Type: application/json" \
  -d '{
    "sbytes": 18000,
    "dbytes": 28000,
    "rate": 1000,
    "dinpkt": 280,
    "tcprtt": 150,
    "synack": 20,
    "ackdat": 18,
    "smean": 0.35,
    "dmean": 0.68
  }'
```

**Expected Result:**
```
Attack Type: SocialEngineering
Confidence: 0.86
Severity: low
Risk Score: 0.60
Rules Fired: ["se_low_complexity"]
```

---

## Batch Testing Script

### Python

```python
#!/usr/bin/env python3
import requests
import json
from datetime import datetime

BASE_URL = "https://your-project.supabase.co/functions/v1/iot-ingest"
DEVICE_TOKEN = "iot_your_token_here"

test_cases = {
    "normal": {
        "sbytes": 45000, "dbytes": 50000, "rate": 250,
        "dinpkt": 300, "tcprtt": 85, "synack": 42,
        "ackdat": 38, "smean": 0.45, "dmean": 0.52
    },
    "ddos": {
        "sbytes": 450000, "dbytes": 350000, "rate": 5500,
        "dinpkt": 950, "tcprtt": 250, "synack": 250,
        "ackdat": 42, "smean": 0.48, "dmean": 0.51
    },
    "malware": {
        "sbytes": 125000, "dbytes": 450, "rate": 2200,
        "dinpkt": 650, "tcprtt": 580, "synack": 120,
        "ackdat": 25, "smean": 0.38, "dmean": 0.72
    },
}

headers = {
    "X-Device-Token": DEVICE_TOKEN,
    "Content-Type": "application/json"
}

for test_name, payload in test_cases.items():
    try:
        response = requests.post(BASE_URL, json=payload, headers=headers)
        result = response.json()

        print(f"\n[{datetime.now().isoformat()}] Test: {test_name}")
        print(f"Status: {response.status_code}")
        print(f"Attack Type: {result.get('prediction', {}).get('label')}")
        print(f"Confidence: {result.get('prediction', {}).get('confidence')}")
        print(f"Severity: {result.get('prediction', {}).get('severity')}")

    except Exception as e:
        print(f"Error testing {test_name}: {e}")
```

### Bash

```bash
#!/bin/bash

BASE_URL="https://your-project.supabase.co/functions/v1/iot-ingest"
DEVICE_TOKEN="iot_your_token_here"

# Array of test cases
declare -a tests=("normal" "ddos" "malware")

for test in "${tests[@]}"; do
  echo "Testing: $test"

  case $test in
    normal)
      DATA='{"sbytes":45000,"dbytes":50000,"rate":250,"dinpkt":300,"tcprtt":85,"synack":42,"ackdat":38,"smean":0.45,"dmean":0.52}'
      ;;
    ddos)
      DATA='{"sbytes":450000,"dbytes":350000,"rate":5500,"dinpkt":950,"tcprtt":250,"synack":250,"ackdat":42,"smean":0.48,"dmean":0.51}'
      ;;
    malware)
      DATA='{"sbytes":125000,"dbytes":450,"rate":2200,"dinpkt":650,"tcprtt":580,"synack":120,"ackdat":25,"smean":0.38,"dmean":0.72}'
      ;;
  esac

  curl -X POST "$BASE_URL" \
    -H "X-Device-Token: $DEVICE_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$DATA" | jq .

  echo "---"
done
```

---

## Debugging Tips

### Check Response Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Detection processed |
| 400 | Bad Request | Check JSON format |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Device inactive/token wrong |
| 500 | Server Error | Check Supabase logs |

### Validate JSON

```bash
curl -X POST ... -d @payload.json --header "Content-Type: application/json"
```

### Test Token Authorization

```bash
# This should fail
curl -X POST https://your-project.supabase.co/functions/v1/iot-ingest \
  -H "Content-Type: application/json" \
  -d '{"sbytes":45000}'

# This should succeed
curl -X POST https://your-project.supabase.co/functions/v1/iot-ingest \
  -H "X-Device-Token: iot_your_token" \
  -H "Content-Type: application/json" \
  -d '{"sbytes":45000,"dbytes":50000,"rate":250,"dinpkt":300,"tcprtt":85,"synack":42,"ackdat":38,"smean":0.45,"dmean":0.52}'
```

### Monitor in Real-Time

Use Supabase dashboard to:
1. View Edge Function logs
2. Query detections table
3. Check alerts table for email status

---

## Performance Benchmarks

- **Response Time**: < 200ms per request
- **Throughput**: 20+ requests/second
- **Database Write**: Indexed on device_id and timestamp
- **Concurrent Users**: 100+ simultaneous connections

---

## Integration Examples

### Node.js / JavaScript

```javascript
async function sendTelemetry(metrics) {
  const response = await fetch(
    `${process.env.SUPABASE_URL}/functions/v1/iot-ingest`,
    {
      method: 'POST',
      headers: {
        'X-Device-Token': process.env.DEVICE_TOKEN,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(metrics),
    }
  );
  return response.json();
}
```

### Python

```python
import requests

def send_telemetry(metrics, token, url):
    headers = {
        'X-Device-Token': token,
        'Content-Type': 'application/json'
    }
    response = requests.post(f'{url}/functions/v1/iot-ingest',
                            json=metrics, headers=headers)
    return response.json()
```

### C / Arduino

```cpp
HTTPClient http;
http.addHeader("X-Device-Token", device_token);
http.addHeader("Content-Type", "application/json");
String payload = "{\"sbytes\":45000,...}";
int httpCode = http.POST(payload);
```
