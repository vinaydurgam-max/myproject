import serial
import serial.tools.list_ports
import threading
import time
import json
from typing import Optional, Callable
from database import register_arduino_connection, update_arduino_heartbeat


class ArduinoManager:
    """Manages Arduino communication via serial port."""

    def __init__(self, baudrate: int = 9600):
        self.baudrate = baudrate
        self.serial_port: Optional[serial.Serial] = None
        self.port_name: Optional[str] = None
        self.is_connected = False
        self.read_thread: Optional[threading.Thread] = None
        self.device_id: Optional[int] = None
        self.on_message_callback: Optional[Callable] = None
        self.last_heartbeat = time.time()

    def find_arduino_ports(self) -> list:
        """Find available Arduino ports."""
        ports = []
        for port in serial.tools.list_ports.comports():
            if 'Arduino' in port.description or 'USB' in port.description or 'CH340' in port.description:
                ports.append({
                    'port': port.device,
                    'description': port.description,
                    'manufacturer': port.manufacturer
                })
        return ports

    def connect(self, port: Optional[str] = None, device_id: Optional[int] = None) -> bool:
        """Connect to Arduino on specified or auto-detected port."""
        try:
            if port is None:
                ports = self.find_arduino_ports()
                if not ports:
                    print("❌ No Arduino ports detected.")
                    return False
                port = ports[0]['port']

            print(f"🔌 Attempting to connect to Arduino on {port}...")
            self.serial_port = serial.Serial(port, self.baudrate, timeout=1)
            self.port_name = port
            self.device_id = device_id
            self.is_connected = True

            register_arduino_connection(port, device_id)
            print(f"✅ Connected to Arduino on {port}")

            self._send_command("CONNECTED", {"status": "connected", "device_id": device_id})

            # Start reading thread
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()

            # Send handshake message
            time.sleep(2)
            self.send_handshake()
            return True

        except Exception as e:
            print(f"⚠️ Error connecting to Arduino: {str(e)}")
            self.is_connected = False
            return False

    def send_handshake(self):
        """Send initial handshake message to confirm communication."""
        print("🤝 Sending handshake to Arduino...")
        self._send_command("HELLO", {"msg": "Python connected"})
        time.sleep(1)
        self._send_command("STATUS", {"device": "IoT Backend", "ip": "Connected"})

    def disconnect(self):
        """Disconnect from Arduino."""
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
                self.is_connected = False
                print(f"🔌 Disconnected from Arduino on {self.port_name}")
            except Exception as e:
                print(f"⚠️ Error disconnecting from Arduino: {str(e)}")

    def send_display_command(self, line1: str, line2: str) -> bool:
        """Send display content to Arduino LCD."""
        return self._send_command("DISPLAY", {
            "line1": line1[:16],
            "line2": line2[:16]
        })

    def send_clear_display(self) -> bool:
        """Clear Arduino LCD display."""
        return self._send_command("CLEAR", {})

    def send_attack_alert(self, attack_type: str, severity: str) -> bool:
        """Send attack alert to Arduino."""
        return self._send_command("ALERT", {
            "attack": attack_type[:16],
            "severity": severity[:8]
        })

    def send_normal_status(self, device_name: str, ip_address: str) -> bool:
        """Send normal device status to Arduino."""
        return self._send_command("STATUS", {
            "device": device_name[:16],
            "ip": ip_address[:16]
        })

    def _send_command(self, cmd: str, data: dict) -> bool:
        """Send JSON command to Arduino."""
        if not self.is_connected or not self.serial_port or not self.serial_port.is_open:
            print("⚠️ Arduino not connected")
            return False

        try:
            message = {
                "cmd": cmd,
                "data": data,
                "timestamp": round(time.time(), 2)
            }
            json_str = json.dumps(message) + "\n"
            self.serial_port.write(json_str.encode('utf-8'))
            print(f"➡️ Sent to Arduino: {json_str.strip()}")
            return True
        except Exception as e:
            print(f"⚠️ Error sending command to Arduino: {str(e)}")
            return False

    def _read_loop(self):
        """Read messages from Arduino in background."""
        while self.is_connected:
            try:
                if self.serial_port and self.serial_port.is_open and self.serial_port.in_waiting:
                    line = self.serial_port.readline().decode(errors='ignore').strip()
                    if line:
                        try:
                            message = json.loads(line)
                            print(f"⬅️ Received from Arduino: {message}")
                            update_arduino_heartbeat(self.port_name)
                            self.last_heartbeat = time.time()

                            if self.on_message_callback:
                                self.on_message_callback(message)

                            # Auto response if Arduino says it's ready
                            if message.get("status") == "arduino_ready":
                                print("🔗 Arduino ready detected — updating display.")
                                self.send_display_command("Connected", "IoT Backend OK")

                        except json.JSONDecodeError:
                            print(f"⚠️ Invalid JSON from Arduino: {line}")
                else:
                    # Auto reconnect every 5s if disconnected
                    if not self.serial_port or not self.serial_port.is_open:
                        print("🔁 Attempting auto-reconnect...")
                        self.connect(self.port_name)
                time.sleep(0.1)
            except Exception as e:
                print(f"⚠️ Error reading from Arduino: {str(e)}")
                break

    def set_message_callback(self, callback: Callable):
        """Set callback for received messages."""
        self.on_message_callback = callback

    def get_status(self) -> dict:
        """Get connection status."""
        return {
            "connected": self.is_connected,
            "port": self.port_name,
            "device_id": self.device_id,
            "baudrate": self.baudrate,
            "last_heartbeat": self.last_heartbeat
        }


# Global Arduino manager instance
arduino_manager = ArduinoManager()


def initialize_arduino(port: Optional[str] = None, device_id: Optional[int] = None) -> bool:
    """Initialize Arduino connection."""
    return arduino_manager.connect(port, device_id)


def get_arduino_status() -> dict:
    """Get Arduino connection status."""
    return arduino_manager.get_status()


def send_to_arduino_display(device_name: str, ip_address: str) -> bool:
    """Send normal device status to Arduino display."""
    return arduino_manager.send_normal_status(device_name, ip_address)


def send_attack_to_arduino(attack_type: str, severity: str) -> bool:
    """Send attack alert to Arduino."""
    return arduino_manager.send_attack_alert(attack_type, severity)


def clear_arduino_display() -> bool:
    """Clear Arduino display."""
    return arduino_manager.send_clear_display()
