from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from .main import login_required

api_test_bp = Blueprint("api_test", __name__)


@login_required
@api_test_bp.route("/upload/image", methods=["GET"])
def upload_image():
    return render_template(
        "admin/api_test/upload_image.jinja2", title="API Test: Upload Image"
    )


@login_required
@api_test_bp.route("/upload/thumbnail", methods=["GET"])
def upload_thumbnail():
    return render_template(
        "admin/api_test/upload_thumbnail.jinja2", title="API Test: Upload Thumbnail"
    )


@login_required
@api_test_bp.route("/upload/file", methods=["GET"])
def upload_file():
    return render_template(
        "admin/api_test/upload_file.jinja2", title="API Test: Upload File"
    )


@login_required
@api_test_bp.route("/delete/file", methods=["GET"])
def delete_file():
    return render_template(
        "admin/api_test/delete_file.jinja2", title="API Test: Delete File"
    )


@login_required
@api_test_bp.route("/sql/query", methods=["GET"])
def sql_query():
    return render_template(
        "admin/api_test/sql_query.jinja2", title="API Test: SQL Query"
    )
