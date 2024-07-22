from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Article, ArticleCategory, ArticleComment
from .main import login_required

article_bp = Blueprint("article", __name__)


def get_category_tree():
    categories = ArticleCategory.query.all()
    category_dict = {
        cat.id: {
            "id": cat.id,
            "category": cat.category,
            "children": [],
        }
        for cat in categories
    }
    root_categories = []
    for cat in categories:
        if cat.parent_id:
            category_dict[cat.parent_id]["children"].append(category_dict[cat.id])
        else:
            root_categories.append(category_dict[cat.id])
    return root_categories


@login_required
@article_bp.route("/", methods=["GET"])
def admin_article_list():
    category = get_category_tree()
    article_list = Article.query.order_by(Article.created_at.desc()).all()
    return render_template(
        "admin/article/article_list.jinja2",
        title="Article List",
        category=category,
        article_list=article_list,
    )
