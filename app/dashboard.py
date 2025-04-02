from flask import Blueprint, render_template, redirect
from flask_login import login_required, current_user
from app.zta import enforce_zero_trust

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard')
@login_required
def user_dashboard():
    zta_check = enforce_zero_trust()
    if zta_check:
        return zta_check  # Redirect if Zero Trust check fails

    return render_template('dashboard.html', username=current_user.username)
