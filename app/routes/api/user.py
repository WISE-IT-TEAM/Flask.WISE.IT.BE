from flask import Blueprint, request, jsonify

user_api_bp = Blueprint("user_api", __name__)


@user_api_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "User API Test Success"})
