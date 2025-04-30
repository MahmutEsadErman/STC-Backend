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
        return make_response(jsonify('{success: ok başarılı}'), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)
    finally:
        cursor.close()
        conn.close()


@app.route("/api/login", methods=["POST"])
def user_login():
    try:

        # todayDate, firstDayOfWeek, lastDayOfWeek = getCurrentDate()
        # dateString = firstDayOfWeek  # +".000"
        #
        #
        # ## TODO: change dateString to automated version as above
        # # dateString = "2020-05-04 00:00:00.000"
        # con = pymssql.connect(host,userDb,passDb,db)
        # cur = con.cursor()
        #
        # username = str(request.json["username"])
        # passwd = str(request.json["password"])
        #
        # cur.execute(
        #     f"select TOP 1  Ogrencisi_ID,Kisisi_ID from Kullanicilar where KullaniciAdi ='{username}' And Sifre= '{passwd}'")
        #
        # res = cur.fetchone()  # queryCalc(cur.description,cur.fetchone())
        #
        # if not res:
        #     return make_response(jsonify('{error:   User not found}'), 404)
        # else:
        #     studentId = res[0]
        #
        #     if studentId != None:
        #         res = {
        #             "userId": studentId
        #         }
        #
        #         cur.execute(f"Select Adi,Grubu FROM Ogrenciler WHERE ID ={studentId}")
        #         userData = cur.fetchone()
        #         res["admin"] = False
        #         res["username"] = userData[0]
        #         res["groupId"] = userData[1]
        #
        #         cur.execute(
        #             f"Select SayfaSayisi,HariciSayfaSayisi FROM EkopHedefleri WHERE Ogrencisi_ID ={studentId} AND Tarihi = '{dateString}'")
        #         ekopGoal = cur.fetchone()
        #         if ekopGoal:
        #             res["ekopPageGoal"] = ekopGoal[0]
        #             res["ekopPageOutGoal"] = ekopGoal[1]
        #         else:
        #             res["ekopPageGoal"] = 20
        #             res["ekopPageOutGoal"] = 250
        #
        #         cur.execute(
        #             f"Select SoruSayisi,Sure FROM ShHedefleri WHERE Ogrencisi_ID ={studentId} AND Tarihi = '{dateString}'")
        #         shGoal = cur.fetchone()
        #
        #         if shGoal:
        #             res["shQuestGoal"] = shGoal[0]
        #             res["shTimeGoal"] = shGoal[1]
        #         else:
        #             res["shQuestGoal"] = 60
        #             res["shTimeGoal"] = 60
        #
        #         cur.execute(
        #             f"Select Namaz,SayfaSayisi FROM ZHedefleri WHERE Ogrencisi_ID ={studentId} AND Tarihi = '{dateString}'")
        #         zGoal = cur.fetchone()
        #
        #         if zGoal:
        #             res["zPrayerGoal"] = zGoal[0]
        #             res["zQuranGoal"] = zGoal[1]
        #         else:
        #             res["zPrayerGoal"] = 10
        #             res["zQuranGoal"] = 4
        #     else:
        #         userId = res[1]
        #
        #         res = {
        #             "userId": userId
        #         }
        #
        #         cur.execute(f"select Adi,Grubu,isEkopAdmin from Kisiler left join Kullanicilar K on Kisiler.ID = K.Kisisi_ID where Kisisi_ID = {userId}")
        #         userData = cur.fetchone()
        #         res["admin"] = True
        #         res["username"] = userData[0]
        #         res["groupId"] = userData[1]
        #         res["isEkopAdmin"] = userData[2] == 1
        #
        # # res = [dict((cur.description[i][0], value)
        # #        for i, value in enumerate(row)) for row in cur.fetchall()]

        return make_response(jsonify('{success:.ok başarılı}'), 200)
    except Exception as e:
        return make_response(jsonify('{error:' + str(e) + '}'), 404)


if __name__ == '__main__':
    app.run(debug=True)
