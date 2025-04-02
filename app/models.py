import pyotp
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from app import db


bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)  # Added email field
    password_hash = db.Column(db.String(256), nullable=False)
    otp_secret = db.Column(db.String(32), nullable=False, default=pyotp.random_base32)  # Cleaner default
    role = db.Column(db.String(20), nullable=False, default='user') 
    def __repr__(self):
        return f"<User {self.username}>"
    
    def set_password(self, password):
        """Hashes and stores the user's password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_otp_uri(self):
        """Returns a URI for setting up a 2FA app (Google Authenticator, Authy, etc.)."""
        issuer_name = "ZTA_Project"
        return f"otpauth://totp/{issuer_name}:{self.username}?secret={self.otp_secret}&issuer={issuer_name}"

    def verify_otp(self, otp_code):
        """Verifies the entered OTP code."""
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(otp_code)
    def is_admin(self):
        return self.role == 'admin'

