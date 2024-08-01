import os
import re
from flask import Blueprint, request, jsonify, url_for, current_app
from datetime import datetime

common_api_bp = Blueprint("common_api", __name__)

MAX_UPLOAD_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "svg", "webp", "bmp"}
ALLOWED_FILE_EXTENSIONS = {
    "txt",
    "md",
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "ppt",
    "pptx",
    "zip",
    "tar",
    "gz",
    "7z",
}


def check_filename(filename):
    reg = re.compile(r"[^A-Za-z0-9_.가-힣-]")
    for s in os.path.sep, os.path.altsep:
        if s:
            filename = filename.replace(s, " ")
            filename = str(reg.sub("", "_".join(filename.split()))).strip("._")
    return filename


def allowed_image(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    )


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_FILE_EXTENSIONS
    )


@common_api_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "Common API Test Success"}), 200


@common_api_bp.route("/upload_image", methods=["POST"])
def upload_image():
    UPLOAD_FOLDER = current_app.config["UPLOAD_FOLDER"]

    # 업로드 폴더가 없으면 생성
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # FormData에서 형식이 맞지 않을 경우
    if "image" not in request.files:
        return jsonify({"message": "FormData Key값을 확인해 주세요."}), 400

    # 파일 가져오기
    file = request.files["image"]

    # 파일 사이즈 체크
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_UPLOAD_FILE_SIZE:
        return jsonify({"message": "파일 사이즈가 10MB를 초과했습니다."}), 400

    # 파일이 없을 경우
    if file.filename == "":
        return jsonify({"message": "선택된 파일이 없습니다."}), 400

    if not allowed_image(file.filename):
        return jsonify({"message": "이미지 파일만 업로드 가능합니다."}), 400

    if file and allowed_image(file.filename):
        filename = check_filename(file.filename)
        add_time = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = "image_" + add_time + "_" + filename
        file_path = os.path.join(UPLOAD_FOLDER, new_filename)
        file.save(file_path)
        return jsonify(
            {"url": f"{url_for('static', filename='Uploads/' + new_filename )}"}
        )

    return jsonify({"message": "파일 업로드에 실패했습니다."}), 400


@common_api_bp.route("/upload_thumbnail", methods=["POST"])
def upload_thumbnail():
    UPLOAD_FOLDER = current_app.config["UPLOAD_FOLDER"]

    # 업로드 폴더가 없으면 생성
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # FormData에서 형식이 맞지 않을 경우
    if "thumbnail" not in request.files:
        return jsonify({"message": "FormData Key값을 확인해 주세요."}), 400

    # 파일 가져오기
    file = request.files["thumbnail"]

    # 파일 사이즈 체크
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_UPLOAD_FILE_SIZE:
        return jsonify({"message": "파일 사이즈가 10MB를 초과했습니다."}), 400

    # 파일이 없을 경우
    if file.filename == "":
        return jsonify({"message": "선택된 파일이 없습니다."}), 400

    if not allowed_image(file.filename):
        return jsonify({"message": "이미지 파일만 업로드 가능합니다."}), 400

    if file and allowed_image(file.filename):
        filename = check_filename(file.filename)
        add_time = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = "thumbnail_" + add_time + "_" + filename
        file_path = os.path.join(UPLOAD_FOLDER, new_filename)
        file.save(file_path)
        return jsonify(
            {"url": f"{url_for('static', filename='Uploads/' + new_filename )}"}
        )

    return jsonify({"message": "파일 업로드에 실패했습니다."}), 400


@common_api_bp.route("/upload_file", methods=["POST"])
def upload_file():
    UPLOAD_FOLDER = current_app.config["UPLOAD_FOLDER"]

    # 업로드 폴더가 없으면 생성
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # FormData에서 형식이 맞지 않을 경우
    if "file_path" not in request.files:
        return jsonify({"message": "FormData Key값을 확인해 주세요."}), 400

    # 파일 가져오기
    file = request.files["file_path"]

    # 파일 사이즈 체크
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_UPLOAD_FILE_SIZE:
        return jsonify({"message": "파일 사이즈가 10MB를 초과했습니다."}), 400

    # 파일이 없을 경우
    if file.filename == "":
        return jsonify({"message": "선택된 파일이 없습니다."}), 400

    if not allowed_file(file.filename):
        return jsonify({"message": "허용되지 않는 파일 형식입니다."}), 400

    if file and allowed_file(file.filename):
        filename = check_filename(file.filename)
        add_time = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = "file_" + add_time + "_" + filename
        file_path = os.path.join(UPLOAD_FOLDER, new_filename)
        file.save(file_path)
        return jsonify(
            {"url": f"{url_for('static', filename='Uploads/' + new_filename )}"}
        )

    return jsonify({"message": "파일 업로드에 실패했습니다."}), 400


@common_api_bp.route("/delete_file", methods=["DELETE"])
def delete_file():
    UPLOAD_FOLDER = current_app.config["UPLOAD_FOLDER"]

    file_name = request.json.get("file_name")

    if not file_name:
        return jsonify({"message": "파일 이름이 없습니다."}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file_name)

    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"message": "파일이 삭제되었습니다."}), 200
    else:
        return jsonify({"message": "파일이 존재하지 않습니다."}), 404
