from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash("Unauthorized Access!", "danger")
                return redirect(url_for("main.index"))
            return func(*args, **kwargs)
        return wrapper
    return decorator
