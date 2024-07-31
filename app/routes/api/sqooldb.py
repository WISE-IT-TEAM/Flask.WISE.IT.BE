from flask import Blueprint, request, jsonify, session
from nanoid import generate
import sqlite3
import os
from datetime import datetime, timedelta
import threading
import time

sqooldb_api_bp = Blueprint("sqooldb_api", __name__)

# DB 폴더 경로 및 SQL 파일 리스트
DB_CONFIGS = {
    "Artist": {
        "folder": os.path.join(os.path.dirname(__file__), "../../static/ArtistDB"),
        "files": ["Table.sql", "Artist.sql", "Member.sql", "Album.sql"],
    },
    # 다른 데이터베이스 설정을 여기에 추가할 수 있습니다.
}

# 세션별 데이터베이스 연결과 마지막 사용 시간을 저장할 딕셔너리
db_connections = {}

# 연결 타임아웃 시간 (2시간)
CONNECTION_TIMEOUT = timedelta(hours=2)

# 스레드 안전성을 위한 락
connection_lock = threading.Lock()


def clean_old_connections():
    """
    주기적으로 오래된 DB 연결을 정리하는 함수
    """
    while True:
        current_time = datetime.now()
        to_remove = []
        with connection_lock:
            for sqldb_id, connection_info in db_connections.items():
                if current_time - connection_info["last_used"] > CONNECTION_TIMEOUT:
                    connection_info["connection"].close()
                    to_remove.append(sqldb_id)

            for sqldb_id in to_remove:
                del db_connections[sqldb_id]

        time.sleep(300)  # 5분마다 체크


# 백그라운드에서 오래된 연결 정리
cleaning_thread = threading.Thread(target=clean_old_connections, daemon=True)
cleaning_thread.start()


def execute_query_with_rollback(query):
    """
    주어진 쿼리를 실행하고 결과를 반환하는 함수
    오류 발생 시 롤백을 수행합니다.
    """
    sqldb_id = session.get("sqldb_id")

    if not sqldb_id:
        return jsonify({"status": "session에서 sqldb_id를 받아오지 못 함"}), 412

    with connection_lock:
        if sqldb_id not in db_connections:
            return jsonify({"status": "해당 spldb_id로 생성된 DB가 없음"}), 412

        connection_info = db_connections[sqldb_id]
        db = connection_info["connection"]
        connection_info["last_used"] = datetime.now()

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

        return (
            jsonify(
                {
                    "message": "쿼리가 정상적으로 실행되었습니다.",
                    "result": result,
                    "columns": columns,
                    "status": "쿼리 실행 성공",
                }
            ),
            200,
        )
    except sqlite3.Error as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


@sqooldb_api_bp.route("/init", methods=["POST"])
def create_db():
    """
    새로운 DB 연결을 생성하는 API 엔드포인트
    """
    data = request.json
    dbname = data.get("dbname")

    if not dbname:
        return jsonify({"status": "DB 정보가 오지 않음"}), 403
    elif dbname not in DB_CONFIGS:
        return jsonify({"status": "DB 이름이 올바르지 않음"}), 404

    # 이미 DB가 있을 경우 해당 connection을 삭제 후 DB 생성 (RESET)
    sqldb_id = session.get("sqldb_id")
    if sqldb_id:
        with connection_lock:
            if sqldb_id in db_connections:
                db_connections[sqldb_id]["connection"].close()
                del db_connections[sqldb_id]
        session.pop("sqldb_id", None)

    SQL_FOLDER = DB_CONFIGS[dbname]["folder"]
    SQL_FILES = DB_CONFIGS[dbname]["files"]

    sqldb_id = str(generate())
    session["sqldb_id"] = sqldb_id
    session.modified = True

    db = sqlite3.connect(":memory:", check_same_thread=False)
    for sql_file in SQL_FILES:
        sql_path = os.path.join(SQL_FOLDER, sql_file)
        if os.path.exists(sql_path):
            with open(sql_path, "r", encoding="UTF-8") as file:
                db.executescript(file.read())
        else:
            return jsonify({"status": f"{sql_file} 파일이 존재하지 않음"}), 400

    with connection_lock:
        db_connections[sqldb_id] = {"connection": db, "last_used": datetime.now()}

    return jsonify({"status": "사용자 DB 정상적으로 생성"}), 200


@sqooldb_api_bp.route("/schema", methods=["GET"])
def get_schema():
    """
    현재 DB의 스키마 정보를 반환하는 API 엔드포인트
    """
    sqldb_id = session.get("sqldb_id")

    if not sqldb_id:
        return jsonify({"status": "session에서 sqldb_id를 받아오지 못 함"}), 412

    with connection_lock:
        if sqldb_id not in db_connections:
            return jsonify({"status": "DB가 생성되지 않음"}), 412

        connection_info = db_connections[sqldb_id]
        db = connection_info["connection"]
        connection_info["last_used"] = datetime.now()

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
    return jsonify({"status": "스키마 불러오기 성공", "schema": schema}), 200


@sqooldb_api_bp.route("/query", methods=["POST"])
def execute_query():
    """
    사용자가 입력한 쿼리를 실행하는 API 엔드포인트
    """
    data = request.json
    query = data.get("query")

    SQL_KEYWORD = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP"]

    if not query or query.isspace():
        return (
            jsonify({"message": "쿼리를 입력해주세요.", "status": "쿼리값이 없음"}),
            412,
        )

    if query.split()[0].upper() not in SQL_KEYWORD:
        return (
            jsonify(
                {
                    "message": "쿼리를 다시 한번 확인해 보세요.",
                    "status": "SQL_KEYWORD에 해당하지 않은 시작",
                }
            ),
            202,
        )

    try:
        result = execute_query_with_rollback(query)
        return result
    except sqlite3.Error as e:
        return (
            jsonify(
                {
                    "message": "쿼리를 다시 한번 확인해 보세요.",
                    "status": f"잘못된 요청: {str(e)}",
                }
            ),
            202,
        )


@sqooldb_api_bp.route("/close", methods=["POST"])
def close_connection():
    """
    현재 세션의 DB 연결을 닫고 정리하는 API 엔드포인트
    """
    sqldb_id = session.get("sqldb_id")
    if sqldb_id:
        with connection_lock:
            if sqldb_id in db_connections:
                db_connections[sqldb_id]["connection"].close()
                del db_connections[sqldb_id]
        session.pop("sqldb_id", None)
        return jsonify({"status": "DB 연결이 성공적으로 닫혔습니다."}), 200
    else:
        return jsonify({"status": "활성화된 DB 연결이 없습니다."}), 200
