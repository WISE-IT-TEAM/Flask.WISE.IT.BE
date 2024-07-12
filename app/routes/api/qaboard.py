from flask import Blueprint, request, jsonify
from app.models import db, Question, Answer

qaboard_api_bp = Blueprint("qaboard_api", __name__)


@qaboard_api_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "QABoard API Test Success"})
