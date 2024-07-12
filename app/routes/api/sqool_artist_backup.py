from flask import Blueprint, request, jsonify, g, session
import sqlite3
import os
from nanoid import generate


sqool_artist_bp = Blueprint("sqool_artist", __name__)


# * ArtistDB 폴더 경로 및 SQL 파일 리스트
SQL_FOLDER = os.path.join(os.path.dirname(__file__), "../../static/ArtistDB")
SQL_FILES = ["Table.sql", "Artist.sql", "Member.sql", "Album.sql"]


# 세션별 데이터베이스 연결을 저장할 딕셔너리
db_connections = {}


def get_db():
    client_id = session.get('client_id')
    if client_id not in db_connections:
        db = sqlite3.connect(':memory:', check_same_thread=False)
        for sql_file in SQL_FILES:
            sql_path = os.path.join(SQL_FOLDER, sql_file)
            if os.path.exists(sql_path):
                with open(sql_path, "r", encoding="UTF-8") as file:
                    db.executescript(file.read())
            else:
                print(f"오류: {sql_file} 파일이 존재하지 않습니다.")
        db_connections[client_id] = db


        print('get_db에서 확인', db_connections)




# def reset_db():
#     client_id = session.get('client_id')
#     if client_id in db_connections:
#         db_connections[client_id].close()
#         del db_connections[client_id]
#     db = sqlite3.connect(':memory:', check_same_thread=False)
#     for sql_file in SQL_FILES:
#         sql_path = os.path.join(SQL_FOLDER, sql_file)
#         if os.path.exists(sql_path):
#             with open(sql_path, "r", encoding='UTF-8') as file:
#                 db.executescript(file.read())
#         else:
#             print(f"오류: {sql_file} 파일이 존재하지 않습니다.")
#     db_connections[client_id] = db



def execute_query_with_rollback(db, query):
    cursor = db.cursor()
    try:
        cursor.execute("BEGIN")
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [description[0] for description in cursor.description] if cursor.description else []
        db.commit()
        return {"result": result, "columns": columns}
    except sqlite3.Error as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@sqool_artist_bp.route("/start", methods=["POST"])
def start_query():
    if "client_id" not in session:
        # session["client_id"] = str(generate())  # * nanoid로 client_id 생성
        session["client_id"] = 'sesac'  # * nanoid로 client_id 생성
    try:
        get_db()
        return jsonify({"status": "DB가 생성되었습니다."}), 200
    except:
        return jsonify({"status": "DB 생성이 실패했습니다."}), 400


@sqool_artist_bp.route("/query", methods=["POST"])
def execute_query():
    if "client_id" not in session:
        return jsonify({"status": "세션이 없습니다. /start를 먼저 호출하세요."}), 400
    else:
        client_id = session.get('client_id')
   
    print('query에서 확인', db_connections)


    data = request.json
    query = data.get("query")


    if not query:
        return jsonify({"status": "쿼리값이 없습니다."}), 400


    try:
        db = db_connections.get(client_id)
        result = execute_query_with_rollback(db, query)
        return jsonify(result)
    except sqlite3.Error as e:
        return jsonify({"status": f"잘못된 요청입니다: {str(e)}"}), 400


@sqool_artist_bp.route("/reset", methods=["POST"])
def reset_database():
    reset_db()
    return jsonify({"status": "데이터베이스가 초기화 되었습니다."}), 200


@sqool_artist_bp.route("/exit", methods=["POST"])
def exit_session():
    client_id = session.get('client_id')
    if client_id in db_connections:
        db_connections[client_id].close()
        del db_connections[client_id]
    session.clear()
    return jsonify({"status": "세션이 종료되었습니다."}), 200


# 애플리케이션 종료 시 모든 데이터베이스 연결 정리
@sqool_artist_bp.teardown_app_request
def teardown_db(exception):
    for db in db_connections.values():
        db.close()
    db_connections.clear()

