from flask import Blueprint, request, jsonify, session
import sqlite3
import os
from nanoid import generate
import threading

class BaseBlueprint:
    def __init__(self, name, import_name, sql_files):
        self.bp = Blueprint(name, import_name)
        self.sql_folder = os.path.join(os.path.dirname(__file__), "../../static/ArtistDB")
        self.sql_files = sql_files
        self.db_connections = {}
        self.lock = threading.Lock()

        self.register_routes()


    def register_routes(self):
        @self.bp.route("/schema", methods=["GET"])
        def get_schema():
            db = self.get_db()
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

        @self.bp.route("/query", methods=["POST"])
        def execute_query():
            data = request.json
            query = data.get("query")

            if not query:
                return jsonify({"status": "쿼리값이 없습니다."}), 400

            try:
                db = self.get_db()
                result = self.execute_query_with_rollback(db, query)
                return jsonify(result)
            except sqlite3.Error as e:
                print(f"SQL 오류: {str(e)}")
                return jsonify({"status": f"잘못된 요청입니다: {str(e)}"}), 400
            except Exception as e:
                print(f"예상치 못한 오류: {str(e)}")
                return jsonify({"status": "서버 내부 오류 발생"}), 500
                


        @self.bp.route("/reset", methods=["POST"])
        def reset_database():
            client_id = session.get('client_id')

            if client_id in self.db_connections:
                self.db_connections[client_id].close()
                del self.db_connections[client_id]
            
            self.get_db()

            return jsonify({"status": "데이터베이스가 초기화 되었습니다."}), 200


        # @staticmethod
        # @self.bp.teardown_app_request
        # def teardown_db(exception):
        #     client_id = session.get('client_id')

        #     if client_id in self.db_connections:
        #         self.db_connections[client_id].close()
        #         del self.db_connections[client_id]


    def get_blueprint(self):
        return self.bp
    

    def get_db(self):
        client_id = session.get('client_id')
        if not client_id:
            client_id = str(generate())
            session["client_id"] = client_id
        
        with self.lock:
            if client_id not in self.db_connections:
                print(f"새로운 db 연결 생성: {client_id}")
                try:
                    db = sqlite3.connect(":memory:", check_same_thread=False)
                    for sql_file in self.sql_files:
                        sql_path = os.path.join(self.sql_folder, sql_file)
                        if os.path.exists(sql_path):
                            with open(sql_path, "r", encoding="UTF-8") as file:
                                db.executescript(file.read())
                        else:
                            print(f"오류: {sql_file} 파일이 존재하지 않습니다.")
                    self.db_connections[client_id] = db
                except sqlite3.Error as e:
                    print(f"db 연결 오류: {str(e)}")
                    raise
            else:
                print(f'기존 db 연결 사용: {client_id}')
        return self.db_connections[client_id]
    

    def execute_query_with_rollback(self, db, query):
        # db = self.get_db()
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