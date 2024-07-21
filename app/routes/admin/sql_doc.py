from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, SqlDocCategory, SqlDoc
from .main import login_required

sql_doc_bp = Blueprint("sql_doc", __name__)


def get_category_tree():
    categories = SqlDocCategory.query.all()
    category_dict = {
        cat.id: {"id": cat.id, "category": cat.category, "children": []}
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
@sql_doc_bp.route("/category", methods=["GET", "POST"])
def admin_category_list():
    if request.method == "POST":
        category = request.form["category"]
        parent_id = request.form.get("parent_id")
        parent_id = parent_id if parent_id else None
        new_category = SqlDocCategory(category=category, parent_id=parent_id)
        db.session.add(new_category)
        db.session.commit()
        flash("카테고리가 추가되었습니다.", "success")
        return redirect(url_for("sql_doc.admin_category_list"))

    if request.method == "GET":
        category = get_category_tree()
        return render_template(
            "admin/sql_doc/category_list.jinja2",
            category=category,
            title="SQL Document Category",
        )


@login_required
@sql_doc_bp.route("/category/<string:category_id>", methods=["GET", "POST"])
def admin_category_detail(category_id):
    category = SqlDocCategory.query.get_or_404(category_id)
    all_category = get_category_tree()

    if request.method == "POST":
        category.category = request.form["category"]
        parent_id = request.form.get("parent_id") or None
        category.parent_id = parent_id if parent_id else None
        db.session.commit()
        flash("카테고리가 수정되었습니다.", "success")
        return redirect(url_for("sql_doc.admin_category_list"))

    if request.method == "GET":
        parent_category = SqlDocCategory.query.get(category.parent_id)
        return render_template(
            "admin/sql_doc/category_detail.jinja2",
            category=category,
            all_category=all_category,
            parent_category=parent_category,
            title="SQL Doc Category Detail",
        )


@login_required
@sql_doc_bp.route("/category/<string:category_id>/delete", methods=["POST"])
def admin_category_delete(category_id):
    category = SqlDocCategory.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash("카테고리가 삭제되었습니다.", "success")
    return redirect(url_for("sql_doc.admin_category_list"))


@login_required
@sql_doc_bp.route("/document", methods=["GET"])
def admin_document_list():
    if request.method == "GET":
        doc = SqlDoc.query.all()
        return render_template(
            "admin/sql_doc/document_list.jinja2", doc=doc, title="SQL Document"
        )


@login_required
@sql_doc_bp.route("/document/create", methods=["GET", "POST"])
def admin_document_create():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        category_id = request.form.get("category_id")
        new_doc = SqlDoc(title=title, content=content, category_id=category_id)
        db.session.add(new_doc)
        db.session.commit()
        flash("문서가 추가되었습니다.", "success")
        return redirect(url_for("sql_doc.admin_document_list"))

    if request.method == "GET":
        category = get_category_tree()
        return render_template(
            "admin/sql_doc/document_create.jinja2",
            category=category,
            title="SQL Document Create",
        )
