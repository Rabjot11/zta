from flask import Blueprint, render_template, send_from_directory, jsonify, request
from flask_login import login_required, current_user
from app.decorators import role_required
from app.models import User  # Ensure User model is imported
import qrcode
import io
import base64
import pyotp


bp = Blueprint("routes", __name__)

@bp.route("/")
def home():
    return render_template("index.html")

@bp.route("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/vnd.microsoft.icon")

@bp.route("/login")
def login():
    return render_template("auth/login.html")


@bp.route("/register")
def register():
    return render_template("auth/register.html")

@bp.route("/login/options")
def login_options():
    return jsonify({
        "status": "ok",
        "message": "WebAuthn options will be handled here."
    })

# Admin Dashboard Route (Accessible only to admins)

# User List API (Accessible only to admins)
@bp.route("/api/users", methods=["GET"])
@login_required
@role_required("admin")
def get_users():
    try:
        users = User.query.all()
        return jsonify([{"id": u.id, "username": u.username, "role": u.role} for u in users])
    except Exception as e:
        return jsonify({"error": "Failed to fetch users", "details": str(e)}), 500


@bp.route("/dashboard")
@login_required
def dashboard():
   # ✅ Generate OTP URI
    otp_uri = pyotp.TOTP(current_user.otp_secret).provisioning_uri(
        name=current_user.email, issuer_name="ZTA_App"
    )

    # ✅ Generate QR Code
    qr = qrcode.make(otp_uri)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render_template("dashboard.html", username=current_user.username, qr_code=f"data:image/png;base64,{qr_base64}")
