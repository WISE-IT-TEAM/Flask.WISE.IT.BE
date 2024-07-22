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
    main_cats = (
        SqlDocCategory.query.filter_by(parent_id=None)
        .with_entities(SqlDocCategory.id, SqlDocCategory.category)
        .order_by(SqlDocCategory.order_num.asc())
        .all()
    )

    for mcat in main_cats:
        category_list.append({"Title": mcat.category, "Id": mcat.id, "Tree": "main"})

        # main 카테고리에 글이 있는지 확인하고 있으면 리스트에 추가
        docs = (
            SqlDoc.query.filter_by(category_id=mcat.id)
            .with_entities(SqlDoc.id, SqlDoc.title)
            .order_by(SqlDoc.order_num.asc())
            .all()
        )

        if len(docs) > 0:
            for doc in docs:
                category_list.append({"Title": doc.title, "Id": doc.id, "Tree": "doc"})

        # main 카테고리에 sub 카테고리가 있는지 확인하고 있으면 리스트에 추가
        sub_cats = (
            SqlDocCategory.query.filter_by(parent_id=mcat.id)
            .with_entities(SqlDocCategory.id, SqlDocCategory.category)
            .order_by(SqlDocCategory.order_num.asc())
            .all()
        )

        if len(sub_cats) > 0:
            for scat in sub_cats:
                category_list.append(
                    {"Title": scat.category, "Id": scat.id, "Tree": "sub"}
                )
                docs = (
                    SqlDoc.query.filter_by(category_id=scat.id)
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


@sqldoc_api_bp.route("/document", methods=["POST"])
def get_document():
    data = request.json
    doc_id = data.get("doc_id")

    doc = (
        SqlDoc.query.filter_by(id=doc_id)
        .with_entities(SqlDoc.title, SqlDoc.content)
        .all()
    )

    if doc == []:
        return (
            jsonify({"status": "해당 id를 가진 게시글이 존재하지 않음: " + doc_id}),
            400,
        )

    document = {"title": doc[0].title, "content": doc[0].content}

    return (
        jsonify({"status": "게시글 상세 내용 불러오기 성공", "document": document}),
        200,
    )
