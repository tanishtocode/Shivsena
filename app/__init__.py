from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect   # SECURITY FIX: added CSRF protection
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()                     # SECURITY FIX: CSRF instance


def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)

    # SECURITY FIX: raise error on startup if SECRET_KEY is not set
    if not app.config.get('SECRET_KEY'):
        raise RuntimeError(
            "SECRET_KEY is not set! Add it to your .env file before running."
        )

    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB max
    app.config['ALLOWED_IMAGE_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp'}

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)                   # SECURITY FIX: activate CSRF on all POST forms
    login_manager.login_view = 'auth.login'

    # Import models so SQLAlchemy knows all tables
    from app.models import User, Complaint, SocialWorkImage

    from app.routes.main import main
    from app.routes.complaint import complaints
    from app.routes.auth import auth

    app.register_blueprint(main)
    app.register_blueprint(complaints)
    app.register_blueprint(auth)

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))