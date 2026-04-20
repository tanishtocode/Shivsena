from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
babel = Babel()


def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)

    if not app.config.get('SECRET_KEY'):
        raise RuntimeError("SECRET_KEY is not set!")

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'

    # 🌐 LANGUAGE SELECTOR
    def select_locale():
        return session.get('lang', 'en')

    babel.init_app(app, locale_selector=select_locale)

    # 🔗 BLUEPRINTS
    from app.routes.main import main
    from app.routes.complaint import complaints
    from app.routes.auth import auth

    app.register_blueprint(main)
    app.register_blueprint(complaints)
    app.register_blueprint(auth)

    # ✅ ADD THIS BLOCK (VERY IMPORTANT)
    from flask_babel import gettext
    app.jinja_env.globals['_'] = gettext

    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))