from flask import Blueprint, request, jsonify
from app.models import db, ArticleCategory, Tag, Article, ArticleComment

article_api_bp = Blueprint("article_api", __name__)


@article_api_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "Article API Test Success"})
