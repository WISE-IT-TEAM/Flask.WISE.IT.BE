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
    articles = (
        Article.query.with_entities(
            Article, func.count(ArticleComment.id).label("comment_count")
        )
        .outerjoin(ArticleComment, Article.id == ArticleComment.article_id)
        .filter(Article.status == "공개")
        .group_by(Article.id)
        .all()
    )

    for article, comment_count in articles:
        article_data = {
            "Id": article.id,
            "Title": article.title,
            "Category": article.category,
            "Thumbnail": article.thumbnail,
            "Content": article.content,
            "Tags": article.tags,
            "Like_count": article.like_count,
            "View_count": article.view_count,
            "Created_at": article.created_at,
            "Comment_count": comment_count,
        }

        article_list.append(article_data)

    return (
        jsonify(
            {
                "status": "Article 게시글 리스트 불러오기 성공",
                "articlelist": article_list,
            }
        ),
        200,
    )


@article_api_bp.route("/<string:art_id>", methods=["GET"])
def get_article(art_id):
    article = Article.query.filter_by(id=art_id).one_or_none()

    if article is None:
        return (
            jsonify({"status": "해당 id를 가진 게시글이 존재하지 않음: " + art_id}),
            400,
        )

    if article.status != "공개":
        return jsonify({"status": "게시글이 공개 상태가 아님"}), 400

    article_info = {
        "Id": article.id,
        "Title": article.title,
        "Category": article.category,
        "Thumbnail": article.thumbnail,
        "Content": article.content,
        "Tags": article.tags,
        "Like_count": article.like_count,
        "View_count": article.view_count,
        "Created_at": article.created_at,
    }

    return (
        jsonify({"status": "게시글 상세 내용 불러오기 성공", "article": article_info}),
        200,
    )


@article_api_bp.route("/<string:art_id>/comments", methods=["GET"])
def get_comments(art_id):
    # json에 담을 리스트 선언
    comment_list = []

    # 상위 댓글 받아오기
    main_comments = (
        ArticleComment.query.filter_by(article_id=art_id, parent_id=None, status="공개")
        .order_by(ArticleComment.created_at.asc())
        .all()
    )

    # 댓글이 없을 경우 빈 리스트 반환
    if not main_comments:
        return jsonify({"status": "댓글이 없음", "comments": comment_list}), 200

    # 상위 댓글이 있으면 리스트에 추가하고 하위 댓글 있는지 확인해서 추가
    for maincom in main_comments:
        comment_list.append(
            {
                "Id": maincom.id,
                "Content": maincom.content,
                "Nickname": maincom.nickname,
                "Created_at": maincom.created_at,
                "Tree": "main",
            }
        )

        sub_comments = (
            ArticleComment.query.filter_by(parent_id=maincom.id, status="공개")
            .order_by(ArticleComment.created_at.asc())
            .all()
        )

        if len(sub_comments) > 0:
            for subcom in sub_comments:
                comment_list.append(
                    {
                        "Id": subcom.id,
                        "Content": subcom.content,
                        "Nickname": subcom.nickname,
                        "Created_at": subcom.created_at,
                        "Tree": "sub",
                    }
                )

    return jsonify({"status": "댓글 받아오기 성공", "comments": comment_list}), 200
