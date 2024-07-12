from flask import Blueprint, request, jsonify

common_api_bp = Blueprint("common_api", __name__)


@common_api_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "Common API Test Success"})
