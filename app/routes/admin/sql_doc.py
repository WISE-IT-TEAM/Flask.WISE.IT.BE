from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, SqlDocCategory, SqlDoc
from .main import login_required

sql_doc_bp = Blueprint("sql_doc", __name__)


@login_required
@sql_doc_bp.route("/", methods=["GET"])
def category_list():
    categories = SqlDocCategory.query.all()
    return render_template("admin/sql_doc/category_list.jinja2", categories=categories)
