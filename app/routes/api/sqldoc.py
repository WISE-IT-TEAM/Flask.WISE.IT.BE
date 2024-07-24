from flask import Blueprint, request, jsonify
from app.models import db, SqlDocCategory, SqlDoc

sqldoc_api_bp = Blueprint("sqldoc_api", __name__)


@sqldoc_api_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "sqldoc API Test Success"})


@sqldoc_api_bp.route("/category", methods=["GET"])
def get_category():
    # json에 담을 리스트 선언
    category_list = []

    # 최상위(main) 디렉토리 받아오기
    main_categories = (
        SqlDocCategory.query.filter_by(parent_id=None)
        .with_entities(SqlDocCategory.id, SqlDocCategory.category)
        .order_by(SqlDocCategory.order_num.asc())
        .all()
    )

    for maincat in main_categories:
        category_list.append(
            {"Title": maincat.category, "Id": maincat.id, "Tree": "main"}
        )

        # main 카테고리에 글이 있는지 확인하고 있으면 리스트에 추가
        docs = (
            SqlDoc.query.filter_by(category_id=maincat.id, status="공개")
            .with_entities(SqlDoc.id, SqlDoc.title)
            .order_by(SqlDoc.order_num.asc())
            .all()
        )

        if len(docs) > 0:
            for doc in docs:
                category_list.append({"Title": doc.title, "Id": doc.id, "Tree": "doc"})

        # main 카테고리에 sub 카테고리가 있는지 확인하고 있으면 리스트에 추가
        sub_categories = (
            SqlDocCategory.query.filter_by(parent_id=maincat.id)
            .with_entities(SqlDocCategory.id, SqlDocCategory.category)
            .order_by(SqlDocCategory.order_num.asc())
            .all()
        )

        if len(sub_categories) > 0:
            for subcat in sub_categories:
                category_list.append(
                    {"Title": subcat.category, "Id": subcat.id, "Tree": "sub"}
                )
                docs = (
                    SqlDoc.query.filter_by(category_id=subcat.id, status="공개")
                    .with_entities(SqlDoc.id, SqlDoc.title)
                    .order_by(SqlDoc.order_num.asc())
                    .all()
                )

                for doc in docs:
                    category_list.append(
                        {"Title": doc.title, "Id": doc.id, "Tree": "doc"}
                    )

    return (
        jsonify(
            {
                "status": "카테고리 리스트 불러오기 성공(main - sub - doc)",
                "categories": category_list,
            }
        ),
        200,
    )


@sqldoc_api_bp.route("/document/<string:doc_id>", methods=["GET"])
def get_document(doc_id):

    doc = SqlDoc.query.filter_by(id=doc_id).one_or_none()

    if doc is None:
        return (
            jsonify({"status": "해당 id를 가진 게시글이 존재하지 않음: " + doc_id}),
            400,
        )

    if doc.status != "공개":
        return jsonify({"status": "게시글이 공개 상태가 아님"}), 400

    document = {"title": doc.title, "content": doc.content}

    return (
        jsonify({"status": "게시글 상세 내용 불러오기 성공", "document": document}),
        200,
    )
