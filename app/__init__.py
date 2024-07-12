from flask import Flask, render_template, session, request, redirect, url_for
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

    @app.route("/")
    def index():
        return render_template("admin/index.jinja2", title="WISE IT API Server")

    from .routes.admin.main import admin_bp
    from .routes.admin.qaboard import qaboard_bp
    from .routes.api.sqool_artist import sqool_artist_bp
    from .routes.api.qaboard import qaboard_api_bp
    from .routes.api.user import user_api_bp
    from .routes.api.common import common_api_bp

    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(qaboard_bp, url_prefix="/admin/qaboard")
    app.register_blueprint(sqool_artist_bp, url_prefix="/api/sqool/artist")
    app.register_blueprint(qaboard_api_bp, url_prefix="/api/qaboard")
    app.register_blueprint(user_api_bp, url_prefix="/api/user")
    app.register_blueprint(common_api_bp, url_prefix="/api/common")

    # ! 페이지 접근 권한 설정
    @app.before_request
    def require_login():
        allowed_routes = [
            "static",
            "index",
            "admin.admin_index",
            "admin.admin_login",
            "admin.admin_register",
            "common_api.ping",
            "qaboard_api.ping",
            "user_api.ping",
            "sqool_artist.execute_query",
            "sqool_artist.reset_database",
        ]
        if "admin_user" not in session and request.endpoint not in allowed_routes:
            return redirect(url_for("index"))

    return app
