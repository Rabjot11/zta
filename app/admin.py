from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models import User, db
from werkzeug.security import generate_password_hash
import qrcode
import io
import base64
import pyotp

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Admin Dashboard Route
@admin_bp.route('/admin-dashboard')
@login_required
def admin_dashboard():
    users = User.query.all()
    user_count = User.query.count()
    doc_count = 100  # Placeholder
    revenue = 5000  # Placeholder
   # ✅ Generate OTP URI
    otp_uri = pyotp.TOTP(current_user.otp_secret).provisioning_uri(
        name=current_user.email, issuer_name="ZTA_App"
    )

    # ✅ Generate QR Code
    qr = qrcode.make(otp_uri)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    return render_template(
        'admin/admin_dashboard.html',
        users=users,
        user_count=user_count,
        doc_count=doc_count,
        revenue=revenue, qr_code=f"data:image/png;base64,{qr_base64}"
    )

# Get all users
@admin_bp.route('/get_users')
@login_required
def get_users():
    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username, "email": user.email, "role": user.role} for user in users]
    return jsonify(user_list)

# Delete a user
@admin_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    return jsonify({"message": "User not found"}), 404


@admin_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    if request.method == "GET":
        # Ensure OTP secret exists for the user
        if not user.otp_secret:
            user.otp_secret = pyotp.random_base32()
            db.session.commit()

        otp_uri = pyotp.TOTP(user.otp_secret).provisioning_uri(
            name=user.email, issuer_name="ZTA_App"
        )

        # Generate QR Code
        buffer = io.BytesIO()
        qr = qrcode.make(otp_uri)
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "qr_code": f"data:image/png;base64,{qr_base64}"
        })

    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid data"}), 400

        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        user.role = data.get("role", user.role)

        db.session.commit()

        # Generate QR Code again (if needed)
        otp_uri = pyotp.TOTP(user.otp_secret).provisioning_uri(
            name=user.email, issuer_name="ZTA_App"
        )
        buffer = io.BytesIO()
        qr = qrcode.make(otp_uri)
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return jsonify({
            "success": True,
            "qr_code": f"data:image/png;base64,{qr_base64}",
            "message": "User updated successfully!"
        })


@admin_bp.route("/add_user", methods=["POST"])
def add_user():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "Invalid JSON data"}), 400

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")

        if not username or not email or not password or not role:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"success": False, "error": "User already exists"}), 400

        # Create new user and generate QR code
        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)  # Ensure password is being hashed
        db.session.add(new_user)
        db.session.commit()

        # Generate QR Code (Ensure QR code function is working)
        # Generate QR Code (Ensure QR code function is working)
        otp_secret = pyotp.random_base32()
        otp_uri = pyotp.TOTP(otp_secret).provisioning_uri(name=email, issuer_name="ZTA_App")
        qr = qrcode.make(otp_uri)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        print("Generated QR Code Base64:", qr_base64[:50])  # Debug

        return jsonify({"success": True, "message": "User added successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        print("Error adding user:", str(e))  # Log error in terminal
        return jsonify({"success": False, "error": str(e)}), 500
