import serial, time, json

arduino = serial.Serial('COM5', 9600, timeout=2)
time.sleep(2)

print("✅ Connected to Arduino!")

# Wait for Arduino ready message
while True:
    line = arduino.readline().decode().strip()
    if line:
        print("Received:", line)
        if '"arduino_ready"' in line:
            print("🔗 Arduino ready detected!")
            break

# Send CONNECTED command
msg = {"cmd": "CONNECTED", "data": {}}
arduino.write((json.dumps(msg) + "\n").encode())

# Display test message
time.sleep(2)
msg = {"cmd": "DISPLAY", "data": {"line1": "System", "line2": "Connected"}}
arduino.write((json.dumps(msg) + "\n").encode())
print("📟 Display command sent!")
