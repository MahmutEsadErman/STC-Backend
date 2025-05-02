import os

import mysql.connector
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

host = "MYSQL1002.site4now.net"
userDb = "ab83bf_stcadmi"
passDb = "Turkiye1461."
db = "db_ab83bf_stcadmi"


@app.route('/', methods=["GET"])
def database_deneme():
    return "hello world"


@app.route('/example', methods=["GET"])
def example():
    try:
        # Example query
        query = "SELECT * FROM deneme;"

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)

        # Create a cursor to interact with the database
        cursor = conn.cursor()
        cursor.execute(query)

        # Fetch results
        results = cursor.fetchall()

        # Process results
        response = []
        for i in results:
            response.append({
                "id": i[0],
                "name": i[1],
                "age": i[2]
            })

        # Clean up
        cursor.close()
        conn.close()

        if not response:
            return make_response(jsonify('{error: subject not found}'), 404)

        # Return the response
        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)


@app.route("/saveTimetable/", methods=["POST"])
def save_timetable():
    try:
        user_id = request.json["userId"]
        timesheet = request.json["timesheet"]

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)

        # Create a cursor to interact with the database
        cursor = conn.cursor()

        for entry in timesheet:
            work_date = entry["workDate"]
            start_time = entry["startTime"]
            end_time = entry["endTime"]
            break_time = entry["breakTime"]
            hours_target = entry["hoursTarget"]
            hours_as_is = entry["hoursAsIs"]
            absence = entry["absence"]
            comment = entry["comment"]
            checked = entry["status"]

            cursor.execute(f"""
                INSERT INTO work_time_sheet
                VALUES ({user_id}, {work_date}, '{start_time}', {end_time}, {break_time}, {hours_target}, {hours_as_is}, {absence}, {comment}, {checked})
                            """)

        conn.commit()

        # Clean up
        cursor.close()
        conn.close()

        return make_response(jsonify('{success: work timesheet saved to the system}'), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)


@app.route("/sendTimetable", methods=["POST"])
def send_timetable():
    try:
        # Get userId
        user_id = request.json["userId"]
        new_status = "pending"

        query = f"""
            UPDATE work_time_sheet
            SET status = '{new_status}'
            WHERE user_id = {user_id};
        """

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)

        # Create a cursor to interact with the database
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)

        # Commit the changes
        conn.commit()

        return make_response(jsonify('{success: work timesheet sent to the supervisor}'), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)
    finally:
        # Clean up
        cursor.close()
        conn.close()


@app.route("/getTimetable/", methods=["GET"])
def get_timetable():
    try:
        # Get userId
        user_id = request.json["userId"]

        query = f" SELECT * FROM work_time_sheet WHERE user_id = {user_id}; "

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)

        # Create a cursor to interact with the database
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)

        # Fetch results
        results = cursor.fetchall()

        # Process results
        response = []
        for i in results:
            response.append({
                "userId": i[0],
                "workDate": i[1],
                "startTime": i[2],
                "endTime": i[3],
                "breakTime": i[4],
                "hoursTarget": i[5],
                "hoursAsIs": i[6],
                "absence": i[7],
                "comment": i[8],
                "checked": i[9]
            })

        # Clean up
        cursor.close()
        conn.close()

        if not response:
            return make_response(jsonify('{error: subject not found}'), 404)

        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)


@app.route("/api/login", methods=["POST"])
def user_login():
    try:

        return make_response(jsonify('{success:.ok başarılı}'), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)


if __name__ == '__main__':
    app.run(debug=True)
