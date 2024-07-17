from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from .config import Config


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
cors_origins = ["*"]


def create_app():
    app = Flask(__name__)

    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    @app.route("/")
    def index():
        return jsonify({"error": "접근 권한이 없습니다."}), 403

    from .routes.admin.main import admin_bp
    from .routes.admin.qaboard import qaboard_bp
    from .routes.admin.api_endpoint import api_endpoint_bp
    from .routes.admin.api_test import api_test_bp
    from .routes.api.sqool_db import sqool_db_bp
    from .routes.api.qaboard import qaboard_api_bp
    from .routes.api.user import user_api_bp
    from .routes.api.common import common_api_bp

    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(qaboard_bp, url_prefix="/admin/qaboard")
    app.register_blueprint(api_endpoint_bp, url_prefix="/admin/api_endpoint")
    app.register_blueprint(api_test_bp, url_prefix="/admin/api_test")
    app.register_blueprint(sqool_db_bp, url_prefix="/api/sqool")
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
            "user_api.ping",
            "qaboard_api.ping",
            "common_api.ping",
            "common_api.upload_image",
            "common_api.upload_thumbnail",
            "common_api.upload_file",
            "common_api.delete_file",
            "sqool_db.create_db",
            "sqool_db.get_schema",
            "sqool_db.start_query",
            "sqool_db.execute_query",
        ]
        if "admin_user" not in session and request.endpoint not in allowed_routes:
            return redirect(url_for("index"))

    return app
