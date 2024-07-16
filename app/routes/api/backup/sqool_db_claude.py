from flask import Blueprint, request, jsonify, session
import sqlite3
import os
from nanoid import generate

# SQLite 데이터베이스를 관리하기 위한 Flask 블루프린트 생성
sqool_db_bp = Blueprint("sqool_db", __name__)

# DB 폴더 경로 및 SQL 파일 리스트를 현재 파일에 직접 정의
DB_CONFIGS = {
    "Artist": {
        "folder": os.path.join(os.path.dirname(__file__), "../../static/ArtistDB"),
        "files": ["Table.sql", "Artist.sql", "Member.sql", "Album.sql"],
    },
    # 다른 데이터베이스 설정을 여기에 추가할 수 있습니다.
}

# 세션별 데이터베이스 연결을 저장할 딕셔너리
db_connections = {}

# 현재 사용 중인 데이터베이스 이름을 저장할 변수
current_db_name = None


def get_db():
    """세션별 데이터베이스 연결을 생성하거나 반환하는 함수"""
    global current_db_name
    client_id = session.get("client_id")
    if not client_id:
        client_id = str(generate())
        session["client_id"] = client_id

    if client_id not in db_connections:
        # 새로운 인메모리 데이터베이스 연결 생성
        db = sqlite3.connect(":memory:", check_same_thread=False)
        if current_db_name and current_db_name in DB_CONFIGS:
            db_folder = DB_CONFIGS[current_db_name]["folder"]
            db_files = DB_CONFIGS[current_db_name]["files"]
            # SQL 파일들을 실행하여 데이터베이스 구조 생성
            for sql_file in db_files:
                sql_path = os.path.join(db_folder, sql_file)
                if os.path.exists(sql_path):
                    with open(sql_path, "r", encoding="UTF-8") as file:
                        db.executescript(file.read())
                else:
                    print(f"오류: {sql_file} 파일이 존재하지 않습니다.")
        db_connections[client_id] = db

    return db_connections[client_id]


def execute_query_with_rollback(query):
    """쿼리를 실행하고 결과를 반환하는 함수 (오류 시 롤백)"""
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
        return {"result": result, "columns": columns}
    except sqlite3.Error as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@sqool_db_bp.route("/", methods=["POST"])
def create_db():
    """사용자 데이터베이스를 생성하는 라우트"""
    global current_db_name
    data = request.json
    dbname = data.get("dbname")

    if dbname not in DB_CONFIGS:
        return jsonify({"status": "잘못된 데이터베이스 이름입니다."}), 400

    current_db_name = dbname
    get_db()

    return jsonify({"status": "사용자 데이터베이스가 정상적으로 생성되었습니다."}), 200


@sqool_db_bp.route("/schema", methods=["GET"])
def get_schema():
    """데이터베이스 스키마 정보를 반환하는 라우트"""
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]

    schema = {}
    for table in tables:
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
    """사용자 쿼리를 실행하고 결과를 반환하는 라우트"""
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"status": "쿼리가 제공되지 않았습니다."}), 400

    try:
        result = execute_query_with_rollback(query)
        return jsonify(result)
    except sqlite3.Error as e:
        return jsonify({"status": f"잘못된 요청입니다: {str(e)}"}), 400


@sqool_db_bp.route("/reset", methods=["POST"])
def reset_database():
    """데이터베이스를 초기화하는 라우트"""
    global current_db_name
    client_id = session.get("client_id")

    if client_id in db_connections:
        db_connections[client_id].close()
        del db_connections[client_id]

    current_db_name = None
    get_db()

    return jsonify({"status": "데이터베이스가 초기화되었습니다."}), 200


@sqool_db_bp.teardown_app_request
def teardown_db(exception):
    """요청 종료 시 데이터베이스 연결을 정리하는 함수"""
    client_id = session.get("client_id")

    if client_id in db_connections:
        db_connections[client_id].close()
        del db_connections[client_id]
