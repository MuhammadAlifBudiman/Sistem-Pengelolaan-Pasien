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

app = Flask(__name__)

MONGODB_CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING")
DB_NAME = os.environ.get("DB_NAME")
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client[DB_NAME]

TOKEN_KEY = 'mytoken'
SECRET_KEY = 'SPARTA'


@app.route('/', methods=['GET', 'POST'])
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
        'profile_pic': 'profile_pics/profile_placeholder.png',
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
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        if request.method == 'POST':
            if 'submit' in request.form:
                poli = request.form['poli']
                tanggal = request.form['tanggal']
                keluhan = request.form['keluhan']
                

                # Ambil data pengguna dari koleksi users
                user_data = db.users.find_one({'username': username})

                if user_data:
                    # Masukkan data pendaftaran ke MongoDB
                    data_pendaftaran = {
                        'username': user_data['username'],
                        'name': user_data['name'],
                        'nik': user_data['nik'],
                        'tgl_lahir': user_data['tgl_lahir'],
                        'gender': user_data['gender'],
                        'agama': user_data['agama'],
                        'status_pernikahan': user_data['status'],
                        'alamat': user_data['alamat'],
                        'no_telp': user_data['no_telp'],
                        'poli': poli,
                        'tanggal': tanggal,
                        'keluhan': keluhan,
                        'status': 'pending'
                    }
                    print(data_pendaftaran)

                    db.registrations.insert_one(data_pendaftaran)
                    # Ambil data antrian dari MongoDB
                    antrian_data = list(db.registrations.find(
                        {"status": {"$in": ["pending", "approve"]}},
                        {"no_urut": True, 
                        "name": True, 
                        "nik": True, 
                        "tanggal": True, 
                        "status": True, 
                        "_id": False}
                    ))
                    return render_template('pendaftaran_formulir.html', data=antrian_data)

            has_pending_or_approved = db.registrations.count_documents({
            "status": {"$in": ["pending", "approve"]}
        }) > 0
            
            
            print(has_pending_or_approved)

            return render_template('pendaftaran_formulir.html', has_pending_or_approved=has_pending_or_approved)
            return render_template('error.html', message='Data pengguna tidak ditemukan')
        return render_template('pendaftaran_formulir.html')
        return render_template('pendaftaran_formulir.html', data=pendaftaran_data)

        return render_template('pendaftaran_formulir.html')
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


@app.route("/pendaftaran_pegawai")
def pendaftaran_pegawai():
    return render_template("pendaftaran_pegawai.html")

@app.route('/api/pendaftaran_pegawai', methods=['GET'])
def api_pendaftaran_pegawai():
    pendaftaran_data = list(db.registrations.find({}, {'_id': 0}))  
    return jsonify(pendaftaran_data)

@app.route('/api/update-pendaftaran-pegawai', methods=['POST'])
def update_pendaftaran_pegawai():
    try:
        registration_id = request.form['registration_id']
        status = request.form['status']

        # Validasi ID Pendaftaran
        if not ObjectId.is_valid(registration_id):
            return jsonify({'result': 'failed', 'message': 'ID Pendaftaran tidak valid'})

        # Validasi Status
        valid_statuses = ['approve', 'reject', 'done']
        if status not in valid_statuses:
            return jsonify({'result': 'failed', 'message': 'Status tidak valid'})

        # Update status pendaftaran di MongoDB
        result = db.registrations.update_one(
            {'_id': ObjectId(registration_id)},
            {'$set': {'status': status}}
        )

        if result.modified_count > 0:
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'failed', 'message': 'ID Pendaftaran tidak ditemukan'})
    except Exception as e:
        return jsonify({'result': 'failed', 'message': str(e)})

@app.route('/api/pendaftaran-pegawai-as-done', methods=['POST'])
def pendaftaran_pegawai_as_done():
    try:
        registration_id = request.form['registration_id']

        # Validasi ID Pendaftaran
        if not ObjectId.is_valid(registration_id):
            return jsonify({'result': 'failed', 'message': 'ID Pendaftaran tidak valid'})

        # Tandai pendaftaran sebagai selesai di MongoDB
        result = db.registrations.update_one(
            {'_id': ObjectId(registration_id)},
            {'$set': {'status': 'done'}}
        )

        if result.modified_count > 0:
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'failed', 'message': 'ID Pendaftaran tidak ditemukan'})
    except Exception as e:
        return jsonify({'result': 'failed', 'message': str(e)})

@app.route("/riwayat_pendaftaran")
def riwayat_pendaftaran():
    return render_template("riwayat_pendaftaran.html")


@app.route('/api/pendaftaran_formulir', methods=['GET'])
def api_riwayat_pendaftaran():
    pendaftaran_data = list(db.registrations.find({}, {'_id': 0}))
@app.route('/api/riwayat_pendaftaran', methods=['GET'])
def riwayat_pendaftaran_api():
    pendaftaran_data = list(db.registrations.find({}, {'_id': 0}))  
    return jsonify(pendaftaran_data)


@app.route("/profile")
def profile():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload['id']}, {
                                      '_id': False, 'password': False})
        return render_template('profile.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        print("Expired Signature Error")
        return jsonify({'result': 'fail', 'msg': 'Your login token has expired'})
    except jwt.exceptions.DecodeError:
        print("Decode Error")
        return jsonify({'result': 'fail', 'msg': 'There was an error decoding your token'})


@app.route('/profile/edit', methods=['POST'])
def edit_profile():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload['id']

        # Fetch user data from the request
        user_info = db.users.find_one({"username": payload["id"]})
        file_path = user_info["profile_pic"]
        name = request.form.get('name')
        nik = request.form.get('nik')
        tgl_lahir = request.form.get('tgl_lahir')
        gender = request.form.get('gender')
        agama = request.form.get('agama')
        status = request.form.get('status')
        alamat = request.form.get('alamat')
        no_telp = request.form.get('no_tlp')

        # Update user data in the database
        doc = {
            'name': name,
            'nik': nik,
            'tgl_lahir': tgl_lahir,
            'gender': gender,
            'agama': agama,
            'status': status,
            'alamat': alamat,
            'no_telp': no_telp,
        }

        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file.filename != '':
                filename = secure_filename(file.filename)
                extension = filename.split(".")[-1]
                file_path = f"profile_pics/{username}.{extension}"
                file.save("./static/" + file_path)
                doc["profile_pic"] = file_path

        db.users.update_one({"username": username}, {"$set": doc})

        return jsonify({'result': 'success', 'msg': 'Profile updated successfully'})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': 'Your login token has expired'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': 'There was an error decoding your token'})


@app.route('/kelola-praktik')
def kelola_praktik():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})
        jadwal = list(db.jadwal.find())
        jadwal[0]["_id"] = str(jadwal[0]["_id"])
        if user_info['role'] != 'pegawai':
            return redirect(url_for('home'))
        return render_template('praktik.html', jadwal=jadwal)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


@app.route("/api/tambah-jadwal", methods=["POST"])
def api_tambah_jadwal():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})
        if user_info['role'] != 'pegawai':
            return redirect(url_for('home'))
        nama = request.form.get("nama")
        poli = request.form.get("poli")
        hari = request.form.getlist("hari")
        jam_buka = request.form.get("jam_buka")
        jam_tutup = request.form.get("jam_tutup")
        jadwal_data = {
            "nama": nama,
            "poli": poli,
            "hari": hari,
            "jam_buka": jam_buka,
            "jam_tutup": jam_tutup,
        }

        result = db.jadwal.insert_one(jadwal_data)
        jadwal_data["_id"] = str(result.inserted_id)

        return jsonify(jadwal_data)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


@app.route("/api/get-jadwal/<id>", methods=["GET"])
def get_jadwal_by_id(id):
    jadwal = db.jadwal.find_one({"_id": ObjectId(id)})
    jadwal["_id"] = str(jadwal["_id"])

    return jsonify(jadwal)


@app.route("/api/edit-jadwal/<id>", methods=["POST"])
def edit_jadwal(id):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})
        if user_info['role'] != 'pegawai':
            return redirect(url_for('home'))
        nama = request.form.get("nama")
        poli = request.form.get("poli")
        hari = request.form.getlist("hari")
        jam_buka = request.form.get("jam_buka")
        jam_tutup = request.form.get("jam_tutup")

        # Update jadwal data
        db.jadwal.update_one({"_id": ObjectId(id)}, {"$set": {
            "nama": nama,
            "poli": poli,
            "hari": hari,
            "jam_buka": jam_buka,
            "jam_tutup": jam_tutup,
        }})

        jadwal = db.jadwal.find_one({"_id": ObjectId(id)})
        jadwal["_id"] = str(jadwal["_id"])

        return jsonify(jadwal)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


@app.route("/api/hapus-jadwal/<id>", methods=["POST"])
def hapus_jadwal(id):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})
        if user_info['role'] != 'pegawai':
            return redirect(url_for('home'))
    # hapus jadwal data dari database
        db.jadwal.delete_one({"_id": ObjectId(id)})

        return jsonify({"message": "Jadwal berhasil dihapus"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
