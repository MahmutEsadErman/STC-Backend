import os

import mysql.connector
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

host = os.environ.get("HOST")
userDb = os.environ.get("USER")
passDb = os.environ.get("PASS")
db = os.environ.get("DB")


@app.route('/', methods=["GET"])
def database_deneme():
    return "hello world"


@app.route('/api/data/subject', methods=["GET"])
def get_subject_data():
    try:
        querySubject = "SELECT * FROM Deneme;"

        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)

        cursor = conn.cursor()
        cursor.execute(querySubject)
        # Fetch results
        results = cursor.fetchall()
        for row in results:
            print(row)

        # Clean up

        # res = []
        # for i in resLesson:
        #     res.append({
        #         "subjectId": i["ID"],
        #         "lessonName": i["DersAdi"],
        #         "subjectName": i["KonuAdi"]
        #     })
        #
        # if not res:
        #     return make_response(jsonify('{error: subject not found}'), 404)
        cursor.close()
        conn.close()
        return make_response(jsonify(results), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)
    finally:
        pass


@app.route("/api/login", methods=["POST"])
def user_login():
    try:

        return make_response(jsonify('{success:.ok başarılı}'), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)


if __name__ == '__main__':
    app.run(debug=True)
