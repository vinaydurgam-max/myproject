import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class EmailAlertSystem:
    """Email alert system for attack notifications."""

    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.admin_email = os.getenv('ADMIN_EMAIL')

    def send_attack_alert(self, device_name: str, attack_type: str, severity: str,
                         indicators: list, recommendations: list) -> bool:
        """Send attack alert email to admin."""
        if not all([self.sender_email, self.sender_password, self.admin_email]):
            print("Warning: Email configuration incomplete. Skipping email alert.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.admin_email
            msg['Subject'] = f'IoT Security Alert: {attack_type} detected on {device_name}'

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            body = f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
      <h2 style="color: #dc3545;">SECURITY ALERT</h2>

      <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
        <h3>Attack Details</h3>
        <table style="width: 100%;">
          <tr>
            <td style="padding: 8px;"><strong>Device:</strong></td>
            <td style="padding: 8px;">{device_name}</td>
          </tr>
          <tr>
            <td style="padding: 8px;"><strong>Attack Type:</strong></td>
            <td style="padding: 8px;"><span style="background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 3px;">{attack_type}</span></td>
          </tr>
          <tr>
            <td style="padding: 8px;"><strong>Severity:</strong></td>
            <td style="padding: 8px;"><span style="background-color: {'#dc3545' if severity == 'Critical' else '#fd7e14'}; color: white; padding: 5px 10px; border-radius: 3px;">{severity}</span></td>
          </tr>
          <tr>
            <td style="padding: 8px;"><strong>Timestamp:</strong></td>
            <td style="padding: 8px;">{timestamp}</td>
          </tr>
        </table>
      </div>

      <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
        <h3>Detection Indicators</h3>
        <ul>
          {''.join(f'<li>{ind}</li>' for ind in indicators)}
        </ul>
      </div>

      <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
        <h3>Recommended Actions</h3>
        <ol>
          {''.join(f'<li>{rec}</li>' for rec in recommendations)}
        </ol>
      </div>

      <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #ffc107;">
        <strong>IMMEDIATE ACTION REQUIRED</strong>
        <p>Please take immediate action to address this security threat. Check the dashboard for more details and access the device for further investigation.</p>
      </div>
    </div>
  </body>
</html>
            """

            msg.attach(MIMEMultipart('alternative'))
            msg['Content-Type'] = 'text/html; charset=utf-8'
            msg.attach(MIMEText(body, 'html'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            print(f"Alert email sent successfully to {self.admin_email}")
            return True

        except Exception as e:
            print(f"Error sending email alert: {str(e)}")
            return False

    def send_connection_alert(self, device_name: str) -> bool:
        """Send device connection notification."""
        if not all([self.sender_email, self.sender_password, self.admin_email]):
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.admin_email
            msg['Subject'] = f'Device Connected: {device_name}'

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            body = f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <div style="background-color: #d4edda; padding: 20px; border-radius: 5px;">
      <h2 style="color: #155724;">Device Connected Successfully</h2>
      <p><strong>Device:</strong> {device_name}</p>
      <p><strong>Connection Time:</strong> {timestamp}</p>
      <p>The device has been connected and is now being monitored for security threats.</p>
    </div>
  </body>
</html>
            """

            msg.attach(MIMEMultipart('alternative'))
            msg['Content-Type'] = 'text/html; charset=utf-8'
            msg.attach(MIMEText(body, 'html'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"Error sending connection alert: {str(e)}")
            return False


def send_attack_alert(device_name: str, attack_type: str, severity: str,
                      indicators: list, recommendations: list) -> bool:
    """Wrapper function for sending attack alerts."""
    alert_system = EmailAlertSystem()
    return alert_system.send_attack_alert(device_name, attack_type, severity, indicators, recommendations)
