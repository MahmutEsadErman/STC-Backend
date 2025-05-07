import os
import datetime

import mysql.connector
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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


@app.route("/getUsers", methods=["GET"])
def get_users():
    conn = None
    cursor = None
    try:
        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)

        # Create a cursor to interact with the database
        cursor = conn.cursor()

        # Execute the query
        cursor.execute("""SELECT users.user_id, group_id, name, lastname, role
                        FROM users
                        LEFT JOIN (
                            SELECT * FROM employee
                        UNION
                        SELECT * FROM supervisor
                        ) AS combined ON users.user_id = combined.user_id
                        WHERE users.role != 'HR'
                        GROUP BY users.user_id
        """)

        # Fetch results
        results = cursor.fetchall()

        # Process results
        response = []
        for i in results:
            response.append({
                "userId": i[0],
                "name": i[2],
                "lastname": i[3],
                "role": i[4],
                "groupId": i[1]
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

@app.route("/saveTimetable", methods=["POST"])
def save_timetable():
    conn = None
    cursor = None
    try:
        timesheet = request.json["timesheet"]

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)

        # Create a cursor to interact with the database
        cursor = conn.cursor()

        for entry in timesheet:
            user_id = entry["userId"]
            work_date = entry["workDate"]
            comment = entry["comment"]
            status = "pending"
            absence = f"'{entry['absence']}'" if entry["absence"].strip() else "NULL"
            start_time = f"'{entry['startTime']}'" if entry["startTime"] else "NULL"
            end_time = f"'{entry['endTime']}'" if entry["endTime"] else "NULL"
            break_time = f"'{entry['breakTime']}'" if entry["breakTime"] else "NULL"
            hoursAsIs = f"'{entry['hoursAsIs']}'" if entry["hoursAsIs"] else "NULL"
            hours_target = f"'{entry['hoursTarget']}'" if entry["hoursTarget"] else "NULL"

            query = f"""UPDATE work_time_sheet SET
                begin = {start_time},
                end = {end_time},
                break_time = {break_time},
                hours_as_is = {hoursAsIs},
                hours_target = {hours_target},
                absence = {absence},
                comment = '{comment}',
                status = '{status}'
                WHERE user_id = {user_id} AND date = '{work_date}'; 
            """

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
        name = request.json["name"]
        begin_date = datetime.datetime.strptime(request.json["beginDate"], "%Y-%m-%d")
        end_date = datetime.datetime.strptime(request.json["endDate"], "%Y-%m-%d")
        new_status = "sent"

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)
        cursor = conn.cursor()

        # Get the supervisor's user_id
        query = f"SELECT user_id FROM supervisor WHERE group_id = (SELECT group_id FROM employee WHERE user_id = {user_id});"
        cursor.execute(query)
        supervisor_id = cursor.fetchall()[0][0]

        # Update the status of the work time sheet
        query = f"""
            UPDATE work_time_sheet
            SET status = '{new_status}'
            WHERE user_id = {user_id} AND status = 'pending' AND date BETWEEN '{begin_date}' AND '{end_date}';
        """

        cursor.execute(query)

        comment = f"{name} sent the timesheet for approval from {begin_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

        # Notification for the supervisor
        query = f"""INSERT INTO notification (timestamp, receiver_id, submitter_id, type, status, empl_id, message) 
        VALUES (current_date, {supervisor_id}, {user_id}, {NotificationTypes.SEND_TIMETABLE}, 0, {user_id}, '{comment}');
        """

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
                "workDate": i[1].strftime("%Y-%m-%d"),
                "startTime": str(i[2])[:-3] if i[2] else None,
                "endTime": str(i[3])[:-3] if i[3] else None,
                "breakTime": str(i[4])[:-3] if i[4] else None,
                "hoursTarget": str(i[5])[:-3] if i[5] else None,
                "hoursAsIs": str(i[6])[:-3] if i[6] else None,
                "absence": str(i[7]) if i[7] else "no",
                "comment": str(i[8]) if i[8] else "",
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

@app.route("/getVacationRequests/<user_id>", methods=["GET"])
def get_vacation_requests(user_id):
    conn = None
    cursor = None
    try:
        query = f" SELECT * FROM vacation_request WHERE sup_id = {user_id}; "

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
                "request_id": i[0],
                "emp_id": i[1],
                "start_date": i[2].strftime("%Y-%m-%d") if i[2] else None,
                "end_time": i[3].strftime("%Y-%m-%d") if i[3] else None,
                "status": i[4],
                "request_timestamp": str(i[5])[:-3] if i[5] else None,
                "reasons_for_rejection": i[6] if i[6] else "",
                "sup_id": i[7]
            })


        if not response:
            return make_response(jsonify('{error: vacation not found}'), 404)

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
        startDate = datetime.datetime.strptime(request.json["startDate"], "%Y-%m-%d")
        endDate = datetime.datetime.strptime(request.json["endDate"], "%Y-%m-%d")
        response = request.json["response"]  # "approved" or "denied"

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)
        cursor = conn.cursor()

        # Determine the new status based on the response
        new_status = "approved" if response else "denied"

        # Update the timetable status
        query = f"""
            UPDATE work_time_sheet
            SET status = '{new_status}'
            WHERE user_id = {user_id} AND date BETWEEN '{startDate}' AND '{endDate}';
        """
        cursor.execute(query)
        comment = f"Your timetable from {startDate.strftime('%Y-%m-%d')} to {endDate.strftime('%Y-%m-%d')} is $new_status!"
        # Add a notification for the employee
        query = f"""
            INSERT INTO notification (timestamp, receiver_id, submitter_id, type, status, empl_id, message)
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


@app.route("/send_sickness", methods=["POST"])
def send_sickness():
    conn = None
    cursor = None
    try:
        # Get userId
        user_id = request.json["userId"]
        name = request.json["name"]
        begin_date = datetime.datetime.strptime(request.json["beginDate"], "%Y-%m-%d")
        end_date = datetime.datetime.strptime(request.json["endDate"], "%Y-%m-%d")

        absence = "sickness"

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)
        cursor = conn.cursor()

        # Get the supervisor's user_id
        query = f"SELECT user_id FROM supervisor WHERE group_id = (SELECT group_id FROM employee WHERE user_id = {user_id});"
        cursor.execute(query)
        supervisor_id = cursor.fetchall()[0][0]

        notification_type = NotificationTypes.SICKNESS

        # Update the status of the work time sheet
        query = f"""
            UPDATE work_time_sheet
            SET absence = '{absence}'
            WHERE user_id = {user_id} AND date BETWEEN '{begin_date}' AND '{end_date}' AND DAYOFWEEK(date) NOT IN (1, 7);
        """

        cursor.execute(query)

        comment = f"{name} sent sickness notification from {begin_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

        # Notification for the supervisor
        query = f"""INSERT INTO notification (timestamp, receiver_id, submitter_id, type, status, empl_id, message) 
        VALUES (current_date, {supervisor_id}, {user_id}, {notification_type}, 0, {user_id}, '{comment}'),
        (current_date, (SELECT user_id FROM users WHERE role='HR' LIMIT 1), {user_id}, {notification_type}, 0, {user_id}, '{comment}');
        """

        cursor.execute(query)

        # Commit the changes
        conn.commit()

        return make_response(jsonify('{success: absence request sent to the supervisor and HR}'), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)
    finally:
        # Clean up
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/send_vacation", methods=["POST"])
def send_vacation():
    conn = None
    cursor = None
    try:
        # Get userId
        user_id = request.json["userId"]
        name = request.json["name"]
        begin_date = datetime.datetime.strptime(request.json["beginDate"], "%Y-%m-%d")
        end_date = datetime.datetime.strptime(request.json["endDate"], "%Y-%m-%d")

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)
        cursor = conn.cursor()

        # Get the supervisor's user_id
        query = f"SELECT user_id FROM supervisor WHERE group_id = (SELECT group_id FROM employee WHERE user_id = {user_id});"
        cursor.execute(query)
        supervisor_id = cursor.fetchall()[0][0]

        absence = "vacation"
        notification_type = NotificationTypes.VOCATION

        comment = f"{name} sent vacation request for approval from {begin_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

        # Notification for the supervisor
        query = f"""INSERT INTO notification (timestamp, receiver_id, submitter_id, type, status, empl_id, message) 
        VALUES (current_date, {supervisor_id}, {user_id}, {notification_type}, 0, {user_id}, '{comment}');
        """

        cursor.execute(query)

        query = f"""INSERT INTO vacation_request (emp_id,sup_id, start_date, end_time, status, request_timestamp) 
        VALUES ({user_id},{supervisor_id} ,'{begin_date}', '{end_date}', 0, current_date);
        """

        cursor.execute(query)

        # Commit the changes
        conn.commit()

        return make_response(jsonify('{success: vacation request sent to the supervisor}'), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)
    finally:
        # Clean up
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/respond_vacation", methods=["POST"])
def respond_vacation():
    conn = None
    cursor = None
    try:
        # Get data from the request
        user_id = request.json["userId"]
        begin_date = datetime.datetime.strptime(request.json["beginDate"], "%Y-%m-%d")
        end_date = datetime.datetime.strptime(request.json["endDate"], "%Y-%m-%d")
        
        employee_id = request.json["employeeId"]
        requestId = request.json["requestId"]
        response = request.json["response"]  # "approved" or "denied"
        commentResponse = request.json["comment"]

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)
        cursor = conn.cursor()

        # Determine the new status based on the response

        if response:
            comment = f"Your vacation request from {begin_date} to {end_date} is approved"
            absence = "vacation"
        else:
            comment = f"your vacation request from {begin_date} to {end_date} is denied"
            absence = "no"

        query = f"""
            UPDATE work_time_sheet
            SET absence = '{absence}'
            WHERE user_id = {employee_id} AND date BETWEEN '{begin_date}' AND '{end_date}' AND DAYOFWEEK(date) NOT IN (1, 7);
        """
        cursor.execute(query)

        # Add a notification for the employee
        query = f"""
            INSERT INTO notification (timestamp, receiver_id, submitter_id, type, status, empl_id, message)
            VALUES (current_date, {employee_id}, {user_id}, {NotificationTypes.VOCATION_APPROVAL if response else NotificationTypes.VOCATION_REJECTION}, 0, {employee_id}, '{comment}'),
            (current_date, (SELECT user_id FROM users WHERE role='HR' LIMIT 1), {user_id}, {NotificationTypes.VOCATION_APPROVAL if response else NotificationTypes.VOCATION_REJECTION}, 0, {employee_id}, '{comment}');
        """
        cursor.execute(query)

        query = f"""UPDATE vacation_request
        SET status = {1 if response else 2},reasons_for_rejection = '{commentResponse}'
        WHERE request_id = {requestId};
        """

        cursor.execute(query)

        # Commit the changes
        conn.commit()

        return make_response(jsonify('{success: vacation response recorded}'), 200)
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
                "timestamp": i[1].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
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


@app.route("/statistics", methods=["GET"])
def statistics():
    conn = None
    cursor = None
    try:
        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)
        cursor = conn.cursor()

        query = """SELECT date, AVG(TIMESTAMPDIFF(MINUTE, begin, end) - TIME_TO_SEC(break_time) / 60) AS avg_work_hours 
                    FROM work_time_sheet
                    WHERE status = 'approved'
                    GROUP BY date;
                 """

        cursor.execute(query)

        # Fetch results
        results = cursor.fetchall()
        # Process results
        response = []
        for i in results:
            response.append({
                "date": i[0].strftime("%Y-%m-%d"),
                "avgWorkHours": str(i[1])[:-3] if i[1] else None
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
        query = f"SELECT user_id, role, name, lastname FROM users WHERE email = '{email}' AND password = '{password}';"
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result is None:
            return make_response(jsonify('{error: user not found}'), 404)
            
        if result[1] == "employee":
            query = f"select group_id from employee where user_id = {result[0]};"
        elif result[1] == "supervisor":            
            query = f"select group_id from supervisor where user_id = {result[0]};"
        
        
        group_id = 0
        if result[1] != "HR":
            cursor.execute(query)
            group_id = cursor.fetchone()[0]
        
        response = {'userId': result[0],
                    'role': result[1],
                    'name': result[2],
                    'lastname': result[3],'groupId':group_id}

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
        group_id = request.json["groupId"]

        # Establish connection
        conn = mysql.connector.connect(host=host, user=userDb, password=passDb, database=db)
        cursor = conn.cursor()

        # Check if the user exists
        query = f"INSERT INTO users (email, password, name, lastname, role) VALUES ('{email}', '{password}', '{name}', '{lastname}', '{role}');"
        cursor.execute(query)

        # Commit the changes
        conn.commit()

        query = f"SELECT user_id FROM users WHERE email='{email}';"
        cursor.execute(query)
        user_id = cursor.fetchall()[0][0]

        if role == "employee":
            query = f"INSERT INTO employee (user_id, group_id) VALUES ({user_id}, {group_id});"
        elif role == "supervisor":
            query = f"INSERT INTO supervisor (user_id, group_id) VALUES ({user_id}, {group_id});"
        cursor.execute(query)
        conn.commit()

        absence = "no"
        status = "pending"
        query = "INSERT INTO work_time_sheet (user_id, date, absence,status) VALUES "
        for i in range(1, 31):
            date = datetime.date(2025, 5, i)
            dateStr = datetime.datetime.strptime(date, "%Y-%m-%d")
            query += f"({user_id}, '{dateStr}', '{absence}', '{status}'),"
         
        cursor.execute(query)
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
