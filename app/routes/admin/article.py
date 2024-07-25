import os
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)
from werkzeug.utils import secure_filename
from datetime import datetime
from app.models import db, Article, ArticleComment
from .main import login_required

article_bp = Blueprint("article", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "svg", "webp", "bmp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@login_required
@article_bp.route("/", methods=["GET"])
def admin_article_list():
    article_list = Article.query.order_by(Article.created_at.desc()).all()
    comment_count = ArticleComment.query.count()
    return render_template(
        "admin/article/article_list.jinja2",
        title="Article List",
        article_list=article_list,
        comment_count=comment_count,
    )


@login_required
@article_bp.route("/create", methods=["GET", "POST"])
def admin_article_create():
    UPLOAD_FOLDER = current_app.config["UPLOAD_FOLDER"]

    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        thumbnail = request.files.get("thumbnail")
        content = request.form.get("content")
        description = request.form.get("description")
        status = request.form.get("status")
        tags = request.form.get("tags")

        thumbnail_path = None
        if thumbnail and allowed_file(thumbnail.filename):
            filename = secure_filename(thumbnail.filename)
            add_time = datetime.now().strftime("%Y%m%d%H%M%S")
            new_filename = "thumbnail_" + add_time + "_" + filename
            thumbnail_path = os.path.join(UPLOAD_FOLDER, new_filename)
            thumbnail.save(thumbnail_path)
            thumbnail_path = url_for("static", filename="Uploads/" + new_filename)

        new_article = Article(
            title=title,
            category=category,
            thumbnail=thumbnail_path,
            content=content,
            description=description,
            status=status,
            tags=tags,
        )
        db.session.add(new_article)
        db.session.commit()

        flash("게시글이 작성되었습니다.", "success")
        return redirect(url_for("article.admin_article_list"))

    return render_template(
        "admin/article/article_create.jinja2", title="Article Create"
    )


@login_required
@article_bp.route("/<article_id>", methods=["GET", "POST"])
def admin_article_modify(article_id):
    article = Article.query.get_or_404(article_id)
    comments = (
        ArticleComment.query.filter_by(article_id=article_id)
        .order_by(ArticleComment.created_at)
        .all()
    )

    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        thumbnail = request.files.get("thumbnail")
        content = request.form.get("content")
        description = request.form.get("description")
        status = request.form.get("status")
        tags = request.form.get("tags")

        if thumbnail and allowed_file(thumbnail.filename):
            filename = secure_filename(thumbnail.filename)
            add_time = datetime.now().strftime("%Y%m%d%H%M%S")
            new_filename = "thumbnail_" + add_time + "_" + filename
            thumbnail_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], new_filename
            )
            thumbnail.save(thumbnail_path)
            article.thumbnail = url_for("static", filename="Uploads/" + new_filename)

        article.title = title
        article.category = category
        article.content = content
        article.description = description
        article.status = status
        article.tags = tags

        db.session.commit()

        flash("게시글이 수정되었습니다.", "success")
        return redirect(url_for("article.admin_article_modify", article_id=article_id))

    return render_template(
        "admin/article/article_modify.jinja2",
        title="Article Modify",
        article=article,
        comments=comments,
    )


@login_required
@article_bp.route("/<article_id>/thumbnail/delete", methods=["GET"])
def admin_article_thumbnail_delete(article_id):
    article = Article.query.get_or_404(article_id)
    article.thumbnail = None
    db.session.commit()

    flash("썸네일이 삭제되었습니다.", "success")
    return redirect(url_for("article.admin_article_modify", article_id=article_id))
