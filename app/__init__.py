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

    CORS(
        app, resources={r"/api/*": {"origins": cors_origins}}, supports_credentials=True
    )

    app.config.from_object(Config)
    app.config["SESSION_COOKIE_SECURE"] = True  # HTTPS를 사용하는 경우
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "None"

    # SQooL DB 커넥션 타임아웃 설정
    app.config.setdefault("DB_CONNECTION_TIMEOUT", 3600)  # 기본 타임아웃 1시간

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    @app.route("/")
    def index():
        return jsonify({"error": "접근 권한이 없습니다."}), 403

    from .routes.admin.main import admin_bp
    from .routes.admin.api_endpoint import api_endpoint_bp
    from .routes.admin.api_test import api_test_bp
    from .routes.admin.sql_doc import sql_doc_bp
    from .routes.admin.qa_board import qa_board_bp
    from .routes.admin.article import article_bp
    from .routes.api.user import user_api_bp
    from .routes.api.common import common_api_bp
    from .routes.api.sqldoc import sqldoc_api_bp
    from .routes.api.article import article_api_bp
    from .routes.api.qaboard import qaboard_api_bp
    from .routes.api.sqooldb import sqooldb_api_bp, setup_periodic_cleanup

    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_endpoint_bp, url_prefix="/admin/api_endpoint")
    app.register_blueprint(api_test_bp, url_prefix="/admin/api_test")
    app.register_blueprint(sql_doc_bp, url_prefix="/admin/sql_doc")
    app.register_blueprint(qa_board_bp, url_prefix="/admin/community/qa_board")
    app.register_blueprint(article_bp, url_prefix="/admin/community/article")
    app.register_blueprint(user_api_bp, url_prefix="/api/user")
    app.register_blueprint(common_api_bp, url_prefix="/api/common")
    app.register_blueprint(sqldoc_api_bp, url_prefix="/api/sqldoc")
    app.register_blueprint(article_api_bp, url_prefix="/api/community/article")
    app.register_blueprint(qaboard_api_bp, url_prefix="/api/community/qaboard")
    app.register_blueprint(sqooldb_api_bp, url_prefix="/api/sqool")

    setup_periodic_cleanup(app)

    return app
