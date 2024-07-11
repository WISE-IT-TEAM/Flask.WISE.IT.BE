from flask import Blueprint, request, jsonify, g, session
import sqlite3
import os
import re
from nanoid import generate

sqool_artist_bp = Blueprint("sqool_artist", __name__)

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
                print(f"경고: {sql_file} 파일이 존재하지 않습니다.")
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
            print(f"경고: {sql_file} 파일이 존재하지 않습니다.")


def is_safe_query(query):
    allowed_keywords = [
        "SELECT",
        "FROM",
        "WHERE",
        "AND",
        "OR",
        "IN",
        "LIKE",
        "BETWEEN",
        "ORDER BY",
        "GROUP BY",
        "HAVING",
        "LIMIT",
        "JOIN",
        "LEFT JOIN",
        "RIGHT JOIN",
        "INNER JOIN",
        "OUTER JOIN",
        "ON",
        "AS",
        "DISTINCT",
        "INSERT",
        "INTO",
        "VALUES",
        "UPDATE",
        "SET",
        "DELETE",
    ]

    query_upper = query.upper()
    for keyword in allowed_keywords:
        query_upper = query_upper.replace(keyword, "")

    query_upper = re.sub(r"[A-Z_][A-Z0-9_]*", "", query_upper)
    query_upper = re.sub(r"'[^']*'", "", query_upper)
    query_upper = re.sub(r"\d+", "", query_upper)

    return len(query_upper.strip()) == 0


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
        session["client_id"] = str(generate())
    g.client_id = session["client_id"]
    g.db = get_db()


@sqool_artist_bp.teardown_request
def teardown_request(exception):
    db = g.pop("db", None)
    if db is not None:
        db.rollback()
        db.close()


@sqool_artist_bp.route("/execute", methods=["POST"])
def execute_query():
    data = request.json
    query = data.get("query")
    params = data.get("params", [])

    if not query:
        return jsonify({"error": "No query provided."}), 400

    if not is_safe_query(query):
        return (
            jsonify(
                {
                    "error": "Unsafe query detected. Only allowed SQL operations are permitted."
                }
            ),
            400,
        )

    try:
        result = execute_query_with_rollback(g.db, query, params)
        return jsonify(result)
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 400


@sqool_artist_bp.route("/reset", methods=["POST"])
def reset_database():
    reset_db()
    return jsonify({"status": "Database reset to initial state."})
