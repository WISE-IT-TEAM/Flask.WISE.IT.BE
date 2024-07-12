from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app,
)
from app.models import db, Question, Answer
from .main import login_required

qaboard_bp = Blueprint("qaboard", __name__)


@login_required
@qaboard_bp.route("/list", methods=["GET"])
def admin_qaboard_list():
    board_list = Question.query.all()
    return render_template(
        "admin/qaboard/qaboard_list.jinja2", title="QABoard List", board_list=board_list
    )


@login_required
@qaboard_bp.route("/create", methods=["GET", "POST"])
def admin_qaboard_create():
    if request.method == "POST":
        nickname = request.form.get("nickname")
        password = request.form.get("password")
        title = request.form.get("title")
        content = request.form.get("content")
        tags = request.form.get("tags")

        question = Question(password)
        question.nickname = nickname
        question.title = title
        question.content = content
        question.tags = tags

        db.session.add(question)
        db.session.commit()

        flash("게시글이 등록되었습니다.", "success")
        return redirect(url_for("admin.admin_board_list"))

    return render_template(
        "admin/qaboard/qaboard_create.jinja2", title="QABoard Create"
    )
