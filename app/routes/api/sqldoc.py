from flask import Blueprint, request, jsonify
from app.models import db, SqlDocCategory, SqlDoc

sqldoc_api_bp = Blueprint("sqldoc_api", __name__)


@sqldoc_api_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "sqldoc API Test Success"})
