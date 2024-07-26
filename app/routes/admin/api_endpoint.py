from flask import Blueprint, render_template
from .main import login_required

api_endpoint_bp = Blueprint("api_endpoint", __name__)


@login_required
@api_endpoint_bp.route("/user", methods=["GET"])
def api_endpoint_user():
    return render_template("admin/api_endpoint/user.jinja2", title="API Endpoint: User")


@login_required
@api_endpoint_bp.route("/article", methods=["GET"])
def api_endpoint_article():
    return render_template(
        "admin/api_endpoint/article.jinja2", title="API Endpoint: Article"
    )


@login_required
@api_endpoint_bp.route("/qaboard", methods=["GET"])
def api_endpoint_qaboard():
    return render_template(
        "admin/api_endpoint/qaboard.jinja2", title="API Endpoint: QABoard"
    )


@login_required
@api_endpoint_bp.route("/sqool/artist", methods=["GET"])
def api_endpoint_sqool_artist():
    return render_template(
        "admin/api_endpoint/sqool_artist.jinja2", title="API Endpoint: Sqool - Artist"
    )


@login_required
@api_endpoint_bp.route("/sqool/movie", methods=["GET"])
def api_endpoint_sqool_movie():
    return render_template(
        "admin/api_endpoint/sqool_movie.jinja2", title="API Endpoint: Sqool - Movie"
    )


@login_required
@api_endpoint_bp.route("/common", methods=["GET"])
def api_endpoint_common():
    return render_template(
        "admin/api_endpoint/common.jinja2", title="API Endpoint: Common"
    )
