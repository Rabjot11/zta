import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# Configure logging
logging.basicConfig(
    filename='access.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

ALERT_EMAIL = "admin@example.com"  # Change this to your email

def send_alert(subject, message):
    """Send an alert email to the admin."""
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = "zta-monitor@example.com"
    msg["To"] = ALERT_EMAIL

    try:
        server = smtplib.SMTP("localhost")  # Change to your SMTP server
        server.sendmail("zta-monitor@example.com", [ALERT_EMAIL], msg.as_string())
        server.quit()
    except Exception as e:
        logging.error(f"Failed to send alert: {e}")

def log_event(username, event_type, details=""):
    """Log security-related events and send alerts for critical issues."""
    message = f"User: {username} | Event: {event_type} | Details: {details}"
    logging.info(message)

    if event_type in ["FAILED_LOGIN", "ACCOUNT_LOCKED"]:
        send_alert(f"Security Alert: {event_type}", message)