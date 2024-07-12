from flask import Blueprint, request, jsonify, g, session
import sqlite3
import os
from nanoid import generate

sqool_artist_bp = Blueprint("sqool_artist", __name__)

# * ArtistDB 폴더 경로 및 SQL 파일 리스트
SQL_FOLDER = os.path.join(os.path.dirname(__file__), "../../static/ArtistDB")
SQL_FILES = ["Table.sql", "Artist.sql", "Member.sql", "Album.sql"]


def get_db():
    if "db" not in g:
        db = sqlite3.connect(":memory:")
        for sql_file in SQL_FILES:
            sql_path = os.path.join(SQL_FOLDER, sql_file)
            if os.path.exists(sql_path):
                with open(sql_path, "r") as file:
                    db.executescript(file.read())
            else:
                print(f"오류: {sql_file} 파일이 존재하지 않습니다.")
        g.db = db
    return g.db


def reset_db():
    if "db" in g:
        g.db.close()
    g.db = sqlite3.connect(":memory:")
    for sql_file in SQL_FILES:
        sql_path = os.path.join(SQL_FOLDER, sql_file)
        if os.path.exists(sql_path):
            with open(sql_path, "r") as file:
                g.db.executescript(file.read())
        else:
            print(f"오류: {sql_file} 파일이 존재하지 않습니다.")


def execute_query_with_rollback(db, query, params=None):
    cursor = db.cursor()
    try:
        cursor.execute("BEGIN")
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        columns = (
            [description[0] for description in cursor.description]
            if cursor.description
            else []
        )

        if query.strip().upper().startswith("SELECT"):
            db.commit()
        else:
            db.rollback()

        return {"result": result, "columns": columns}
    except sqlite3.Error as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@sqool_artist_bp.before_request
def before_request():
    if "client_id" not in session:
        session["client_id"] = str(generate())  # * nanoid로 client_id 생성
    g.client_id = session["client_id"]
    g.db = get_db()


@sqool_artist_bp.teardown_request
def teardown_request(exception):
    db = g.pop("db", None)
    if db is not None:
        db.rollback()
        db.close()


@sqool_artist_bp.route("/query", methods=["POST"])
def execute_query():
    data = request.json
    query = data.get("query")
    params = data.get("params", [])

    if not query:
        return jsonify({"status": "쿼리값이 없습니다."}), 400

    try:
        result = execute_query_with_rollback(g.db, query, params)
        return jsonify(result)
    except sqlite3.Error as e:
        return jsonify({"status": f"잘못된 요청입니다: {str(e)}"}), 400


@sqool_artist_bp.route("/reset", methods=["POST"])
def reset_database():
    reset_db()
    return jsonify({"status": "데이터베이스가 초기화 되었습니다."}), 200
