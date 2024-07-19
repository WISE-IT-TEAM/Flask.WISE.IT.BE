from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app,
    jsonify,
)
from sqlalchemy import inspect
from app.models import db, AdminUser, Question, Answer
from app import bcrypt
import os
import psutil

admin_bp = Blueprint("admin", __name__)


def login_required(f):
    def wrap(*args, **kwargs):
        if "admin_user" not in session:
            return redirect(url_for("admin.admin_login"))
        return f(*args, **kwargs)

    return wrap


@admin_bp.route("/")
def admin_index():
    return redirect(url_for("admin.admin_login"))


@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        admin_user = AdminUser.query.filter_by(username=username).first()

        if admin_user and bcrypt.check_password_hash(admin_user.password, password):
            session["admin_user"] = admin_user.id
            return redirect(url_for("admin.admin_dashboard"))

        flash("아이디 또는 비밀번호가 올바르지 않습니다.", "danger")
        return redirect(url_for("admin.admin_login"))
    elif request.method == "GET":
        if session.get("admin_user"):
            return redirect(url_for("admin.admin_dashboard"))
        else:
            return render_template("admin/login.jinja2", title="Login")


@admin_bp.route("/register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password_confirm")
        register_key = request.form.get("register_key")

        username_check = AdminUser.query.filter_by(username=username).first()

        if username_check:
            flash("이미 존재하는 아이디 입니다.", "danger")

        if register_key != current_app.config["REGISTER_KEY"]:
            flash("관리자 패스워드 키가 올바르지 않습니다.", "danger")
            return redirect(url_for("admin.admin_register"))

        admin_user = AdminUser(username, password)
        db.session.add(admin_user)
        db.session.commit()

        flash("관리자 등록이 완료되었습니다.", "success")
        return redirect(url_for("admin.admin_login"))

    return render_template("admin/register.jinja2", title="Register")


@admin_bp.route("/logout")
def admin_logout():
    session.pop("admin_user", None)
    flash("로그아웃 되었습니다.", "success")
    return redirect(url_for("admin.admin_login"))


def get_system_usage():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    disk = psutil.disk_usage("/")
    disk_usage = disk.percent
    return cpu_usage, memory_usage, disk_usage


@login_required
@admin_bp.route("/dashboard", methods=["GET"])
def admin_dashboard():

    return render_template("admin/dashboard.jinja2", title="Dashboard")


@login_required
@admin_bp.route("/usage", methods=["GET"])
def usage():
    cpu_usage, memory_usage, disk_usage = get_system_usage()
    return jsonify(cpu=cpu_usage, memory=memory_usage, disk=disk_usage)


@login_required
@admin_bp.route("/database", methods=["GET"])
def admin_database():
    inspector = inspect(db.engine)
    schema = {}
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        schema[table_name] = [
            {"name": column["name"], "type": column["type"]} for column in columns
        ]
    return render_template("admin/database.jinja2", title="Database", schema=schema)
