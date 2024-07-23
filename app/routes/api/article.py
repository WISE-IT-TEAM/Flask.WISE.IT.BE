from flask import Blueprint, request, jsonify
from app.models import db, Article, ArticleComment
from sqlalchemy.sql import func

article_api_bp = Blueprint("article_api", __name__)


@article_api_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "Article API Test Success"})


@article_api_bp.route("/list")
def get_article_list():
    # json에 담을 리스트 선언
    article_list = []

    # article 정보와 댓글 수 받아오기
    article_info = (
        Article.query
        .with_entities(
            Article,
            func.count(ArticleComment.id).label('comment_num')
        )
        .outerjoin(
            ArticleComment,
            Article.id == ArticleComment.article_id
        )
        .filter_by(status='공개')
        .group_by(Article.id)
        .all()
    )
    
    for article, comment_num in article_info:
        article_data = {
            'id': article.id,
            'title': article.title,
            'category': article.category,
            'thumbnail': article.thumbnail,
            'content': article.content,
            'tags': article.tags,
            'like_count': article.like_count,
            'view_count': article.view_count,
            'created_at': article.created_at
        }

        article_list.append(article_data)

    return (
        jsonify({"status": "게시글 리스트 불러오기 성공", "articlelist": article_list}),
        200,
    )