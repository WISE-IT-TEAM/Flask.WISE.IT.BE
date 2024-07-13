import os
from flask import Blueprint, request, jsonify, url_for, current_app
from werkzeug.utils import secure_filename

common_api_bp = Blueprint("common_api", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@common_api_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "Common API Test Success"})


@common_api_bp.route("/upload_image", methods=["POST"])
def upload_image():

    UPLOAD_FOLDER = current_app.config["UPLOAD_FOLDER"]

    # 업로드 폴더가 없으면 생성
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # 파일이 없을 경우
    if "image" not in request.files:
        return jsonify({"message": "선택된 파일이 없습니다."})

    # 파일 가져오기
    file = request.files["image"]

    # 파일이 없을 경우
    if file.filename == "":
        return jsonify({"message": "선택된 파일이 없습니다."})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        return jsonify({"url": f"{url_for('static', filename='Uploads/' + filename )}"})

    return jsonify({"message": "허용되지 않는 파일 형식입니다."})
