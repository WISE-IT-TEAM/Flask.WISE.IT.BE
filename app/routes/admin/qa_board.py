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
from ..api.common import upload_file, upload_image, delete_file

qa_board_bp = Blueprint("qa_board", __name__)


@login_required
@qa_board_bp.route("/", methods=["GET"])
def admin_qaboard_list():
    board_list = Question.query.order_by(Question.created_at.desc()).all()
    return render_template(
        "admin/qaboard/qaboard_list.jinja2", title="QABoard List", board_list=board_list
    )


@login_required
@qa_board_bp.route("/<question_id>", methods=["GET", "POST"])
def admin_qaboard_detail(question_id):
    question = Question.query.get(question_id)
    answers = Answer.query.filter_by(question_id=question_id).all()

    if request.method == "POST":
        password = request.form.get("password")
        content = request.form.get("content")

        answer = Answer(password)
        answer.content = content
        answer.question_id = question_id

        db.session.add(answer)
        db.session.commit()

        flash("답변이 등록되었습니다.", "success")
        return redirect(
            url_for("qa_board.admin_qaboard_detail", question_id=question_id)
        )

    return render_template(
        "admin/qaboard/qaboard_detail.jinja2",
        title="QABoard Detail",
        question=question,
        answers=answers,
    )


@login_required
@qa_board_bp.route("/create", methods=["GET", "POST"])
def admin_qaboard_create():
    if request.method == "POST":
        nickname = request.form.get("nickname")
        password = request.form.get("password")
        title = request.form.get("title")
        content = request.form.get("content")

        question = Question(password)
        question.nickname = nickname
        question.title = title
        question.content = content

        db.session.add(question)
        db.session.commit()

        flash("게시글이 등록되었습니다.", "success")
        return redirect(url_for("qa_board.admin_qaboard_list"))

    return render_template(
        "admin/qaboard/qaboard_create.jinja2", title="QABoard Create"
    )
