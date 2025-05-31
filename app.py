import os
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import mysql.connector

#from flask_cors import CORS

app = Flask(__name__)
#CORS(app)

host = "MYSQL1002.site4now.net"
userDb = "ab83bf_stcadmi"
passDb = "Turkiye1461."
db = "db_ab83bf_stcadmi"
port = "3306"


class Notifications_type:
    addReviews = '1'  #
    removeReviews = '2'  #
    addProducts = '3'  #
    removeProducts = '4'  #
    addOntoFavList = '5'  #
    removeFromFavList = '6'  #
    purchaseProduct = '7'  # send notf to buyer
    cancelProduct = '8'  # send notf to seller
    sellProduct = '9'  # send notf to seller


@app.route('/')
def databaseDeneme():
    return "enesby!"


@app.route('/login', methods=["POST"])
def loginCheck():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return make_response(jsonify({'error': 'Email and password are required'}), 400)

        conn = mysql.connector.connect(
            host=host,
            user=userDb,
            password=passDb,
            database=db
        )

        cursor = conn.cursor()
        query = "SELECT first_name, last_name FROM users WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        result = cursor.fetchone()

        if not result:
            return make_response(jsonify({'error': 'Invalid credentials'}), 401)
        else:
            response = {
                'first_name': result[0],
                'last_name': result[1],
            }
            print("Login response:", response)  # ✅ Only after it's defined
            return make_response(jsonify(response), 200)

    except Exception as e:
        print("Login error:", str(e))  # ✅ Log the actual error
        return make_response(jsonify({'error': str(e)}), 404)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/register', methods=["POST"])
def register():
    conn = None
    cursor = None
    try:

        data = request.get_json()  # retriving data from request
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        password = data.get("password")
        conn = mysql.connector.connect(
            host=host,
            user=userDb,
            password=passDb,
            database=db
        )
        cursor = conn.cursor()
        query = f"INSERT INTO users(first_name,last_name,email,password) VALUES('{first_name}', '{last_name}', '{email}', '{password}') "
        cursor.execute(query)

        conn.commit()
        return make_response(jsonify('{success: user registered}'), 200)

    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/homepage',methods=["GET"]) # login basarili olduktan sonra ya da olmadan once rastegele categorilerin altinda product olusur
def homepage():
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host=host,
            user=userDb,
            password=passDb,
            database=db
        )
        #data = request.get_json()
        cursor = conn.cursor()
        # Kategori ID'lerini çek
        query = "SELECT id FROM categories"
        cursor.execute(query)
        category_ids = cursor.fetchall()
        response = []

        for cat in category_ids:
            category_id = cat[0]  # tuple içinden sayıyı al

            query = f"""
                SELECT * FROM products 
                WHERE category_id = {category_id} 
                ORDER BY RAND() 
                LIMIT 10
            """
            cursor.execute(query)
            result = cursor.fetchall()
            if result:
                for product in result:
                    response.append({
                        'id': product[0],
                        'name': product[1],
                        'price': product[2],
                        'category_id': product[3],
                        'seller_id': product[4],
                        'amount': product[5]
                    })

        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/categories/<category_id>',methods=["GET"]) # categori belirlendikten sonra o categori icerisindeki productlar gonderilir
def showTheProducts(category_id):
    cursor = None
    conn = None

    try:
        conn = mysql.connector.connect(
            host=host,
            user=userDb,
            password=passDb,
            database=db
        )
        cursor = conn.cursor()
        query = f"SELECT * FROM products where category_id = {category_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        response = []
        if result:
            for i in result:
                response.append(
                    {
                        'id': i[0],
                        'name': i[1],
                        'price': i[2],
                        'category_id': i[3],
                        'seller_id': i[4],
                        'amount': i[5]
                    }
                )
            return make_response(jsonify(response), 200)
        else:
            return make_response(jsonify('error : nothing could be found'), 404)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# Fetch products by user ID
@app.route('/products/<user_id>',methods=["GET"])
def getProductsByUser(user_id):
    cursor = None
    conn = None

    try:
        conn = mysql.connector.connect(
            host=host,
            user=userDb,
            password=passDb,
            database=db
        )
        cursor = conn.cursor()
        query = f"SELECT * FROM products where seller_id = {user_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        response = []
        if result:
            for i in result:
                response.append(
                    {
                        'id': i[0],
                        'name': i[1],
                        'price': i[2],
                        'category_id': i[3],
                        'seller_id': i[4],
                        'amount': i[5]
                    }
                )
            return make_response(jsonify(response), 200)
        else:
            return make_response(jsonify('error : nothing could be found'), 404)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/addProduct', methods=["POST"])
def addProducts():
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host=host,
            user=userDb,
            password=passDb,
            database=db
        )
        data = request.get_json()  # user_id,name,price,category_id,amount
        user_id = data.get("user_id")
        name = data.get("name")
        price = data.get("price")
        category_id = data.get("category_id")
        amount = data.get("amount")
        cursor = conn.cursor()
        query = f"INSERT INTO products(name,price,category_id,seller_id,amount) VALUES('{name}',{price},{category_id},{user_id},{amount})"
        cursor.execute(query)
        query = f"INSERT INTO notifications (user_id,type,message,created_at) VALUES ({user_id},'{3}',' {name}  is added',NOW())"
        cursor.execute(query)
        conn.commit()
        return make_response(jsonify(f'{{succes :  product is added}}', 200))
    except Exception as e:

        return make_response(jsonify({'error': str(e)}), 404)
    finally:
        cursor.close()
        conn.close()


@app.route('/removeProduct/<product_id>', methods=["POST"])
def removeProducts(product_id):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host=host,
            user=userDb,
            password=passDb,
            database=db
        )
        cursor = conn.cursor()
        data = request.get_json()
        user_id = data.get("user_id")
        query = f"SELECT name FROM products where  id = {product_id}"
        cursor.execute(query)
        result = cursor.fetchall()
        if not result:
            return make_response(jsonify(f'{{error :  product couldnt be removed}}'), 404)
        name = result[0][0]
        query = f"DELETE FROM products where  id = {product_id}"
        cursor.execute(query)
        query = f"INSERT INTO notifications (user_id,type,message,created_at) VALUES ({user_id},'{4}',' The product {name}  is removed',NOW())"
        cursor.execute(query)
        conn.commit()
        return make_response(jsonify(f'{{succes :  product is removed}}'), 200)
    except Exception as e:

        return make_response(jsonify({'error': str(e)}), 404)
    finally:
        cursor.close()
        conn.close()

@app.route('/reviews/<product_id>',methods=["GET"]) # producta tiklantiktan sonra reviewslarini gosterir
def reviews(product_id):
    cursor = None
    conn = None
    try:
        conn = mysql.connector.connect(host=host,
                                       user=userDb,
                                       password=passDb,
                                       database=db)
        cursor = conn.cursor()
        query = f"SELECT * FROM reviews where product_id=  {product_id}"
        cursor.execute(query)
        result = cursor.fetchall()
        if result:
            response = []
            for i in result:
                response.append(
                    {
                        'id': i[0],
                        'product_id': i[1],
                        'user_id': i[2],
                        'rating': i[3],
                        'comment': i[4],
                        'review_date': i[5]

                    }
                )
            return make_response(jsonify(response), 200)
        else:
            return make_response(jsonify({'error': str(e)}), 404)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/reviews/<product_id>/add', methods=["POST"])  #review ekle
def addReviews(product_id):
    cursor = None
    conn = None
    try:
        conn = mysql.connector.connect(host=host,
                                       user=userDb,
                                       password=passDb,
                                       database=db)
        cursor = conn.cursor()

        data = request.get_json()
        user_id = data.get("user_id")
        rating = data.get("rating")
        comment = data.get("comment")
        query = f"INSERT INTO reviews(product_id,user_id,rating,comment,review_date) VALUES({product_id},{user_id},{rating},'{comment}',NOW())"
        cursor.execute(query)

        message = "review is added"
        query = f"INSERT INTO notifications (user_id,type,message,created_at) VALUES ({user_id},'{1}','{message}',NOW())"
        cursor.execute(query)

        conn.commit()
        return make_response(jsonify('{success : your review is added}', 200))
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)
    finally:
        conn.close()
        cursor.close()


@app.route('/reviews/<id>/remove', methods=["POST"])  #review sil
def removeReviews(id):
    cursor = None
    conn = None
    try:
        conn = mysql.connector.connect(host=host,
                                       user=userDb,
                                       password=passDb,
                                       database=db)
        cursor = conn.cursor()
        query = f"SELECT * FROM reviews where id = {id}"
        cursor.execute(query)
        result = cursor.fetchall()
        if not result:
            return make_response(jsonify('{error : your review couldnt be found}', 404))
        query = f"DELETE FROM reviews where id = {id}"
        cursor.execute(query)
        message = "review is removed"
        query = f"INSERT INTO notifications (user_id,type,message,created_at) VALUES ({result[0][2]},'{2}','{message}',NOW())"
        cursor.execute(query)

        conn.commit()

        return make_response(jsonify('{success : your review is removed}', 200))
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)
    finally:
        conn.close()
        cursor.close()
@app.route('/favorites/<user_id>',methods=["GET"])
def favorites(user_id):#user_id
    conn = None
    cursor = None
    try :
        conn = mysql.connector.connect(host=host,
            user=userDb,
            password=passDb,
            database=db)
        cursor = conn.cursor()
       # data = request.get_json()
        #user_id = data.get('user_id')
        query = f"SELECT * from favorites where user_id = {user_id}"
        cursor.execute(query)

        result = cursor.fetchall()
        if not result:
            return make_response(jsonify('{error: favorites is empty}'),404)
        response = []
        for i in result:
            response.append({
                'user_id': i[0],
                'product_id':i[1]
            })

        return make_response(jsonify(response),200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}),404)
    finally:
        conn.close()
        cursor.close()

@app.route('/favorites/add',methods=["POST"])
def addFavorites():#product_id,user_id
    cursor = None
    conn = None


    try:
        conn = mysql.connector.connect(host=host,
            user=userDb,
            password=passDb,
            database=db)
        cursor = conn.cursor()
        data  = request.get_json()
        product_id = data.get("product_id")
        user_id = data.get("user_id")
        query = f"INSERT INTO favorites VALUES({user_id},{product_id})"
        cursor.execute(query)
        query = f"insert into notifications (user_id,type,message,created_at) values({user_id},'5','product is added on favlist',NOW())"
        cursor.execute(query)
        conn.commit()


        return make_response(jsonify({'success ': ' product added into your favorites'}),200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}),404)
    finally:
        conn.close()
        cursor.close()


@app.route('/favorites/remove', methods=["POST"])
def removeFavorites():  #user_id,product_id
    cursor = None
    conn = None
    try:
        conn = mysql.connector.connect(host=host,
                                       user=userDb,
                                       password=passDb,
                                       database=db)
        cursor = conn.cursor()
        data = request.get_json()
        product_id = data.get("product_id")
        user_id = data.get("user_id")
        query = f"SELECT * from favorites where product_id ={product_id}"
        cursor.execute(query)
        result = cursor.fetchall()
        if not result:
            return make_response(jsonify('{error : there is no such a entry}'))
        query = f"DELETE FROM favorites where product_id ={product_id}"
        cursor.execute(query)
        query = f"insert into notifications (user_id,type,message,created_at) values({user_id},'6','product is removed from favlist',NOW())"
        cursor.execute(query)
        conn.commit()

        return make_response(jsonify({'success': 'selected product has been removed from the favorites list'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)
    finally:
        conn.close()
        cursor.close()


@app.route('/notification/<user_id>', methods=["GET"])
def notifications(user_id):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(host=host,
                                       user=userDb,
                                       password=passDb,
                                       database=db)
        cursor = conn.cursor()

        query = f"SELECT * FROM notifications where user_id = {user_id}"
        cursor.execute(query)
        result = cursor.fetchall()
        if not result:
            make_response(jsonify('{error : there is no any notifications sent to this user}'), 404)
        response = []
        for i in result:
            response.append(
                {
                    "id": i[0],
                    "user_id": i[1],
                    "type": i[2],
                    "message": i[3],
                    "is_read": i[4],
                    "created_at": i[5]
                }
            )
        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify({'error ': str(e)}), 404)
    finally:
        conn.close
        cursor.close

@app.route('/notificationIsRead/<notification_id>',methods=["POST"])
def notificationIsRead(notification_id):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(host=host,
            user=userDb,
            password=passDb,
            database=db)
        cursor = conn.cursor()
        query= f"select id   from notifications where id = {notification_id}"
        cursor.execute(query)
        result = cursor.fetchall()
        if not result:
            return make_response(jsonify('{error : there is no such a entry in notifications}'),404)
        query = f" UPDATE notifications SET is_read = 1 where id = {notification_id} "
        cursor.execute(query)
        conn.commit()

        return make_response(jsonify("success : notification is read"),200)
    except Exception as e:
        return make_response(jsonify({'error' : str(e)}),404)
    finally:
        conn.close
        cursor.close

@app.route('/orders/<user_id>',methods = ["GET"])
def orders(user_id):#user_id
    conn= None
    cursor = None
    try :
        conn = mysql.connector.connect(
            host=host,
            user=userDb,
            password=passDb,
            database=db)
        cursor = conn.cursor()
        #data  = request.get_json()
        #user_id = data.get("user_id")
        query = f"select * from orders where customer_id = {user_id}"
        cursor.execute(query)
        result = cursor.fetchall()
        if not result:
            return make_response(jsonify({'error : couldnt be found any entry'} ),404)
        response = []
        for i in result:
            response.append({
                'id': i[0],
                'customer_id': i[1],
                'product_id': i[2],
                'amount': i[3],
                'order_date': i[4],
                'status': i[5],
                'address': i[6]
            })
            return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)} ),404)
    finally:
        conn.close
        cursor.close


@app.route('/purchase', methods=["POST"])
def purchase():  #order_id
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host=host,
            user=userDb,
            password=passDb,
            database=db)
        cursor = conn.cursor()
        data = request.get_json()
        order_id = data.get("order_id")
        query = f"select amount,status,product_id,customer_id from orders where id = {order_id} "
        cursor.execute(query)
        result = cursor.fetchall()
        if not result:
            return make_response(jsonify("{error : there is no such a order}"))
        print(result)
        amount = result[0][0]
        status = result[0][1]
        product_id = result[0][2]
        user_id = result[0][3]
        if (status != "pending"):
            return make_response(jsonify("error : there is noany pending orders"), 404)
        query = f"select amount from products where id = {product_id}"
        cursor.execute(query)
        result = cursor.fetchall()
        available_quantity = result[0][0]
        if (available_quantity == 0 or (available_quantity - amount) < 0):
            return make_response(jsonify("{error : there is not enough product}"))
        query = f"update products  set amount = {available_quantity - amount} where id = {product_id}"
        cursor.execute(query)
        print("buraada")
        query = f"INSERT into notifications (user_id,type,message,created_at) VALUES({user_id},'7','purchasing is done without having any issues',NOW())"  #for buyer
        cursor.execute(query)
        query = f"UPDATE orders set status  = 'processing' where id = {order_id}"
        cursor.execute(query)
        query = f"insert into notifications(user_id,type,message,created_at) values((select seller_id from products where id = {product_id}),'9','your product has been bought amount of {amount} ',NOW())"  #for seller
        cursor.execute(query)
        conn.commit()
        return make_response(jsonify('{succes : purchasing is done} '), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)
    finally:
        conn.close
        cursor.close


@app.route('/addToOrders', methods=["POST"])
def addToOrders():  #user_id,amount,product_id,address
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host=host,
            user=userDb,
            password=passDb,
            database=db)
        cursor = conn.cursor()
        data = request.get_json()
        user_id = data.get("user_id")
        product_id = data.get("product_id")
        amount = data.get("amount")
        address = data.get("address")
        query = f"select status,address,amount from orders where customer_id = {user_id} and product_id={product_id}"
        cursor.execute(query)
        result = cursor.fetchall()
        status = result[0][0]
        if (status == 'pending' and address == result[0][1]):
            query = f" update orders set amount= {amount + result[0][2]} where customer_id = {user_id} and product_id={product_id} "
            cursor.execute(query)
            conn.commit()
            return make_response(jsonify("success  : orders exists but still added "), 200)

        query = f"INSERT INTO orders(customer_id,product_id,amount,order_date,address) VALUES({user_id},{product_id},{amount},NOW(),'{address}')"
        cursor.execute(query)
        conn.commit()
        return make_response(jsonify("success  : orders is added "), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)
    finally:
        conn.close
        cursor.close


@app.route('/cancelOrder', methods=["POST"])
def cancelOrder():  #order_id
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host=host,
            user=userDb,
            password=passDb,
            database=db)
        cursor = conn.cursor()
        data = request.get_json()
        order_id = data.get("order_id")
        query = f"select * from orders where id = {order_id} "
        cursor.execute(query)
        result = cursor.fetchall()
        status = result[0][5]
        if (status == 'delivered'):
            return make_response(jsonify('{error : order had already been delivered}'), 404)
        query = f"update orders set status = 'cancelled' where id = {order_id}"
        cursor.execute(query)

        query = f"insert into notifications (user_id,type,message,created_at) VALUES((select seller_id from products where id = {result[0][2]}),'8','the order is cancelled',NOW())"
        cursor.execute(query)
        conn.commit()

        return make_response(jsonify('{succes : order is cancelled}'), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)
    finally:
        conn.close
        cursor.close


if __name__ == "__main__":
    app.run(debug=True)
