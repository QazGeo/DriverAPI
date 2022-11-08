from flask import *
from functions import *
import pymysql
import pymysql.cursors
import datetime

connection = pymysql.connect(host = 'localhost', user = 'root', password = '', database = '4RLS')

app = Flask(__name__)

@app.route('/login', methods = ['POST'])

# def login(email, password):
def login():
    try:

        json = request.json
        email = json['email']
        password = json['password']
        sql = "select * from drivers where email = %s"
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, email)
        if cursor.rowcount == 0:
            response = jsonify({'msg' : 'Invalid email!'})
            response.status_code = 400
            return response
        else:
            row = cursor.fetchone()
            # hash_pswd = row['password']
            hash_pswd = row['password']  # hashed password from database
            status = password_verify(password, hash_pswd)  # verifying hashed password is same with database
            if status:
                response = jsonify({'msg': 'Login successful!', 'data': row})
                response.status_code = 200
                return response
            else:
                response = jsonify({'msg': 'Login failed!'})
                response.status_code = 401
                return response

    except:
        response = jsonify({'msg':'Something went wrong...'})
        response.status_code = 500
        return response


@app.route('/changepassword', methods = ['POST'])
def changepassword():
    json = request.json
    driver_id = json['driver_id']
    current_pswd = json['current_pswd']
    new_pswd = json['new_pswd']
    con_pswd = json['con_pswd']

    sql = 'select * from admin where user_id = %s'
    cursor = connection.cursor()
    cursor.execute(sql, (driver_id))
    row = cursor.fetchone()
    hashed_pswd = row[7]
    status = password_verify(current_pswd, hashed_pswd)
    if status:
        print("Current okay")
        response = password_check(new_pswd)
        if response == True:
            print("New okay")
            if new_pswd != con_pswd:
                response = jsonify({'msg': 'Passwords do not match!'})
                response.status_code = 400
                return response
            else:
                print("Confirm okay")
                sql = 'update admin set password = %s where user_id = %s'
                cursor = connection.cursor()
                try:
                    cursor.execute(sql, (password_hash(new_pswd), driver_id))
                    connection.commit()
                    response = jsonify({'msg': 'Password changed', 'data': row})
                    response.status_code = 200
                    return response
                except:
                    connection.rollback()
                    response = jsonify({'msg': 'An error occurred, please try again'})
                    response.status_code = 500
                    return response
        else:
            response = jsonify({'msg': response})
            response.status_code = 400
            return response
    else:
        response = jsonify({'msg':'Wrong password'})
        response.status_code = 400
        return response

app.run(debug=True)


