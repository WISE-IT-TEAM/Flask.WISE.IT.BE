from flask import Blueprint, request, jsonify, session
import sqlite3
import os
from nanoid import generate

sqool_db_bp = Blueprint("sqool_db", __name__)

# * DB 폴더 경로 및 SQL 파일 리스트
DB_CONFIGS = {
    "Artist": {
        "folder": os.path.join(os.path.dirname(__file__), "../../static/ArtistDB"),
        "files": ["Table.sql", "Artist.sql", "Member.sql", "Album.sql"],
    },
    # 다른 데이터베이스 설정을 여기에 추가할 수 있습니다.
}


# 세션별 데이터베이스 연결을 저장할 딕셔너리
db_connections = {}


def execute_query_with_rollback(query):
    sqldb_id = session.get("sqldb_id")

    if sqldb_id not in db_connections.keys():
        return jsonify({"status": "DB가 생성되지 않았습니다."}), 400

    db = db_connections[sqldb_id]

    cursor = db.cursor()
    try:
        cursor.execute("BEGIN")
        cursor.execute(query)
        result = cursor.fetchall()
        columns = (
            [description[0] for description in cursor.description]
            if cursor.description
            else []
        )
        db.commit()

        return jsonify({"result": result, "columns": columns}), 200
    except sqlite3.Error as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@sqool_db_bp.route("/", methods=["POST"])
def create_db():
    data = request.json
    dbname = data.get("dbname")

    if not dbname:
        return jsonify({"status": "DB 정보가 없습니다."}), 400
    elif dbname not in DB_CONFIGS.keys():
        return jsonify({"status": "DB 이름이 올바르지 않습니다."}), 400

    # 이미 DB가 있을 경우 해당 connection을 삭제 후 DB 생성 (RESET)
    sqldb_id = session.get("sqldb_id")
    if sqldb_id:
        del db_connections[sqldb_id]

    SQL_FOLDER = DB_CONFIGS[dbname]["folder"]
    SQL_FILES = DB_CONFIGS[dbname]["files"]

    sqldb_id = str(generate())
    session["sqldb_id"] = sqldb_id

    db = sqlite3.connect(":memory:", check_same_thread=False)
    for sql_file in SQL_FILES:
        sql_path = os.path.join(SQL_FOLDER, sql_file)
        if os.path.exists(sql_path):
            with open(sql_path, "r", encoding="UTF-8") as file:
                db.executescript(file.read())
        else:
            print(f"오류: {sql_file} 파일이 존재하지 않습니다.")

    db_connections[sqldb_id] = db

    return jsonify({"status": "사용자 데이터베이스가 정상적으로 생성되었습니다."}), 200


@sqool_db_bp.route("/schema", methods=["GET"])
def get_schema():
    sqldb_id = session.get("sqldb_id")

    if sqldb_id not in db_connections.keys():
        return jsonify({"status": "DB가 생성되지 않았습니다."}), 400

    db = db_connections[sqldb_id]
    cursor = db.cursor()

    # 모든 테이블 가져오기
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]

    schema = {}
    for table in tables:
        # 각 테이블의 컬럼 정보 가져오기
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        schema[table] = [
            {
                "Columns": column[1].upper(),
                "Type": column[2].upper(),
            }
            for column in columns
        ]

    cursor.close()
    return jsonify(schema)


@sqool_db_bp.route("/query", methods=["POST"])
def execute_query():
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"status": "쿼리값이 없습니다."}), 400

    try:
        result = execute_query_with_rollback(query)
        return result
    except sqlite3.Error as e:
        return jsonify({"status": f"잘못된 요청입니다: {str(e)}"}), 400


# '/reset' 대신 '/'를 통해 무조건 db를 재생성
# @sqool_db_bp.route("/reset", methods=["POST"])
# def reset_database():
#     sqldb_id = session.get('sqldb_id')

#     if sqldb_id in db_connections:
#         del db_connections[sqldb_id]

#     # check = create_db()
#     # print(check)

#     return jsonify({"status": "데이터베이스가 초기화 되었습니다."}), 200
