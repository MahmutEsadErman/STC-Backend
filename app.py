import os

import mysql.connector
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database connection details
host = os.environ.get("HOST")
userDb = os.environ.get("USER")
passDb = os.environ.get("PASS")
db = os.environ.get("DB")


class NotificationTypes:
    SEND_TIMETABLE = 1
    TIMETABLE_APPROVAL = 2
    TIMETABLE_REJECTION = 3
    SICKNESS = 4
    VOCATION = 5
    VOCATION_APPROVAL = 6
    VOCATION_REJECTION = 7


@app.route('/', methods=["GET"])
def database_deneme():
    return "hello world"


@app.route("/saveTimetable", methods=["POST"])
def save_timetable():
    conn = None
    cursor = None
    try:
        user_id = request.json["userId"]
        timesheet = request.json["timesheet"]

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)

        # Create a cursor to interact with the database
        cursor = conn.cursor()

        query = "INSERT INTO work_time_sheet VALUES"

        for entry in timesheet:
            work_date = entry["workDate"]
            start_time = entry["startTime"]
            end_time = entry["endTime"]
            break_time = entry["breakTime"]
            hours_target = entry["hoursTarget"]
            hours_as_is = entry["hoursAsIs"]
            absence = entry["absence"]
            comment = entry["comment"]
            status = entry["status"]

            query += f" ({user_id}, '{work_date}', '{start_time}', '{end_time}', {break_time}, {hours_target}, {hours_as_is}, {absence}, '{comment}', {status}),"

        # Remove the last comma and add a semicolon
        query = query[:-1] + ";"

        cursor.execute(query)

        conn.commit()

        return make_response(jsonify('{success: work timesheet saved to the system}'), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)
    finally:
        # Clean up
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/sendTimetable", methods=["POST"])
def send_timetable():
    conn = None
    cursor = None
    try:
        # Get userId
        user_id = request.json["userId"]
        comment = request.json["comment"]
        new_status = "pending"

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)
        cursor = conn.cursor()

        # Get the supervisor's user_id
        query = f"SELECT user_id FROM supervisor WHERE group_id = (SELECT group_id FROM employee WHERE user_id = {user_id};)"
        cursor.execute(query)
        supervisor_id = cursor.fetchall()

        # Update the status of the work time sheet
        query = f"""
            UPDATE work_time_sheet
            SET status = '{new_status}'
            WHERE user_id = {user_id} AND status = 'pending';
        """

        # Notification for the supervisor
        query += f"""INSERT INTO notification (timestamp, reciever_id, submitter_id, type, status, empl_id, message) 
        VALUES (current_date, {supervisor_id}, {user_id}, {NotificationTypes.SEND_TIMETABLE}, 0, {user_id}, '{comment}');
        """

        # Execute the query
        cursor.execute(query)

        # Commit the changes
        conn.commit()

        return make_response(jsonify('{success: work timesheet sent to the supervisor}'), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)
    finally:
        # Clean up
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/getTimetable/<user_id>", methods=["GET"])
def get_timetable(user_id):
    conn = None
    cursor = None
    try:
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
                "startTime": str(i[2]),
                "endTime": str(i[3]),
                "breakTime": str(i[4]),
                "hoursTarget": str(i[5]),
                "hoursAsIs": str(i[6]),
                "absence": i[7],
                "comment": i[8],
                "status": i[9]
            })

        if not response:
            return make_response(jsonify('{error: subject not found}'), 404)

        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)
    finally:
        # Clean up
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Supervisor approves or rejects the timetable
@app.route("/respond_timetable", methods=["POST"])
def respond_timetable():
    conn = None
    cursor = None
    try:
        # Get data from the request
        user_id = request.json["userId"]
        employee_id = request.json["employeeId"]
        timetable_id = request.json["timetableId"]
        response = request.json["response"]  # "approve" or "reject"
        comment = request.json["comment"]

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)
        cursor = conn.cursor()

        # Determine the new status based on the response
        new_status = "approved" if response else "rejected"

        # Update the timetable status
        query = f"""
            UPDATE work_time_sheet
            SET status = '{new_status}'
            WHERE id = {timetable_id} AND user_id = {user_id};
        """
        cursor.execute(query)

        # Add a notification for the employee
        query = f"""
            INSERT INTO notification (timestamp, reciever_id, submitter_id, type, status, empl_id, message)
            VALUES (current_date, {employee_id}, {user_id}, {NotificationTypes.TIMETABLE_APPROVAL if response else NotificationTypes.TIMETABLE_REJECTION}, 0, {employee_id}, '{comment}');
        """
        cursor.execute(query)

        # Commit the changes
        conn.commit()

        return make_response(jsonify('{success: timetable response recorded}'), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)
    finally:
        # Clean up
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/notifications/<user_id>", methods=["GET"])
def get_notifications(user_id):
    conn = None
    cursor = None
    try:
        # Get notifications for the user
        query = f" SELECT * FROM notification WHERE receiver_id = {user_id}; "

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)
        cursor = conn.cursor()

        cursor.execute(query)
        # Fetch results
        results = cursor.fetchall()

        # Process results
        response = []
        for i in results:
            response.append({
                "notificationId": i[0],
                "timestamp": i[1],
                "receiverId": i[2],
                "submitterId": i[3],
                "type": i[4],
                "status": i[5],
                "employeeID": i[6],
                "message": i[7]
            })

        if not response:
            return make_response(jsonify('{error: subject not found}'), 404)

        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)
    finally:
        # Clean up
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/login", methods=["POST"])
def login():
    conn = None
    cursor = None
    try:
        # Get user credentials
        email = request.json["email"]
        password = request.json["password"]

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)
        cursor = conn.cursor()

        # Check if the user exists
        query = f"SELECT role FROM users WHERE email = '{email}' AND password = '{password}';"
        cursor.execute(query)
        result = cursor.fetchone()

        if result is None:
            return make_response(jsonify('{error: user not found}'), 404)
        else:
            response = {'role': result[0]}

        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)
    finally:
        # Clean up
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/register", methods=["POST"])
def register():
    conn = None
    cursor = None
    try:
        # Get user credentials
        email = request.json["email"]
        password = request.json["password"]
        name = request.json["name"]
        lastname = request.json["lastname"]
        role = request.json["role"]

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)
        cursor = conn.cursor()

        # Check if the user exists
        query = f"INSERT INTO users (email, password, name, lastname, role) VALUES ('{email}', '{password}', '{name}', '{lastname}', '{role}');"
        cursor.execute(query)

        # Commit the changes
        conn.commit()

        return make_response(jsonify('{success: user registered}'), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)
    finally:
        # Clean up
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == '__main__':
    app.run(debug=True)
