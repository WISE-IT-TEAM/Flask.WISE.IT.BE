from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app,
)
from sqlalchemy import inspect
from . import admin
from ..models import db, AdminUser, Question, Answer
from .. import bcrypt
import os


def login_required(f):
    def wrap(*args, **kwargs):
        if "admin_user" not in session:
            return redirect(url_for("admin.admin_login"))
        return f(*args, **kwargs)

    return wrap


@admin.route("/", methods=["GET", "POST"])
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

    return render_template("admin/login.jinja2", title="Login")


@admin.route("/register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password_confirm")
        register_key = request.form.get("register_key")

        if register_key != current_app.config["REGISTER_KEY"]:
            flash("관리자 패스워드 키가 올바르지 않습니다.", "danger")
            return redirect(url_for("admin.admin_register"))

        admin_user = AdminUser(username, password)
        db.session.add(admin_user)
        db.session.commit()

        flash("관리자 등록이 완료되었습니다.", "success")
        return redirect(url_for("admin.admin_login"))

    return render_template("admin/register.jinja2", title="Register")


@admin.route("/logout")
def admin_logout():
    session.pop("admin_user", None)
    flash("로그아웃 되었습니다.", "success")
    return redirect(url_for("admin.admin_login"))


@login_required
@admin.route("/dashboard", methods=["GET"])
def admin_dashboard():

    return render_template("admin/dashboard.jinja2", title="Dashboard")


@login_required
@admin.route("/database", methods=["GET"])
def admin_database():
    inspector = inspect(db.engine)
    schema = {}
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        schema[table_name] = [
            {"name": column["name"], "type": column["type"]} for column in columns
        ]
    return render_template("admin/database.jinja2", title="Database", schema=schema)


@login_required
@admin.route("/board_list", methods=["GET"])
def admin_board_list():
    board_list = Question.query.all()
    return render_template(
        "admin/qaboard/board_list.jinja2", title="QABoard List", board_list=board_list
    )


@login_required
@admin.route("/board_create", methods=["GET", "POST"])
def admin_board_create():
    if request.method == "POST":
        nickname = request.form.get("nickname")
        password = request.form.get("password")
        thumbnail = request.form.get("thumbnail")
        title = request.form.get("title")
        content = request.form.get("content")
        tags = request.form.get("tags")

        question = Question(password)
        question.nickname = nickname
        question.thumbnail = thumbnail
        question.title = title
        question.content = content
        question.tags = tags

        db.session.add(question)
        db.session.commit()

        flash("게시글이 등록되었습니다.", "success")
        return redirect(url_for("admin.admin_board_list"))

    return render_template("admin/qaboard/board_create.jinja2", title="QABoard Create")
