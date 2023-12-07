from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import hashlib
import os
from os.path import join, dirname
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from bson import ObjectId


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")

app = Flask(__name__)

MONGODB_CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING")
DB_NAME = os.environ.get("DB_NAME")
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client[DB_NAME]

TOKEN_KEY = 'mytoken'
SECRET_KEY = 'SPARTA'


@app.route('/' , methods=['GET', 'POST'])
def home():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload['id']})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return render_template('index.html', msg="Your login token has expired")
    except jwt.exceptions.DecodeError:
        return render_template('index.html', msg="There was an error logging you in")
    
@app.route('/api/get_jadwal', methods=['GET'])
def get_jadwal():
    try:
        # Mengambil data jadwal
        jadwal_data = list(db.jadwal_praktek.find({}, {'_id': False}))
        return jsonify({"jadwal": jadwal_data})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/get_antrian', methods=['GET'])
def get_antrian():
    try:
        # Mengambil data antrian
        antrian_data = list(db.antrian.find({}, {'_id': False}))
        return jsonify({"antrian": antrian_data})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/login', methods=['GET'])
def login():
    msg = request.args.get('msg')
    return render_template('login.html', msg=msg)


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/api/register", methods=["POST"])
def api_register():
    username = request.form['username']
    name = request.form['name']
    nik = request.form['nik']
    tgl_lahir = request.form['tgl-lahir']
    gender = request.form['gender']
    agama = request.form['agama']
    status = request.form['status']
    alamat = request.form['alamat']
    no_telp = request.form['no-telp']
    password = request.form['password']

    # Hash password sebelum disimpan
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    # Simpan data pengguna ke MongoDB
    user_data = {
        'username': username,
        'name': name,
        'nik': nik,
        'tgl_lahir': tgl_lahir,
        'gender': gender,
        'agama': agama,
        'status': status,
        'alamat': alamat,
        'no_telp': no_telp,
        'password': hashed_password,
        'role': 'pasien'
    }

    db.users.insert_one(user_data)
    return redirect(url_for('login'))


@app.route("/api/check-username", methods=["POST"])
def check_username():
    username_receive = request.form['username']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


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
    print('signin')
    # Sign in
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]

    # Use bcrypt for password hashing
    hashed_password = hashlib.sha256(
        password_receive.encode('utf-8')).hexdigest()

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
    
@app.route('/pendaftaran_formulir', methods=['GET', 'POST'])
def pendaftaran_formulir():
    if request.method == 'POST':
        poli = request.form['poli']
        tanggal = request.form['tanggal']
        keluhan = request.form['keluhan']

        # Masukkan data ke MongoDB
        data_pendaftaran = {
            'poli': poli,
            'tanggal': tanggal,
            'keluhan': keluhan
        }
        db.registrations.insert_one(data_pendaftaran)

        pendaftaran_data = list(db.registrations.find())

        return render_template('pendaftaran_formulir.html', data=pendaftaran_data)
    
    return render_template('pendaftaran_formulir.html') 

@app.route('/api/pendaftaran', methods=['GET'])
def riwayat_pendaftaran():
    pendaftaran_data = list(db.registrations.find({}, {'_id': 0}))  
    return jsonify(pendaftaran_data)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
