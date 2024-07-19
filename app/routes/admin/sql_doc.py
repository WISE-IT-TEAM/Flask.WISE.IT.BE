from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, SqlDocCategory, SqlDoc
from .main import login_required

sql_doc_bp = Blueprint("sql_doc", __name__)


@login_required
@sql_doc_bp.route("/category", methods=["GET", "POST"])
def admin_category_list():
    if request.method == "POST":
        category = request.form.get("category")
        parent_id = request.form.get("parent_id")

        if category:
            new_category = SqlDocCategory(category=category, parent_id=parent_id)
            db.session.add(new_category)
            db.session.commit()
            flash("카테고리가 추가되었습니다.", "success")
            return redirect(url_for("sql_doc.category_list"))

    if request.method == "GET":
        category = SqlDocCategory.query.all()
        return render_template("admin/sql_doc/category_list.jinja2", category=category)
