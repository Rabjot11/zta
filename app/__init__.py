from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # Redirect to login if not authenticated

def create_app():
    app = Flask(__name__,template_folder="templates")
    app.config.from_object(Config)  # Load configuration first

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)  # Migration support
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Import blueprints inside the function to avoid circular imports
    from app.routes import bp as main_bp  # Main routes
    from app.auth import auth_bp  # Authentication routes
    from app.admin import admin_bp  # Admin routes
    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    from app.models import User  # Import here to avoid circular imports
    return User.query.get(int(user_id))

