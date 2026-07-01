from flask import Flask, g
from .config import Config
from .database import init_db, close_db, get_db
from .auth import auth_bp, load_logged_in_user, csrf_token
from .dashboard import dashboard_bp
from .admin import admin_bp
from .api import api_bp


def create_app():
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder="static",
        template_folder="templates",
    )
    app.config.from_object(Config)
    app.secret_key = app.config["SECRET_KEY"]

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    app.teardown_appcontext(close_db)
    app.before_request(load_logged_in_user)

    app.jinja_env.globals["csrf_token"] = csrf_token

    with app.app_context():
        init_db()

    return app
