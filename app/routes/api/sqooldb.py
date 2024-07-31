from flask import Blueprint, request, jsonify, current_app, session
import sqlite3
import os
import time
import threading
from contextlib import closing
from functools import wraps
from nanoid import generate
from apscheduler.schedulers.background import BackgroundScheduler

sqooldb_api_bp = Blueprint("sqooldb_api", __name__)

# DB 설정
DB_CONFIGS = {
    "Artist": {
        "folder": os.path.join(os.path.dirname(__file__), "../../static/ArtistDB"),
        "files": ["Table.sql", "Artist.sql", "Member.sql", "Album.sql"],
    },
    # 다른 데이터베이스 설정을 여기에 추가할 수 있습니다.
}

# 허용된 SQL 키워드 리스트
ALLOWED_SQL_KEYWORDS = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP"]

# 전역 변수로 데이터베이스 연결과 마지막 사용 시간을 저장
db_connections = {}
db_connections_lock = threading.Lock()


def get_db():
    """
    현재 요청에 대한 데이터베이스 연결을 반환합니다.
    연결이 없으면 새로 생성하고, 있으면 재사용합니다.
    """
    sqldb_id = session.get("sqldb_id")
    if not sqldb_id:
        raise ValueError("SQLDB ID가 없습니다")

    current_time = time.time()

    with db_connections_lock:
        if sqldb_id in db_connections:
            db, last_used = db_connections[sqldb_id]
            if current_time - last_used < current_app.config.get(
                "DB_CONNECTION_TIMEOUT", 3600
            ):
                db_connections[sqldb_id] = (db, current_time)
                return db
            else:
                db.close()
                del db_connections[sqldb_id]

        # db = sqlite3.connect(f":memory:{sqldb_id}", check_same_thread=False)
        db = sqlite3.connect(":memory:", check_same_thread=False)
        db.row_factory = sqlite3.Row
        db_connections[sqldb_id] = (db, current_time)
        return db


def require_db(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            get_db()
        except ValueError:
            return jsonify({"status": "DB가 초기화되지 않았습니다"}), 412
        return f(*args, **kwargs)

    return decorated_function


@sqooldb_api_bp.teardown_app_request
def close_db(exception):
    """요청이 완료될 때 데이터베이스 연결을 정리합니다."""
    current_time = time.time()
    timeout = current_app.config.get("DB_CONNECTION_TIMEOUT", 3600)

    with db_connections_lock:
        for sqldb_id, (db, last_used) in list(db_connections.items()):
            if current_time - last_used > timeout:
                db.close()
                del db_connections[sqldb_id]


def cleanup_old_connections():
    """주기적으로 오래된 연결을 정리하는 함수"""
    current_time = time.time()
    timeout = current_app.config.get("DB_CONNECTION_TIMEOUT", 3600)

    with db_connections_lock:
        for sqldb_id, (db, last_used) in list(db_connections.items()):
            if current_time - last_used > timeout:
                db.close()
                del db_connections[sqldb_id]


def setup_periodic_cleanup(app):
    """애플리케이션 시작 시 주기적 정리 작업을 설정합니다."""
    if not app.config.get("TESTING", False):
        scheduler = BackgroundScheduler()
        scheduler.add_job(cleanup_old_connections, "interval", hours=1)
        scheduler.start()


def is_safe_query(query):
    """주어진 쿼리가 안전한지 검사합니다."""
    first_word = query.strip().split()[0].upper()
    return first_word in ALLOWED_SQL_KEYWORDS


def execute_query_with_rollback(query):
    """주어진 쿼리를 실행하고 결과를 반환합니다. 오류 발생 시 롤백을 수행합니다."""
    db = get_db()
    with db:  # 트랜잭션 시작
        cursor = db.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            columns = (
                [description[0] for description in cursor.description]
                if cursor.description
                else []
            )
            return {
                "message": "쿼리가 성공적으로 실행되었습니다",
                "result": [dict(zip(columns, row)) for row in result],
                "columns": columns,
                "status": "쿼리 실행 성공",
            }, 200
        except sqlite3.Error as e:
            # 트랜잭션이 자동으로 롤백됩니다
            current_app.logger.error(f"데이터베이스 오류: {str(e)}")
            return {
                "message": "쿼리 실행 중 오류가 발생했습니다",
                "status": f"오류: {str(e)}",
            }, 500


@sqooldb_api_bp.route("/init", methods=["POST"])
def create_db():
    """새로운 데이터베이스를 초기화합니다."""
    data = request.json
    dbname = data.get("dbname")

    if not dbname:
        return jsonify({"status": "DB 정보가 제공되지 않았습니다"}), 403
    elif dbname not in DB_CONFIGS.keys():
        return jsonify({"status": "유효하지 않은 DB 이름입니다"}), 404

    sqldb_id = str(generate())
    session["sqldb_id"] = sqldb_id
    session.modified = True

    db = get_db()
    SQL_FOLDER = DB_CONFIGS[dbname]["folder"]
    SQL_FILES = DB_CONFIGS[dbname]["files"]

    for sql_file in SQL_FILES:
        sql_path = os.path.join(SQL_FOLDER, sql_file)
        if os.path.exists(sql_path):
            with open(sql_path, "r", encoding="UTF-8") as file:
                db.executescript(file.read())
        else:
            return jsonify({"status": f"{sql_file} 파일이 존재하지 않습니다"}), 400

    return jsonify({"status": "사용자 DB가 성공적으로 생성되었습니다"}), 200


@sqooldb_api_bp.route("/schema", methods=["GET"])
@require_db
def get_schema():
    """데이터베이스 스키마 정보를 반환합니다."""
    db = get_db()
    with closing(db.cursor()) as cursor:
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

    return (
        jsonify({"status": "스키마를 성공적으로 불러왔습니다", "schema": schema}),
        200,
    )


@sqooldb_api_bp.route("/query", methods=["POST"])
@require_db
def execute_query():
    """사용자가 제공한 SQL 쿼리를 실행합니다."""
    data = request.json
    query = data.get("query")

    if not query or query.isspace():
        return (
            jsonify(
                {
                    "message": "쿼리를 입력해주세요",
                    "status": "쿼리가 제공되지 않았습니다",
                }
            ),
            412,
        )

    if not is_safe_query(query):
        return (
            jsonify(
                {
                    "message": f"허용되지 않은 SQL 키워드입니다. 허용된 키워드: {', '.join(ALLOWED_SQL_KEYWORDS)}",
                    "status": "안전하지 않은 쿼리",
                }
            ),
            403,
        )

    result, status_code = execute_query_with_rollback(query)
    return jsonify(result), status_code
