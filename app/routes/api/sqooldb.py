from flask import Blueprint, request, jsonify, session, current_app
import sqlite3
import os
from nanoid import generate
import redis
import pickle
import time

sqooldb_api_bp = Blueprint("sqooldb_api", __name__)

# * DB 폴더 경로 및 SQL 파일 리스트
DB_CONFIGS = {
    "Artist": {
        "folder": os.path.join(os.path.dirname(__file__), "../../static/ArtistDB"),
        "files": ["Table.sql", "Artist.sql", "Member.sql", "Album.sql"],
    },
    # 다른 데이터베이스 설정을 여기에 추가할 수 있습니다.
}

# Redis 클라이언트 설정
REDIS_URI = os.environ.get("REDIS_URI")
REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_KEY = os.environ.get("REDIS_KEY")
redis_client = redis.Redis(host=REDIS_URI, port=REDIS_PORT, password=REDIS_KEY)

# 만료 시간 설정 (7,200초 = 2시간)
EXPIRY_TIME = 60


# 세션별 데이터베이스 연결을 저장할 딕셔너리
# db_connections = {}


def get_db_connection(sqldb_id):
    db_conn = redis_client.get(f"db_conn:{sqldb_id}")
    if db_conn:
        # 연결 정보가 있으면 만료 시간 갱신
        redis_client.expire(f"db_conn:{sqldb_id}", EXPIRY_TIME)
        return pickle.loads(db_conn)
    return None


def set_db_connection(sqldb_id, db):
    redis_client.setex(f"db_conn:{sqldb_id}", EXPIRY_TIME, pickle.dumps(db))


def update_last_activity(sqldb_id):
    redis_client.expire(f"db_conn:{sqldb_id}", EXPIRY_TIME)


def execute_query_with_rollback(query):
    sqldb_id = session.get("sqldb_id")

    if not sqldb_id:
        return jsonify({"status": "session에서 sqldb_id를 받아오지 못 함"}), 412

    # if sqldb_id not in db_connections.keys():
    #     return jsonify({"status": "해당 spldb_id로 생성된 DB가 없음"}), 412

    # db = db_connections[sqldb_id]

    db = get_db_connection(sqldb_id)
    print("db_connections의 값: ", db)

    if not db:
        return jsonify({"status": "해당 spldb_id로 생성된 DB가 없음"}), 412

    update_last_activity(sqldb_id)

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
    data = request.json
    dbname = data.get("dbname")

    if not dbname:
        return jsonify({"status": "DB 정보가 오지 않음"}), 403
    elif dbname not in DB_CONFIGS.keys():
        return jsonify({"status": "DB 이름이 올바르지 않음"}), 404

    # 이미 DB가 있을 경우 해당 connection을 삭제 후 DB 생성 (RESET)
    sqldb_id = data.get("sqldb_id")
    # if sqldb_id and sqldb_id in db_connections.keys():
    #     del db_connections[sqldb_id]

    if sqldb_id:
        old_db = get_db_connection(sqldb_id)
        if old_db:
            old_db.close()
            redis_client.delete(f"db_conn:{sqldb_id}")

    SQL_FOLDER = DB_CONFIGS[dbname]["folder"]
    SQL_FILES = DB_CONFIGS[dbname]["files"]

    sqldb_id = str(generate())
    session["sqldb_id"] = sqldb_id
    session.modified = True
    # print("create_db에서 세션 값: ", session)

    db = sqlite3.connect(":memory:", check_same_thread=False)
    for sql_file in SQL_FILES:
        sql_path = os.path.join(SQL_FOLDER, sql_file)
        if os.path.exists(sql_path):
            with open(sql_path, "r", encoding="UTF-8") as file:
                db.executescript(file.read())
        else:
            return jsonify({"status": "{sql_file} 파일이 존재하지 않음"}), 400

    # db_connections[sqldb_id] = db
    set_db_connection(sqldb_id, db)

    return jsonify({"status": "사용자 DB 정상적으로 생성"}), 200


@sqooldb_api_bp.route("/schema", methods=["GET"])
def get_schema():
    sqldb_id = session.get("sqldb_id")

    # if sqldb_id not in db_connections.keys():
    #     return jsonify({"status": "DB가 생성되지 않음"}), 412

    # db = db_connections[sqldb_id]

    db = get_db_connection(sqldb_id)
    if not db:
        return jsonify({"status": "DB가 생성되지 않음"}), 412

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
    data = request.json
    query = data.get("query")

    SQL_KEYWORD = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP"]

    # print("excute_db에서 세션 값:", session)

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


@sqooldb_api_bp.before_request
def before_request():
    sqldb_id = session.get("sqldb_id")
    if sqldb_id:
        update_last_activity(sqldb_id)


# '/reset' 대신 '/'를 통해 무조건 db를 재생성
# @sqooldb_api_bp.route("/reset", methods=["POST"])
# def reset_database():
#     sqldb_id = session.get('sqldb_id')

#     if sqldb_id in db_connections:
#         del db_connections[sqldb_id]

#     # check = create_db()
#     # print(check)

#     return jsonify({"status": "데이터베이스가 초기화 되었습니다."}), 200
