# IoT Device Integration Guide

This guide explains how to integrate your IoT devices (ESP32, ESP8266, or any device capable of HTTP requests) with the IoT Security System.

## Prerequisites

1. Your device registered in the web dashboard
2. Device token copied from the dashboard
3. Device capable of making HTTP POST requests

## API Endpoint

```
POST https://your-supabase-project.supabase.co/functions/v1/iot-ingest
```

## Headers

```
X-Device-Token: your_device_token_here
Content-Type: application/json
```

## Telemetry Data Format

Send the following JSON structure:

```json
{
  "device_id": "esp32_001",
  "packets_per_sec": 340,
  "failed_conn": 12,
  "bytes_sent": 18000,
  "tcp_flags": 4,
  "udp_rate": 300,
  "icmp_rate": 0
}
```

### Field Descriptions

- **device_id**: Your device identifier (string)
- **packets_per_sec**: Network packets per second (number)
- **failed_conn**: Number of failed connections (number)
- **bytes_sent**: Bytes transmitted (number)
- **tcp_flags**: TCP flag count (number)
- **udp_rate**: UDP packets per second (number)
- **icmp_rate**: ICMP packets per second (number)

## Example: ESP32 Arduino Code

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* apiEndpoint = "https://your-project.supabase.co/functions/v1/iot-ingest";
const char* deviceToken = "iot_your_device_token_here";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    http.begin(apiEndpoint);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Device-Token", deviceToken);

    StaticJsonDocument<256> doc;
    doc["device_id"] = "esp32_001";
    doc["packets_per_sec"] = random(100, 500);
    doc["failed_conn"] = random(0, 20);
    doc["bytes_sent"] = random(10000, 30000);
    doc["tcp_flags"] = random(0, 10);
    doc["udp_rate"] = random(50, 350);
    doc["icmp_rate"] = random(0, 50);

    String jsonString;
    serializeJson(doc, jsonString);

    int httpResponseCode = http.POST(jsonString);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response: " + response);
    } else {
      Serial.println("Error: " + String(httpResponseCode));
    }

    http.end();
  }

  delay(5000);
}
```

## Example: Python Script

```python
import requests
import random
import time

API_ENDPOINT = "https://your-project.supabase.co/functions/v1/iot-ingest"
DEVICE_TOKEN = "iot_your_device_token_here"

headers = {
    "Content-Type": "application/json",
    "X-Device-Token": DEVICE_TOKEN
}

while True:
    telemetry = {
        "device_id": "sensor_001",
        "packets_per_sec": random.randint(100, 500),
        "failed_conn": random.randint(0, 20),
        "bytes_sent": random.randint(10000, 30000),
        "tcp_flags": random.randint(0, 10),
        "udp_rate": random.randint(50, 350),
        "icmp_rate": random.randint(0, 50)
    }

    try:
        response = requests.post(API_ENDPOINT, json=telemetry, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

    time.sleep(5)
```

## Simulating Attack Patterns

### Normal Traffic
```json
{
  "packets_per_sec": 250,
  "failed_conn": 3,
  "bytes_sent": 15000,
  "tcp_flags": 2,
  "udp_rate": 100,
  "icmp_rate": 5
}
```

### UDP Flood Attack
```json
{
  "packets_per_sec": 1500,
  "failed_conn": 10,
  "bytes_sent": 45000,
  "tcp_flags": 3,
  "udp_rate": 800,
  "icmp_rate": 2
}
```

### SYN Flood Attack
```json
{
  "packets_per_sec": 600,
  "failed_conn": 35,
  "bytes_sent": 25000,
  "tcp_flags": 15,
  "udp_rate": 150,
  "icmp_rate": 1
}
```

### Mirai Botnet Simulation
```json
{
  "packets_per_sec": 1200,
  "failed_conn": 25,
  "bytes_sent": 65000,
  "tcp_flags": 8,
  "udp_rate": 400,
  "icmp_rate": 3
}
```

## Response Format

### Success Response
```json
{
  "success": true,
  "prediction": {
    "label": "UDP Flood",
    "confidence": 0.92,
    "severity": "high"
  },
  "timestamp": "2025-10-31T12:34:56.789Z"
}
```

### Error Response
```json
{
  "error": "Invalid or inactive device token"
}
```

## Attack Labels

The system can detect the following attack types:

- **Normal** - Regular network traffic
- **Mirai Botnet** - Mirai malware infection
- **UDP Flood** - UDP-based DDoS attack
- **SYN Flood** - TCP SYN flood attack
- **ICMP Flood** - ICMP ping flood
- **Port Scan** - Port scanning activity
- **Suspicious Activity** - Unusual but unclassified behavior

## Severity Levels

- **low** - Minor anomaly
- **medium** - Moderate threat
- **high** - Serious threat
- **critical** - Critical threat requiring immediate action

## Email Alerts

When an attack is detected (any label except "Normal"), the system automatically:
1. Records the detection in the database
2. Sends an email alert to the device owner
3. Displays the alert in the dashboard

## Troubleshooting

### 401 Error - Missing Device Token
- Ensure the `X-Device-Token` header is included
- Check that the token is correct

### 403 Error - Invalid Token
- Verify the device is registered in the dashboard
- Check that the device is active (not disabled)
- Confirm you're using the correct token

### 500 Error - Server Error
- Check the telemetry data format
- Ensure all required fields are included
- Verify data types are correct

## Best Practices

1. Send telemetry every 5-10 seconds for real-time monitoring
2. Store the device token securely on your device
3. Handle network errors gracefully with retry logic
4. Monitor the dashboard for attack alerts
5. Review detection logs regularly
