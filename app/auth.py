import pyotp
import qrcode
import io
from flask import Blueprint, render_template, redirect, url_for, flash, session, request, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User
from app import bcrypt

auth_bp = Blueprint('auth', __name__)

# User Registration Route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for('auth.register'))

        # Check if email or username already exists
        if User.query.filter_by(email=email).first():
            flash("Email is already registered!", "danger")
            return redirect(url_for('auth.register'))
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for('auth.register'))

        # Generate OTP Secret
        otp_secret = pyotp.random_base32()

        # Store user in DB
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password, otp_secret=otp_secret)
        db.session.add(new_user)
        db.session.commit()

        session['username'] = username  # Store username in session for QR code
        flash("Registration successful! Please set up 2FA.", "success")
        return redirect(url_for('auth.setup_2fa'))

    return render_template('auth/register.html')

# Setup 2FA Page
@auth_bp.route('/setup-2fa')
def setup_2fa():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash("Session expired. Please log in again.", "danger")
        return redirect(url_for('auth.login'))

    otp_uri = pyotp.totp.TOTP(user.otp_secret).provisioning_uri(user.username, issuer_name="ZTA_App")

    qr = qrcode.make(otp_uri)
    img_io = io.BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)
    qr_code_url = url_for('auth.qr_code', _external=True)

    return render_template('auth/setup-2fa.html', qr_code=qr_code_url, secret=user.otp_secret)

# Generate QR Code Image
@auth_bp.route('/qr_code')
def qr_code():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash("Session expired. Please log in again.", "danger")
        return redirect(url_for('auth.login'))

    otp_uri = pyotp.totp.TOTP(user.otp_secret).provisioning_uri(user.username, issuer_name="ZTA_App")

    qr = qrcode.make(otp_uri)
    img_io = io.BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

# Login Route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials, try again.", "danger")
            return redirect(url_for('auth.login'))

        session['username'] = username  # Store username for OTP verification
        return redirect(url_for('auth.verify_otp'))

    return render_template('auth/login.html')

# OTP Verification Route
@auth_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash("Session expired. Please log in again.", "danger")
        return redirect(url_for('auth.login'))

    totp = pyotp.TOTP(user.otp_secret)

    if request.method == 'POST':
        otp_code = request.form.get('otp')
        if totp.verify(otp_code):
            login_user(user)
            session.pop('username', None)
            flash("Login successful!", "success")
            if user.role == "admin":
                return redirect(url_for("admin.admin_dashboard"))
            else:
                return redirect(url_for('routes.dashboard'))
        else:
            flash('Invalid OTP', 'danger')

    return render_template('auth/verify_otp.html')

# Logout Route
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.login'))



@auth_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):  # Add user_id parameter
    user = User.query.get(user_id)  # Fetch user from database
    if not user:
        flash("User not found!", "error")
        return redirect(url_for('auth.login'))  # Redirect if user doesn't exist
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.role = request.form.get('role')

        new_password = request.form.get('password')
        if new_password:
            user.password_hash = generate_password_hash(new_password)  # Fix attribute name
        
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('auth.edit_user', user_id=user.id))  # Redirect after updating user

    otp_uri = pyotp.totp.TOTP(user.otp_secret).provisioning_uri(user.username, issuer_name="ZTA_App")
    qr_code_url = url_for('auth.qr_code', _external=True)

    return render_template('auth/edit-user.html', user=user, qr_code=qr_code_url)



