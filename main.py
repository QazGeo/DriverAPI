from flask import *
from functions import *
import pymysql
import pymysql.cursors
import jwt
import datetime
from datetime import *
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = "guighuI789UJhio156"
# app.secret_key = "QWSERRdsr4948948*/*/8776tdhd"


connection = pymysql.connect(host = 'localhost', user = 'root', password = '', database = '4RLS')


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
                token = jwt.encode(
                    {
                        'public_id': row['driver_id'],
                        'exp': datetime.utcnow() + timedelta(minutes=1)
                    }
                    ,
                    app.config['SECRET_KEY'], algorithm="HS256"
                )
                response = jsonify({'msg': 'Login successful!', 'data': row, 'token': token})
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

def token_required(f):

    # decorators allow u to add more functionality to an existing functions

    @wraps(f)
    def decorated(*args, **kwargs):
         token = None
         if "Authorization" in request.headers:
             token = request.headers["Authorization"].split(" ")[1] # bearer, token
         if not token:
             return {
             "message": "Authentication Token is missing!",
             "data": None,
             "error": "Unauthorized"
             }, 401
         try:
             data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
         except Exception as e:
             return {
                 "message": "Something went wrong",
                 "data": None,
                 "error": str(e)
                 }, 500
         return f(*args, **kwargs) #f should be true if token is right else false
    return decorated

@app.route('/changepassword', methods = ['POST'])
@token_required
def changepassword():
    json = request.json
    driver_id = json['driver_id']
    current_pswd = json['current_pswd']
    new_pswd = json['new_pswd']
    con_pswd = json['con_pswd']

    sql = 'select * from drivers where driver_id = %s'
    cursor = connection.cursor()
    cursor.execute(sql, (driver_id))
    row = cursor.fetchone()
    hashed_pswd = row[12]
    status = password_verify(current_pswd, hashed_pswd)
    if status:
        print("Current okay")
        response = password_check(new_pswd)
        if response == True:
            print("New okay")
            if new_pswd != con_pswd:
                response = jsonify({'msg': 'Passwords do not match!'})
                response.status_code = 401
                return response
            else:
                print("Confirm okay")
                sql = 'update drivers set password = %s where driver_id = %s'
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
            response.status_code = 401
            return response
    else:
        response = jsonify({'msg':'Wrong password'})
        response.status_code = 401
        return response


@app.route('/allocatedvehicle', methods = ['POST'])
@token_required
def allocatedvehicle():
    try:
        json = request.json
        driver_id = json['driver_id']
        sql = "select * from driver_allocations where driver_id = %s and alloc_status = %s"
        cursor = connection.cursor()
        cursor.execute(sql, (driver_id, "active"))
        row = cursor.fetchone()

        # pulling vehicle reg

        reg_no = row[2]

    #     more queries, finding car details

        sql3 = "select * from vehicles where reg_no = %s"
        cursor3 = connection.cursor(pymysql.cursors.DictCursor)
        cursor3.execute(sql3, (reg_no))

        if cursor3.rowcount == 0:
            response = jsonify({'msg': 'Vehicle not found!'})
            response.status_code = 404
            return response
        else:
            vehicle = cursor3.fetchone()
            makes = getmakes()
            response = jsonify({'msg': 'Success', 'data': vehicle, 'makes': makes})
            response.status_code = 200
            return response

    except:
        response = jsonify({'msg': 'Driver is not allocated or doesnt exist!'})
        response.status_code = 500
        return response
        # return render_template("views/viewvehicles.html",  vehicles = vehicles, makes = getmakes(), types = gettypes(), models = modellist())

# getting assignments via driver_id

@app.route('/myassign/<driver_id>', methods = ['GET'])
@token_required
def myassign(driver_id):
    sql = "select * from vehicle_task_allocation where driver_id = %s ORDER BY reg_no DESC"
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql, (driver_id))

    if cursor.rowcount == 0:
        response = jsonify({'msg': 'No assigned tasks!'})
        response.status_code = 400
        return response
    else:
        assign = cursor.fetchall()
        print(assign)
        response = jsonify({'msg': 'All tasks', 'data': assign})
        response.status_code = 200
        return response

@app.route('/tripongoing', methods = ['PUT'])
@token_required
def tripongoing():
    json = request.json
    task_id = json['task_id']
    sql = "select * from vehicle_task_allocation where task_id = %s"
    cursor = connection.cursor()
    cursor.execute(sql, (task_id))

    if cursor.rowcount == 0:
        response = jsonify({'msg': 'No such task!'})
        response.status_code = 404
        return response
    else:
        row = cursor.fetchone()
        print(row[6])
        status = row[6]
        if status == 'Pending':
            sqlupdate = "update vehicle_task_allocation set trip_completion_status = %s where task_id = %s"
            cursor = connection.cursor()
            try:
                cursor.execute(sqlupdate, ('Ongoing', task_id))
                connection.commit()
                response = jsonify({'msg':'Trip started.'})
                response.status_code = 200
                return response
            except:
                connection.rollback()
                response = jsonify({'msg':'Server error! Try again later.'})
                response.status_code = 500
                return response
        else:
            response = jsonify({'msg': 'Task is already {}'.format(status)})
            response.status_code = 417
            return response

@app.route('/tripcomplete', methods = ['PUT'])
@token_required
def tripcomplete():
    json = request.json
    task_id = json['task_id']
    sql = "select * from vehicle_task_allocation where task_id = %s"
    cursor = connection.cursor()
    cursor.execute(sql, (task_id))

    if cursor.rowcount == 0:
        response = jsonify({'msg': 'No such task!'})
        response.status_code = 404
        return response
    else:
        row = cursor.fetchone()
        print(row[6])
        status = row[6]
        if status == 'Ongoing':
            sqlupdate = "update vehicle_task_allocation set trip_completion_status = %s where task_id = %s"
            cursor = connection.cursor()
            try:
                cursor.execute(sqlupdate, ('Completed', task_id))
                connection.commit()
                response = jsonify({'msg':'Trip completed.'})
                response.status_code = 200
                return response
            except:
                connection.rollback()
                response = jsonify({'msg':'Server error! Try again later.'})
                response.status_code = 500
                return response
        else:
            response = jsonify({'msg': 'Task is already {}'.format(status)})
            response.status_code = 417
            return response

@app.route('/tripdelete', methods = ['DELETE'])
@token_required
def tripdelete():
    json = request.json
    task_id = json['task_id']
    sql = "select * from vehicle_task_allocation where task_id = %s"
    cursor = connection.cursor()
    cursor.execute(sql, (task_id))

    if cursor.rowcount == 0:
        response = jsonify({'msg': 'No such task!'})
        response.status_code = 404
        return response
    else:
        sql = "delete from vehicle_task_allocation where task_id = %s"
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (task_id))
            connection.commit()
            response = jsonify({'msg': 'Trip deleted.'})
            response.status_code = 200
            return response
        except:
            connection.rollback()
            response = jsonify({'msg': 'Server error! Try again later.'})
            response.status_code = 500
            return response

def getmakes():
    sql = "select * from vehicle_make order by make_name asc"
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    makes = cursor.fetchall()
    return makes




app.run(debug=True)


