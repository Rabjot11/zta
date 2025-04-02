from flask import redirect, url_for, session
from flask_login import current_user
import time

# Sample roles (Replace with a real database)
USER_ROLES = {
    "admin": ["dashboard", "settings"],
    "user": ["dashboard"],
}

def get_device_id():
    """Generate a unique device fingerprint."""
    user_agent = request.headers.get('User-Agent', '')
    ip_address = request.remote_addr or '0.0.0.0'
    raw_data = f"{user_agent}|{ip_address}"
    return hashlib.sha256(raw_data.encode()).hexdigest()


def enforce_zero_trust():
    """Enforce Zero Trust security checks."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    # Check if user has a stored device ID
    stored_device_id = session.get('device_id')
    current_device_id = get_device_id()

    if stored_device_id and stored_device_id != current_device_id:
        session.clear()
        return redirect(url_for('auth.logout'))

    # Store device ID for the session
    session['device_id'] = current_device_id

    # Check session timeout (5 minutes idle)
    if 'last_active' in session and (time.time() - session['last_active']) > 300:
        session.clear()
        return redirect(url_for('auth.logout'))

    session['last_active'] = time.time()

FAILED_ATTEMPTS = {}

def track_failed_logins(username):
    """Track failed login attempts and block if necessary."""
    now = time.time()
    if username not in FAILED_ATTEMPTS:
        FAILED_ATTEMPTS[username] = []

    # Remove old failed attempts (older than 5 minutes)
    FAILED_ATTEMPTS[username] = [t for t in FAILED_ATTEMPTS[username] if now - t < 300]

    # Add current failed attempt
    FAILED_ATTEMPTS[username].append(now)

    # Block if more than 3 failed attempts
    if len(FAILED_ATTEMPTS[username]) >= 3:
        log_event(username, "ACCOUNT_LOCKED", "Too many failed login attempts")
        return True  # User should be blocked

    return False

def enforce_endpoint_security():
    """
    Enforces Zero Trust security policies on API endpoints.
    This function should include checks like user authentication, 
    device trust verification, and IP validation.
    """
    print("Enforcing Zero Trust policies...")
    return True  # Modify this based on actual security checks
