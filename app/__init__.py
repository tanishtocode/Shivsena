from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)

    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB max
    app.config['ALLOWED_IMAGE_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp'}

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # IMPORTANT: import models so SQLAlchemy knows all tables
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