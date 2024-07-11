from flask import Flask, session, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from .config import Config


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    from .routes.admin.main import admin_bp
    from .routes.admin.qaboard import qaboard_bp
    from .routes.api.sqool_artist import sqool_artist_bp

    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(qaboard_bp, url_prefix="/admin/qaboard")
    app.register_blueprint(sqool_artist_bp, url_prefix="/api/sqool/artist")

    @app.before_request
    def require_login():
        allowed_routes = [
            "admin.admin_login",
            "admin.admin_register",
            "admin.admin_logout",
            "static",
            "sqool_artist.execute_query",
            "sqool_artist.reset_database",
        ]
        if "admin_user" not in session and request.endpoint not in allowed_routes:
            return redirect(url_for("admin.admin_login"))

    return app
