from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import hashlib
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

MONGODB_CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING")
DB_NAME = os.environ.get("DB_NAME")
SECRET_KEY = os.environ.get("SECRET_KEY")
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client[DB_NAME]


@app.route("/")
def index():
    return render_template("index.html")


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


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
