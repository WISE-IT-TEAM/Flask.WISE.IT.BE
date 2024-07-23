from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Article, ArticleComment
from .main import login_required

article_bp = Blueprint("article", __name__)


@login_required
@article_bp.route("/", methods=["GET"])
def admin_article_list():
    article_list = Article.query.order_by(Article.created_at.desc()).all()
    return render_template(
        "admin/article/article_list.jinja2",
        title="Article List",
        article_list=article_list,
    )


@login_required
@article_bp.route("/create", methods=["GET", "POST"])
def admin_article_create():
    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        thumbnail = request.files.get("thumbnail")
        content = request.form.get("content")
        status = request.form.get("status")
        tags = request.form.get("tags")

        new_article = Article(
            title=title,
            category=category,
            thumbnail=thumbnail,
            content=content,
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
    article = Article.query.get(article_id)
    comments = ArticleComment.query.filter_by(article_id=article_id).all()

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        article.title = title
        article.content = content

        db.session.commit()

        flash("게시글이 수정되었습니다.", "success")
        return redirect(url_for("article.admin_article_modify", article_id=article_id))

    return render_template(
        "admin/article/article_modify.jinja2",
        title="Article Modify",
        article=article,
        comments=comments,
    )
