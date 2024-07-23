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
