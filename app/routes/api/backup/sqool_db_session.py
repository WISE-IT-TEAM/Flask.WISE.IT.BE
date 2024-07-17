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


def get_db():
    db = session.get("db_connection")

    if not db:
        return jsonify({"status": "먼저 데이터베이스를 생성하세요"}), 400
        
    return db


def execute_query_with_rollback(query):
    db = get_db()
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

        session["db_connection"] = db
        
        return {"result": result, "columns": columns}
    except sqlite3.Error as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@sqool_db_bp.route('/', methods=["POST"])
def create_db():
    data = request.json
    dbname = data.get("dbname")

    if dbname not in DB_CONFIGS:
        return jsonify({"status": "잘못된 데이터베이스 이름입니다."}), 400
    
    SQL_FOLDER = DB_CONFIGS[dbname]["folder"]
    SQL_FILES = DB_CONFIGS[dbname]["files"]

    # client_id = session.get('client_id')
    # if not client_id:
    #     client_id = str(generate())
    #     session["client_id"] = client_id
    
    # if client_id not in db_connections:
    if not session.get("db_connection"):
        db = sqlite3.connect(":memory:", check_same_thread=False)
        for sql_file in SQL_FILES:
            sql_path = os.path.join(SQL_FOLDER, sql_file)
            if os.path.exists(sql_path):
                with open(sql_path, "r", encoding="UTF-8") as file:
                    db.executescript(file.read())
            else:
                print(f"오류: {sql_file} 파일이 존재하지 않습니다.")
        session["db_connection"] = [db]

        return jsonify({"status": "사용자 데이터베이스가 정상적으로 생성되었습니다."}), 200

@sqool_db_bp.route("/schema", methods=["GET"])
def get_schema():
    db = get_db()
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
        return jsonify(result)
    except sqlite3.Error as e:
        return jsonify({"status": f"잘못된 요청입니다: {str(e)}"}), 400


@sqool_db_bp.route("/reset", methods=["POST"])
def reset_database():
    session.pop("db_connection")
    
    create_db()

    return jsonify({"status": "데이터베이스가 초기화 되었습니다."}), 200


# @sqool_db_bp.teardown_app_request
# def teardown_db(exception):
    