from flask import Blueprint, render_template
from .main import login_required

api_docs_bp = Blueprint("api_docs", __name__)


@login_required
@api_docs_bp.route("/user", methods=["GET"])
def api_docs_user():
    return render_template("admin/api_docs/user.jinja2", title="API Docs: User")


@login_required
@api_docs_bp.route("/qaboard", methods=["GET"])
def api_docs_qaboard():
    return render_template("admin/api_docs/qaboard.jinja2", title="API Docs: QABoard")


@login_required
@api_docs_bp.route("/sqool/artist", methods=["GET"])
def api_docs_sqool_artist():
    return render_template(
        "admin/api_docs/sqool_artist.jinja2", title="API Docs: Sqool - Artist"
    )


@login_required
@api_docs_bp.route("/sqool/movie", methods=["GET"])
def api_docs_sqool_movie():
    return render_template(
        "admin/api_docs/sqool_movie.jinja2", title="API Docs: Sqool - Movie"
    )


@login_required
@api_docs_bp.route("/common", methods=["GET"])
def api_docs_common():
    return render_template("admin/api_docs/common.jinja2", title="API Docs: Common")
