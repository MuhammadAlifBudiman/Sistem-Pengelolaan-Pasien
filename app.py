import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, session, redirect, url_for, request
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import bcrypt  # Import the bcrypt library
from werkzeug.utils import secure_filename

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")

app = Flask(__name__)

MONGODB_CONNECTION_STRING = 'mongodb+srv://test:sparta@cluster0.xwzbkyt.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.dbsparta_plus_week4

TOKEN_KEY = 'mytoken'
SECRET_KEY = 'SPARTA'

@app.route('/', methods=['GET'])
def home():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload['id']})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for('login', msg="Your login token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('login', msg="There was an error logging you in"))

@app.route('/login', methods=['GET'])
def login():
    msg = request.args.get('msg')
    return render_template('login.html', msg=msg)

@app.route('/user/<username>', methods=['GET'])
def user(username):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = username == payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

@app.route("/sign_in", methods=["POST"])
def sign_in():
    # Sign in
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]
    
    # Use bcrypt for password hashing
    hashed_password = bcrypt.hashpw(password_receive.encode("utf-8"), bcrypt.gensalt())
    
    result = db.users.find_one(
        {
            "username": username_receive,
            "password": hashed_password,
        }
    )
    
    if result:
        payload = {
            "id": username_receive,
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
