import re
from flask import render_template, jsonify, request, redirect, url_for
import secrets
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient, ASCENDING, DESCENDING
import os
from os.path import join, dirname
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from bson import ObjectId
from flask_bcrypt import Bcrypt
from pagination import Pagination
from exceptions import HttpException, handle_http_exception
from apiresponse import api_response
from utils import *
from middlewares import *
from flask import make_response

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
# Register the error handler
app.errorhandler(HttpException)(handle_http_exception)
bcrypt = Bcrypt(app)

MONGODB_CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING")
if not MONGODB_CONNECTION_STRING:
    raise ValueError(
        "MONGODB_CONNECTION_STRING environment variable is not set")
DB_NAME = os.environ.get("DB_NAME")
if not DB_NAME:
    raise ValueError("DB_NAME environment variable is not set")
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client[DB_NAME]

TOKEN_KEY = os.environ.get("TOKEN_KEY")
if not TOKEN_KEY:
    raise ValueError("TOKEN_KEY environment variable is not set")
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")






#################### TEMPLATE ROUTES ####################

# Return Home Page
@app.route('/')
@validate_token_template(SECRET_KEY, TOKEN_KEY, db, allow_guest=True)
def home(decoded_token):
    msg = request.args.get('msg')
    scripts = ['js/index.js']
    css = ['css/index.css']
    if decoded_token:
        user_id = ObjectId(decoded_token.get("uid"))
        user_info = db.users.find_one({"_id": user_id}, {
                                        '_id': False, 'password': False})
        return render_template('pages/index.html', user_info=user_info, active_page='home', scripts=scripts, css=css, msg=msg)
    else:
        return render_template('pages/index.html', active_page='home', scripts=scripts, css=css, msg=msg)


# Return Login Page
@app.route('/login')
def login():
    msg = request.args.get('msg')
    scripts = ['js/login.js']
    css = ['css/login.css']
    return render_template('pages/login.html', msg=msg, scripts=scripts, css=css)


# Return Register Page
@app.route("/register")
def register():
    scripts = ['js/register.js']
    css = ['css/register.css']
    return render_template("pages/register.html", scripts=scripts, css=css)


# Return Pendaftaran Pasien Page (GET)
@app.route('/pendaftaran')
@validate_token_template(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_template(["pasien"])
def pendaftaran_get(decoded_token):
    scripts = ['js/pendaftaran.js']
    user_id = ObjectId(decoded_token.get("uid"))
    user_info = db.users.find_one({"_id": user_id}, {
                                    '_id': False, 'password': False})
    return render_template('pages/pendaftaran.html', user_info=user_info, active_page='pendaftaran', scripts=scripts)


# Return Riwayat Pendaftaran Page
@app.route("/riwayat_pendaftaran")
@validate_token_template(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_template(["pasien"])
def riwayat_pendaftaran(decoded_token):
    scripts = ['js/riwayat_pendaftaran.js']
    user_id = ObjectId(decoded_token.get("uid"))
    user_info = db.users.find_one({"_id": user_id}, {
                                    '_id': False, 'password': False})
    return render_template("pages/riwayat_pendaftaran.html", user_info=user_info, active_page='riwayat_pendaftaran', scripts=scripts)


# Return Riwayat Checkup Page
@app.route("/riwayat_checkup")
@validate_token_template(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_template(["pasien"])
def riwayat_checkup(decoded_token):
    scripts = ['js/riwayat_checkup.js']
    user_id = ObjectId(decoded_token.get("uid"))
    user_info = db.users.find_one({"_id": user_id}, {
                                    '_id': False, 'password': False})
    return render_template("pages/riwayat_checkup.html", user_info=user_info, active_page='riwayat_checkup', scripts=scripts)



# Return Profile Page
@app.route("/profile")
@validate_token_template(SECRET_KEY, TOKEN_KEY, db)
def profile(decoded_token):
    scripts = ['js/profile.js']
    css = ['css/profile.css']
    user_id = ObjectId(decoded_token.get("uid"))
    user_info = db.users.find_one({"_id": user_id}, {
                                    '_id': False, 'password': False})
    if is_valid_date(user_info.get('tgl_lahir')):
        user_info['tgl_lahir'] = datetime.strptime(user_info.get('tgl_lahir'), '%d-%m-%Y').strftime('%Y-%m-%d')
    print(user_info)
    return render_template('pages/profile.html', user_info=user_info, active_page='profile', scripts=scripts, css=css)


# Return Kelola Pendaftaran Page
@app.route("/kelola_pendaftaran")
@validate_token_template(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_template(["pegawai"])
def kelola_pendaftaran(decoded_token):
    scripts = ['js/kelola_pendaftaran.js']
    user_id = ObjectId(decoded_token.get("uid"))
    user_info = db.users.find_one({"_id": user_id}, {
                                    '_id': False, 'password': False})
    # Ambil data dari MongoDB sesuai dengan kebutuhan Anda
    data = list(db.registrations.find(
        {"status": {"$in": ["pending", "approved", "done"]}},
        {"name": True, "poli": True, "tanggal": True,
            "keluhan": True, "status": True, "_id": True, "antrian": True}
    ))

    return render_template('pages/kelola_pendaftaran.html', data=data, user_info=user_info, active_page='kelola_pendaftaran', scripts=scripts)


# Return Dashboard Page
@app.route("/dashboard")
@validate_token_template(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_template(["pegawai"])
def dashboard(decoded_token):
    scripts = ['js/dashboard.js']
    user_id = ObjectId(decoded_token.get("uid"))
    user_info = db.users.find_one({"_id": user_id}, {
                                    '_id': False, 'password': False})
    return render_template("pages/dashboard.html", user_info=user_info, active_page='dashboard', scripts=scripts)


# Return Rekam Medis Page
@app.route("/rekam_medis")
@validate_token_template(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_template(["pegawai"])
def get_rekam_medis(decoded_token):
    scripts = ['js/rekam_medis.js']
    user_id = ObjectId(decoded_token.get("uid"))
    user_info = db.users.find_one({"_id": user_id}, {
                                    '_id': False, 'password': False})
    data_rekam_medis = []
    for d in db.users.find():
        exist = db.registrations.find_one({'username': d['username']})
        if exist:
            data_rekam_medis.append({
                'username': d['username'],
                'nik': d['nik'],
                'name': d['name'],
                'action': 'lihat' if db.rekam_medis.find_one({'nik': d['nik']}) else 'buat'
            })
    return render_template("pages/rekam_medis.html", data_rekam_medis=data_rekam_medis, user_info=user_info, active_page='rekam_medis', scripts=scripts)


# Return Kelola Jadwal Page
@app.route('/kelola_praktik')
@validate_token_template(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_template(["pegawai"])
def kelola_praktik(decoded_token):
    scripts = ['js/praktik.js']
    user_id = ObjectId(decoded_token.get("uid"))
    user_info = db.users.find_one({"_id": user_id}, {
                                    '_id': False, 'password': False})
    return render_template('pages/praktik.html', user_info=user_info, active_page='kelola_praktik', scripts=scripts)





#################### API ROUTES ####################

# Handle Register
@app.route("/api/register", methods=["POST"])
def api_register():
    body = request.is_json
    if not body:
        raise HttpException(False, 415, "failed", "Data harus dalam bentuk JSON")
    
    data = request.get_json()
    if not data:
        raise HttpException(False, 400, "failed", "Data JSON tidak valid")

    username = data.get('username')
    name = data.get('name')
    nik = data.get('nik')
    tgl_lahir = data.get('tglLahir')
    gender = data.get('gender')
    agama = data.get('agama')
    status = data.get('status')
    alamat = data.get('alamat')
    no_telp = data.get('noTelp')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')

    # Cek apakah semua input sudah diisi
    if not all([username, name, nik, tgl_lahir, gender, agama, status, alamat, no_telp, password]):
        raise HttpException(False, 400, "failed", "Semua input harus diisi")
    

    # Cek apakah username sudah ada di database
    existing_user = db.users.find_one({'username': username})
    if existing_user:
        raise HttpException(False, 400, "failed", "Username sudah digunakan")

    # Cek apakah nik memiliki 16 digit angka
    if not is_valid_nik(nik):
        raise HttpException(False, 400, "failed", "NIK harusterdiri dari 16 digit angka")

    existing_nik = db.users.find_one({'nik': nik})
    if existing_nik:
        raise HttpException(False, 400, "failed", "NIK sudah digunakan")

    # Cek apakah format tanggal lahir valid
    if not is_valid_date(tgl_lahir):
        raise HttpException(False, 400, "failed", "Format tanggal lahir tidak valid, gunakan format dd-mm-yyyy")

    # Cek apakah tanggal lahir valid
    if not is_max_date_now(tgl_lahir):
        raise HttpException(False, 400, "failed", "Tanggal lahir tidak boleh lebih dari hari ini")

    # Cek apakah jenis kelamin valid
    if not is_valid_gender(gender):
        raise HttpException(False, 400, "failed", "Jenis kelamin tidak valid")

    # Cek apakah nomor telepon valid
    if not is_valid_phone_number(no_telp):
        raise HttpException(False, 400, "failed", "Nomor telepon tidak valid, gunakan format nomor 10 - 13 digit")

    # Cek apakah password sesuai
    if len(password) < 8:
        raise HttpException(False, 400, "failed", "Password harus memiliki minimal 8 karakter")

    if not any(char.isupper() for char in password):
        raise HttpException(False, 400, "failed", "Password harus memiliki minimal 1 huruf kapital")

    if not any(char.isdigit() for char in password):
        raise HttpException(False, 400, "failed", "Password harus memiliki minimal 1 angka")

    if not any(not char.isalnum() for char in password):
        raise HttpException(False, 400, "failed", "Password harus memiliki minimal 1 karakter spesial")

    if password != confirm_password:
        raise HttpException(False, 400, "failed", "Password dan konfirmasi password tidak sesuai")

    # Generate a unique salt for each user
    salt = secrets.token_hex(16)

    # Use a cost factor of 12, you can adjust it based on your security needs
    hashed_password = bcrypt.generate_password_hash(
        salt + password + salt, 10).decode('utf-8')

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
        'role': 'pasien',
        'salt': salt,
    }

    result = db.users.insert_one(user_data)
    response = api_response(True, 201, "success", "Pendaftaran akun berhasil", {'user_id': str(result.inserted_id), 'username': username})
    return jsonify(response.__dict__)


# Handle Login
@app.route("/api/login", methods=["POST"])
def sign_in():
    body = request.is_json
    if body:
        raise HttpException(False, 415, "failed", "Data harus dalam bentuk form data")
    # Sign in
    username_receive = request.form.get("username")
    password_receive = request.form.get("password")

    if not username_receive:
        raise HttpException(False, 400, "failed", "Username tidak boleh kosong")
    if not password_receive:
        raise HttpException(False, 400, "failed", "Password tidak boleh kosong")

    user = db.users.find_one({"username": username_receive})
    if not user:
        raise HttpException(False, 400, "failed", "Username / password salah")
    
    # Use bcrypt to verify the password with the stored salt
    check_password = bcrypt.check_password_hash(user.get('password'), user.get('salt') + password_receive + user.get('salt'))
    if not check_password:
        raise HttpException(False, 400, "failed", "Username / password salah")

    user_session = create_user_session(user["_id"], db)
    payload = {
        "uid": str(user["_id"]),
        "sid": str(user_session["_id"]),
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    response = api_response(True, 200, "success", "Login berhasil", {TOKEN_KEY: token})
    response_data = make_response(jsonify(response.__dict__))
    response_data.headers.add(
"Set-Cookie", f"{TOKEN_KEY}={token}; HttpOnly; Secure; Max-Age={60 * 60 * 24}; Path=/")
    return response_data


# Handle Logout
@app.route("/api/logout", methods=["POST"])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
def logout(decoded_token):
    user_id = ObjectId(decoded_token["uid"])
    session_id = ObjectId(decoded_token["sid"])
    logout_user_session(session_id, db)
    response = api_response(True, 200, "success", "Logout berhasil")
    response_data = make_response(jsonify(response.__dict__))
    response_data.headers.add(
        "Set-Cookie", f"{TOKEN_KEY}=; HttpOnly; Secure; Max-Age=0; Path=/")
    return response_data


# API Pendaftaran Dashboard
@app.route('/api/pendaftaran')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
def api_pendaftaran(decoded_token):
    # Get parameters from DataTables request
    draw = int(request.args.get('draw', 0))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    search_value = request.args.get('search[value]', '')
    status = request.args.getlist('status')
    order_column_index = int(request.args.get('order[0][column]', 0))  
    order_direction = request.args.get('order[0][dir]', 'asc')

    # Define regex pattern for matching variations of "Approve"
    approve_pattern = re.compile(r'^a(p(p(r(o(v(e?)?)?)?)?)?)?', re.IGNORECASE)
    reject_pattern = re.compile(r'^r(e(j(e(c(t?)?)?)?)?)?', re.IGNORECASE)
    done_pattern = re.compile(r'^d(o(n(e?)?)?)?', re.IGNORECASE)

    # MongoDB query with search
    query = {}
    if status:
        query['status'] = {"$in": status}
    if search_value:
        query["$or"] = [
            {"antrian": {"$regex": search_value, "$options": "i"}},
            {"name": {"$regex": search_value, "$options": "i"}},
            {"poli": {"$regex": search_value, "$options": "i"}},
            {"tanggal": {"$regex": search_value, "$options": "i"}},
            {"keluhan": {"$regex": search_value, "$options": "i"}},
        ]
    # check if status is approve and search value match with approve pattern
    if status and search_value and (approve_pattern.match(search_value) or reject_pattern.match(search_value)):
         query["$or"] += [
            {"status": "pending"},
         ]
    # check if status is done and search value match with done pattern
    if status and search_value and done_pattern.match(search_value):
            query["$or"] += [
                {"status": "approved"},
            ]

    if not status and search_value:
        query["$or"] += [
                {"status": {"$regex": search_value, "$options": "i"}},
            ]

    # Adjust the query for sorting
    sort_column = ["antrian", "name", "poli", "tanggal", "keluhan", "status"][order_column_index]
    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING
    collation = {'locale': 'en', 'strength': 2}
    data = list(db.registrations.find(query).sort(sort_column, sort_direction).collation(collation).skip(start).limit(length))
    for d in data:
        d['_id'] = str(d['_id'])
    

    # Total records count (unfiltered)
    total_records = db.registrations.count_documents({})

    # Total records count after filtering
    filtered_records = db.registrations.count_documents(query)

    total_pages = (filtered_records + length - 1) // length  # Calculate total pages
    # Create the meta pagination object
    pagination = Pagination(start+1, length, total_pages, filtered_records)

    # return jsonify(response.__dict__)
    response = api_response(True, 200, "success", "Data fetched successfully", data, pagination.__dict__, draw, start, length, total_records, filtered_records)

    return jsonify(response.__dict__)


# Pendaftaran Pasien (POST)
@app.route('/api/pendaftaran', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pasien"])
def pendaftaran_post(decoded_token):
    body = request.is_json
    if body:
        raise HttpException(False, 415, "failed", "Data harus dalam bentuk form data")
    
    user_id = ObjectId(decoded_token.get("uid"))
    # Ambil data pengguna dari koleksi users
    user_data = db.users.find_one({"_id": user_id}, {
                                    '_id': False, 'password': False})
    if not user_data:
        raise HttpException(False, 400, "failed", "Data pengguna tidak ditemukan")
    
    poli = request.form.get('poli')
    # get all poli from collection jadwal in a list
    poli_list = list(db.jadwal.distinct('poli'))
    if not poli:
        raise HttpException(False, 400, "failed", "Poli tidak boleh kosong")
    if poli not in poli_list:
        raise HttpException(False, 400, "failed", f"Poli {poli} tidak tersedia, pilih dari {poli_list}")
    tanggal = request.form.get('tanggal')
    if not tanggal:
        raise HttpException(False, 400, "failed", "Tanggal tidak boleh kosong")
    if not is_valid_date(tanggal):
        raise HttpException(False, 400, "failed", "Format tanggal tidak valid, gunakan format dd-mm-yyyy")
    if not is_min_date_now(tanggal):
        raise HttpException(False, 400, "failed", "Tanggal tidak boleh kurang dari hari ini")
    keluhan = request.form.get('keluhan')
    if not keluhan:
        raise HttpException(False, 400, "failed", "Keluhan tidak boleh kosong")
    has_pending_registration = bool(db.registrations.count_documents({
        "status": {"$in": ["pending"]},
        "username": user_data.get('username')
    }) > 0)
    if has_pending_registration:
        raise HttpException(False, 400, "failed", "Anda sudah memiliki pendaftaran yang sedang diproses")
    has_approved_registration = bool(db.registrations.count_documents({
        "status": {"$in": ["approved"]},
        "username": user_data.get('username')
    }) > 0)
    if has_approved_registration:
        raise HttpException(False, 400, "failed", "Anda sudah memiliki pendaftaran yang disetujui")
    
    # Masukkan data pendaftaran ke MongoDB
    data_pendaftaran = {
        'username': user_data.get('username'),
        'name': user_data.get('name'),
        'nik': user_data.get('nik'),
        'tgl_lahir': user_data.get('tgl_lahir'),
        'gender': user_data.get('gender'),
        'agama': user_data.get('agama'),
        'status_pernikahan': user_data.get('status'),
        'alamat': user_data.get('alamat'),
        'no_telp': user_data.get('no_telp'),
        'poli': poli,
        'tanggal': tanggal,
        'keluhan': keluhan,
        'status': 'pending'
    }

    result = db.registrations.insert_one(data_pendaftaran)
    data_pendaftaran["_id"] = str(result.inserted_id)

    response = api_response(True, 201, "success", "Formulir telah diproses. Silakan tunggu.", data_pendaftaran)
    return jsonify(response.__dict__)


# Return Riwayat Pendaftaran Pasien
@app.route('/api/pendaftaran/me')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pasien"])
def riwayat_pendaftaran_api(decoded_token):
    user_id = ObjectId(decoded_token.get("uid"))
    user_data = db.users.find_one({"_id": user_id}, {
                                    '_id': False, 'password': False})
    username = user_data.get('username')

    # Get parameters from DataTables request
    draw = int(request.args.get('draw', 0))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    search_value = request.args.get('search[value]', '')
    order_column_index = int(request.args.get('order[0][column]', 0))  
    order_direction = request.args.get('order[0][dir]', 'asc')

    
    if not user_data:
        raise HttpException(False, 400, "failed", "Data pengguna tidak ditemukan")
    
    # MongoDB query with search
    query = {'username': username}
    if search_value:
        query["$or"] = [
            {"name": {"$regex": search_value, "$options": "i"}},
            {"nik": {"$regex": search_value, "$options": "i"}},
            {"poli": {"$regex": search_value, "$options": "i"}},
            {"tanggal": {"$regex": search_value, "$options": "i"}},
            {"status": {"$regex": search_value, "$options": "i"}},
        ]

    # Adjust the query for sorting
    sort_column = ["_id","name", "nik", "poli", "tanggal", "status"][order_column_index]
    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING
    collation = {'locale': 'en', 'strength': 2}
    data = list(db.registrations.find(query).sort(sort_column, sort_direction).collation(collation).skip(start).limit(length))

    for d in data:
        d['_id'] = str(d['_id'])
    
    # Total records count (unfiltered)
    total_records = db.registrations.count_documents({'username': username})

    # Total records count after filtering
    filtered_records = db.registrations.count_documents(query)

    total_pages = (filtered_records + length - 1) // length  # Calculate total pages
    # Create the meta pagination object
    pagination = Pagination(start+1, length, total_pages, filtered_records)
    
    response = api_response(True, 200, "success", "Data berhasil diambil", data, pagination.__dict__, draw, start, length, total_records, filtered_records)
    return jsonify(response.__dict__)


@app.route('/api/pendaftaran/<id>/approve', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
def approve_pendaftaran(decoded_token, id):    
    data_pendaftaran = db.registrations.find_one(
        {"_id": ObjectId(id)})
    if data_pendaftaran.get('status') == 'approved':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah disetujui")
    
    if data_pendaftaran.get('status') == 'done':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah selesai")
    
    if data_pendaftaran.get('status') == 'rejected':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah ditolak")

    # Calculate the antrian based on the number of registrations for the same date and poli
    antrian = db.registrations.count_documents({
        "poli": data_pendaftaran["poli"],
        "tanggal": data_pendaftaran["tanggal"],
        'status': {'$in': ['approved', 'done']}
    })

    # Logika untuk menyetujui pendaftaran (mengubah status menjadi approved)
    db.registrations.update_one(
        {'_id': ObjectId(id)},
        {'$set': {'status': 'approved',
                    'antrian': f"{antrian + 1:03d}"}}
    )

    response = api_response(True, 200, "success", "Pendaftaran berhasil disetujui")
    return jsonify(response.__dict__)


@app.route('/api/pendaftaran/<id>/reject', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
def reject_pendaftaran(decoded_token, id):
    data_pendaftaran = db.registrations.find_one(
        {"_id": ObjectId(id)})

    if data_pendaftaran.get('status') == 'approved':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah disetujui")
    
    if data_pendaftaran.get('status') == 'done':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah selesai")
    
    if data_pendaftaran.get('status') == 'rejected':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah ditolak")

    # Logika untuk menolak pendaftaran (mengubah status menjadi rejected)
    db.registrations.update_one(
        {'_id': ObjectId(id)},
        {'$set': {'status': 'rejected'}}
    )

    response = api_response(True, 200, "success", "Pendaftaran berhasil ditolak")
    return jsonify(response.__dict__)


@app.route('/api/pendaftaran/<id>/done', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
def done_pendaftaran(decoded_token, id):
    data_pendaftaran = db.registrations.find_one(
        {"_id": ObjectId(id)})

    if data_pendaftaran.get('status') == 'pending':
        raise HttpException(False, 400, "failed", "Pendaftaran masih diproses")
    
    if data_pendaftaran.get('status') == 'done':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah selesai")
    
    if data_pendaftaran.get('status') == 'rejected':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah ditolak")

    # Logika untuk menyelesaikan pendaftaran (mengubah status menjadi done)
    db.registrations.update_one(
        {'_id': ObjectId(id)},
        {'$set': {'status': 'done'}}
    )

    db.list_checkup_user.insert_one({
        'nama': data_pendaftaran['name'],
        'nik': data_pendaftaran['nik'],
        'tgl_periksa': data_pendaftaran['tanggal'],
        'poli': data_pendaftaran['poli'],
        'keluhan': data_pendaftaran['keluhan']
    })

    response = api_response(True, 200, "success", "Pendaftaran selesai")
    return jsonify(response.__dict__)


# Return Atrian Hari Ini
@app.route('/api/antrian/today')
def get_antrian():
    # Ambil data antrian hari ini
    antrian_data = list(db.jadwal.aggregate([
        {
            "$lookup": {
                "from": "registrations",
                "localField": "poli",
                "foreignField": "poli",
                "as": "registrations"
            }
        },
        {
            "$unwind": {
                "path": "$registrations",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$group": {
                "_id": "$poli",
                "jumlah_pendaftar": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {
                                        "$or": [
                                            {"$eq": [
                                                "$registrations.status", "approved"]},
                                            {"$eq": [
                                                "$registrations.status", "done"]}
                                        ]
                                    },
                                    {"$eq": [
                                        "$registrations.tanggal", datetime.now().strftime("%d-%m-%Y")]}
                                ]
                            },
                            1,
                            0
                        ]
                    }
                },
                "dalam_antrian": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$eq": [
                                        "$registrations.status", "done"]},
                                    {"$eq": [
                                        "$registrations.tanggal", datetime.now().strftime("%d-%m-%Y")]}
                                ]
                            },
                            1,
                            0
                        ]
                    }
                },
            }
        },
        {
            "$project": {
                "_id": 0,
                "poli": "$_id",
                "jumlah_pendaftar": 1,
                "dalam_antrian": 1
            }
        }
    ]))
    for antrian in antrian_data:
        antrian['jumlah_pendaftar'] = db.registrations.count_documents({
            "poli": antrian['poli'],
            "tanggal": datetime.now().strftime("%d-%m-%Y"),
            "status": {"$in": ["approved", "done"]}
        })
        antrian['dalam_antrian'] = db.registrations.count_documents({
            "poli": antrian['poli'],
            "tanggal": datetime.now().strftime("%d-%m-%Y"),
            "status": "done"
        })
    response = api_response(True, 200, "success", "Antrian berhasil diambil", antrian_data)
    return jsonify(response.__dict__)



# Return Antrian Pasien
@app.route('/api/antrian/me')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pasien"])
def get_antrian_data(decoded_token):
    user_id = ObjectId(decoded_token.get("uid"))
    user_data = db.users.find_one({"_id": user_id}, {
                                    '_id': False, 'password': False})
    if not user_data:
        raise HttpException(False, 400, "failed", "Data pengguna tidak ditemukan")

    antrian_data = list(db.registrations.find(
        {
            "username": user_data.get('username'),
            "status": {"$in": ["pending", "approved"]}
        },
        {
            "_id": False
        }
    ))

    response = api_response(True, 200, "success", "Data berhasil diambil", antrian_data)

    return jsonify(response.__dict__)



@app.route('/api/antrian/check')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pasien"])
def check_antrian(decoded_token):
    user_id = ObjectId(decoded_token.get("uid"))
    user_data = db.users.find_one({"_id": user_id}, {
                                    '_id': False, 'password': False})
    if not user_data:
        raise HttpException(False, 400, "failed", "Data pengguna tidak ditemukan")


    has_pending_or_approved = bool(db.registrations.count_documents({
        "status": {"$in": ["pending", "approved"]},
        "username": user_data.get('username')
    }) > 0)

    response = api_response(True, 200, "success", "Data berhasil dimabil", {'has_pending_or_approved': has_pending_or_approved})
    return jsonify(response.__dict__)


# Return Riwayat Checkup Pasien
@app.route("/api/checkup/me")
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pasien"])
def api_riwayat_checkup(decoded_token):
    user_id = ObjectId(decoded_token.get("uid"))
    user_data = db.users.find_one({"_id": user_id}, {
                                    '_id': False, 'password': False})
    if not user_data:
        raise HttpException(False, 400, "failed", "Data pengguna tidak ditemukan")
    nik = user_data.get('nik')
    # Get parameters from DataTables request
    draw = int(request.args.get('draw', 0))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    search_value = request.args.get('search[value]', '')
    order_column_index = int(request.args.get('order[0][column]', 0))  
    order_direction = request.args.get('order[0][dir]', 'asc')

    
    if not user_data:
        raise HttpException(False, 400, "failed", "Data pengguna tidak ditemukan")
    
    # MongoDB query with search
    query = {'nik': nik}
    if search_value:
        query["$or"] = [
            {"tgl_periksa": {"$regex": search_value, "$options": "i"}},
            {"poli": {"$regex": search_value, "$options": "i"}},
            {"dokter": {"$regex": search_value, "$options": "i"}},
            {"keluhan": {"$regex": search_value, "$options": "i"}},
            {"hasil_anamnesa": {"$regex": search_value, "$options": "i"}},
        ]

    # Adjust the query for sorting
    sort_column = ["_id", "tgl_periksa", "poli", "dokter", "keluhan", "hasil_anamnesa"][order_column_index]
    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING
    collation = {'locale': 'en', 'strength': 2}
    data = list(db.list_checkup_user.find(query).sort(sort_column, sort_direction).collation(collation).skip(start).limit(length))

    for d in data:
        d['_id'] = str(d['_id'])
    
    # Total records count (unfiltered)
    total_records = db.list_checkup_user.count_documents({'nik': nik})

    # Total records count after filtering
    filtered_records = db.list_checkup_user.count_documents(query)

    total_pages = (filtered_records + length - 1) // length  # Calculate total pages
    # Create the meta pagination object
    pagination = Pagination(start+1, length, total_pages, filtered_records)

    response = api_response(True, 200, "success", "Data berhasil diambil", data, pagination.__dict__, draw, start, length, total_records, filtered_records)
    return jsonify(response.__dict__)


@app.route("/api/checkup")
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
def api_riwayat_checkup_pegawai(decoded_token):
    # Get parameters from DataTables request
    draw = int(request.args.get('draw', 0))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    search_value = request.args.get('search[value]', '')
    order_column_index = int(request.args.get('order[0][column]', 0))  
    order_direction = request.args.get('order[0][dir]', 'asc')

    # MongoDB query with search
    query = {}
    if search_value:
        query["$or"] = [
            {"tgl_periksa": {"$regex": search_value, "$options": "i"}},
            {"poli": {"$regex": search_value, "$options": "i"}},
            {"nama": {"$regex": search_value, "$options": "i"}},
            {"dokter": {"$regex": search_value, "$options": "i"}},
            {"keluhan": {"$regex": search_value, "$options": "i"}},
            {"hasil_anamnesa": {"$regex": search_value, "$options": "i"}},
        ]

    # Adjust the query for sorting
    sort_column = ["_id", "tgl_periksa", "nama", "dokter", "poli", "keluhan", "hasil_anamnesa"][order_column_index]
    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING
    data = list(db.list_checkup_user.find(query).sort(sort_column, sort_direction).skip(start).limit(length))

    for d in data:
        d['_id'] = str(d['_id'])
    
    # Total records count (unfiltered)
    total_records = db.list_checkup_user.count_documents({})

    # Total records count after filtering
    filtered_records = db.list_checkup_user.count_documents(query)

    total_pages = (filtered_records + length - 1) // length  # Calculate total pages
    # Create the meta pagination object
    pagination = Pagination(start+1, length, total_pages, filtered_records)

    response = api_response(True, 200, "success", "Data berhasil diambil", data, pagination.__dict__, draw, start, length, total_records, filtered_records)
    return jsonify(response.__dict__)



@app.route("/api/checkup/<nik>")
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
def api_pasien_checkup(decoded_token, nik):
    # Get parameters from DataTables request
    draw = int(request.args.get('draw', 0))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    search_value = request.args.get('search[value]', '')
    order_column_index = int(request.args.get('order[0][column]', 0))  
    order_direction = request.args.get('order[0][dir]', 'desc')

    # MongoDB query with search
    query = {'nik': nik}
    if search_value:
        query["$or"] = [
            {"tgl_periksa": {"$regex": search_value, "$options": "i"}},
            {"poli": {"$regex": search_value, "$options": "i"}},
            {"dokter": {"$regex": search_value, "$options": "i"}},
            {"keluhan": {"$regex": search_value, "$options": "i"}},
            {"hasil_anamnesa": {"$regex": search_value, "$options": "i"}},
        ]

    # Adjust the query for sorting
    sort_column = ["_id", "tgl_periksa", "dokter", "poli", "keluhan", "hasil_anamnesa", "action"][order_column_index]
    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING
    data = list(db.list_checkup_user.find(query).sort(sort_column, sort_direction).skip(start).limit(length))

    for d in data:
        d['_id'] = str(d['_id'])
    
    # Total records count (unfiltered)
    total_records = db.list_checkup_user.count_documents({'nik': nik})

    # Total records count after filtering
    filtered_records = db.list_checkup_user.count_documents(query)

    total_pages = (filtered_records + length - 1) // length

    # Create the meta pagination object
    pagination = Pagination(start+1, length, total_pages, filtered_records)
    response = api_response(True, 200, "success", "Data berhasil diambil", data, pagination.__dict__, draw, start, length, total_records, filtered_records)
    return jsonify(response.__dict__)


@app.route('/api/checkup/<nik>/<id>')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
def api_detail_checkup(decoded_token,nik, id):
    data = db.list_checkup_user.find_one({"_id": ObjectId(id)}, {"_id": False})
    if not data:
        raise HttpException(False, 400, "failed", "Data tidak ditemukan")
    response = api_response(True, 200, "success", "Data berhasil diambil", data)
    return jsonify(response.__dict__)


@app.route('/api/checkup/<nik>/<id>', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
def edit_checkup(decoded_token, nik, id):
    body = request.is_json
    if body:
        raise HttpException(False, 415, "failed", "Data harus dalam bentuk form data")
    data = db.list_checkup_user.find_one({"_id": ObjectId(id)}, {"_id": False})
    if not data:
        raise HttpException(False, 400, "failed", "Data tidak ditemukan")

    doc = {}
    dokter = request.form.get('dokter')
    dokter_list = list(db.jadwal.distinct('nama'))
    if dokter:
        if dokter not in dokter_list:
            raise HttpException(False, 400, "failed", f"Dokter {dokter} tidak tersedia, pilih dari {dokter_list}")
        doc['dokter'] = dokter

    hasil_anamnesa = request.form.get('hasil_anamnesa')
    if hasil_anamnesa:
        doc['hasil_anamnesa'] = hasil_anamnesa

    db.list_checkup_user.update_one({"_id": ObjectId(id)}, {"$set": doc})

    response = api_response(True, 200, "success", "Data berhasil diperbarui")
    return jsonify(response.__dict__)


# Return Profile User
@app.route("/api/profile")
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
def api_profile(decoded_token):
    user_id = ObjectId(decoded_token.get("uid"))
    user_data = db.users.find_one({"_id": user_id}, {
                                    '_id': False, 'password': False})
    response = api_response(True, 200, "success", "Data berhasil diambil", user_data)
    return jsonify(response.__dict__)


# Handle Edit Profile
@app.route('/api/profile/edit', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
def edit_profile(decoded_token):
    user_id = ObjectId(decoded_token.get("uid"))
    user_data = db.users.find_one({"_id": user_id}, {
                                    '_id': False, 'password': False})
    body = request.is_json
    if body:
        raise HttpException(False, 415, "failed", "Data harus dalam bentuk form data")
    
    username = user_data.get('username')
    old_nik = user_data.get('nik')
    file_path = user_data.get('profile_pic')

    name = request.form.get('name')
    nik = request.form.get('nik')
    tgl_lahir = request.form.get('tgl_lahir')
    gender = request.form.get('gender')
    agama = request.form.get('agama')
    status = request.form.get('status')
    alamat = request.form.get('alamat')
    no_telp = request.form.get('no_tlp')

    # Prepare the update document
    profile_doc = {}
    checkup_doc = {}
    registration_doc = {}
    rekam_medis = {}
    if name:
        profile_doc['name'] = name
        checkup_doc['nama'] = name
        registration_doc['name'] = name
        rekam_medis['nama'] = name
    if nik:
        if not is_valid_nik(nik):
            raise HttpException(False, 400, "failed", "NIK harus terdiri dari 16 digit angka")
        existing_nik = db.users.find_one({'nik': nik})
        if existing_nik and existing_nik['username'] != username:
            raise HttpException(False, 400, "failed", "NIK sudah digunakan")
        profile_doc['nik'] = nik
        checkup_doc['nik'] = nik
        registration_doc['nik'] = nik
        rekam_medis['nik'] = nik
    if tgl_lahir:
        if not is_valid_date(tgl_lahir):
            raise HttpException(False, 400, "failed", "Format tanggal lahir tidak valid, gunakan format dd-mm-yyyy")
        if not is_max_date_now(tgl_lahir):
            raise HttpException(False, 400, "failed", "Tanggal lahir tidak boleh lebih dari hari ini")
        profile_doc['tgl_lahir'] = tgl_lahir
        registration_doc['tgl_lahir'] = tgl_lahir
        rekam_medis['umur'] = (datetime.now() - datetime.strptime(tgl_lahir, '%d-%m-%Y')).days // 365
    if gender:
        if not is_valid_gender(gender):
            raise HttpException(False, 400, "failed", "Jenis kelamin tidak valid")
        profile_doc['gender'] = gender
        registration_doc['gender'] = gender
    if agama:
        profile_doc['agama'] = agama
        registration_doc['agama'] = agama
    if status:
        profile_doc['status'] = status
        registration_doc['status_pernikahan'] = status
    if alamat:
        profile_doc['alamat'] = alamat
        registration_doc['alamat'] = alamat
        rekam_medis['alamat'] = alamat
    if no_telp:
        if not is_valid_phone_number(no_telp):
            raise HttpException(False, 400, "failed", "Nomor telepon tidak valid, gunakan format nomor 10 - 13 digit")
        profile_doc['no_telp'] = no_telp
        registration_doc['no_telp'] = no_telp
        rekam_medis['no_telp'] = no_telp

    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file.filename == '':
            raise HttpException(False, 400, "failed", "Profile picture tidak boleh kosong")
        filename = secure_filename(file.filename)
        extension = filename.split(".")[-1]
        if extension not in ["jpg", "jpeg", "png"]:
            raise HttpException(False, 400, "failed", "Profile picture harus berupa file gambar")
        file_path = f"profile_pics/{username}.{extension}"
        file.save("./static/" + file_path)
        profile_doc["profile_pic"] = file_path
    # update collection users
    db.users.update_one({"username": username}, {"$set": profile_doc})
    # update collection registrations
    db.registrations.update_many({"username": username}, {"$set": registration_doc})
    # update collection checkup
    db.list_checkup_user.update_many({"nik": old_nik}, {"$set": checkup_doc})
    # update collection rekam_medis
    db.rekam_medis.update_many({"nik": old_nik}, {"$set": rekam_medis})

    response = api_response(True, 200, "success", "Profile berhasil diperbarui")

    return jsonify(response.__dict__)


@app.route('/api/rekam_medis')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
def api_rekam_medis(decoded_token):
    # Get parameters from DataTables request
    draw = int(request.args.get('draw', 0))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    search_value = request.args.get('search[value]', '')
    order_column_index = int(request.args.get('order[0][column]', 0))  
    order_direction = request.args.get('order[0][dir]', 'asc')

    # MongoDB query with search
    query = {}
    if search_value:
        query["$or"] = [
            {"nama": {"$regex": search_value, "$options": "i"}},
            {"nik": {"$regex": search_value, "$options": "i"}},
        ]

    # Adjust the query for sorting
    sort_column = ["_id", "nama", "nik", "umur"][order_column_index]
    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING
    data = list(db.rekam_medis.find(query).sort(sort_column, sort_direction).skip(start).limit(length))

    for d in data:
        d['_id'] = str(d['_id'])

    # Total records count (unfiltered)
    total_records = db.rekam_medis.count_documents({})

    # Total records count after filtering
    filtered_records = db.rekam_medis.count_documents(query)

    total_pages = (filtered_records + length - 1) // length  # Calculate total pages
    # Create the meta pagination object
    pagination = Pagination(start+1, length, total_pages, filtered_records)

    response = api_response(True, 200, "success", "Data berhasil diambil", data, pagination.__dict__, draw, start, length, total_records, filtered_records)
    return jsonify(response.__dict__)


@app.route('/api/rekam_medis', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
def api_rekam_medis_post(decoded_token):
    body = request.is_json
    if body:
        raise HttpException(False, 415, "failed", "Data harus dalam bentuk form data")
    
    no_kartu = request.form.get('no')
    existing_no_kartu = bool(db.rekam_medis.count_documents({'no_kartu': no_kartu}) > 0)
    if not no_kartu:
        raise HttpException(False, 400, "failed", "Nomor kartu tidak boleh kosong")
    if existing_no_kartu:
        raise HttpException(False, 400, "failed", "Nomor kartu sudah digunakan")
    if not is_valid_no_kartu(no_kartu):
        raise HttpException(False, 400, "failed", "Format nomor kartu tidak valid, gunakan format nn-nn-nn")
    dokter = request.form.get('dokter')
    dokter_list = list(db.jadwal.distinct('nama'))
    if not dokter:
        raise HttpException(False, 400, "failed", "Dokter tidak boleh kosong")
    if dokter not in dokter_list:
        raise HttpException(False, 400, "failed", f"Dokter {dokter} tidak tersedia, pilih dari {dokter_list}")
    hasil_anamnesa = request.form.get('hasil_anamnesa')
    if not hasil_anamnesa:
        raise HttpException(False, 400, "failed", "Hasil anamnesa tidak boleh kosong")
    nik = request.form.get('nik')
    if not nik:
        raise HttpException(False, 400, "failed", "NIK tidak boleh kosong")
    existing_rekam_medis = bool(db.rekam_medis.count_documents({'nik': nik}))
    if existing_rekam_medis:
        raise HttpException(False, 400, "failed", "Rekam medis sudah ada")
    user_data = db.users.find_one({'nik': nik})
    if not user_data:
        raise HttpException(False, 400, "failed", "Data pengguna tidak ditemukan")
    data_reg = db.registrations.find_one({'nik': nik})
    if not data_reg:
        raise HttpException(False, 400, "failed", "Data pendaftaran tidak ditemukan")
    nama = user_data.get('name')
    data_rekam_medis = {
        'no_kartu': no_kartu,
        'nama': nama,
        'nik': nik,
        'umur': (datetime.now() - datetime.strptime(user_data['tgl_lahir'], '%d-%m-%Y')).days // 365,
        'alamat': user_data['alamat'],
        'no_telp': user_data['no_telp']
    }
    db.rekam_medis.insert_one(data_rekam_medis)
    data_list_checkup_user = {
        'nama': nama,
        'poli': data_reg['poli'],
        'keluhan': data_reg['keluhan'],
        'tgl_periksa': data_reg['tanggal'],
        'dokter': dokter,
        'hasil_anamnesa': hasil_anamnesa
    }

    db.list_checkup_user.update_one(
        {'nik': nik}, {'$set': data_list_checkup_user}, upsert=True)
    
    response = api_response(True, 200, "success", "Rekam medis berhasil dibuat")
    return jsonify(response.__dict__)


@app.route('/api/users/pasien')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
def api_users_pasien(decoded_token):
    # Get parameters from DataTables request
    draw = int(request.args.get('draw', 0))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    search_value = request.args.get('search[value]', '')
    order_column_index = int(request.args.get('order[0][column]', 0))
    order_direction = request.args.get('order[0][dir]', 'asc')

    # Get unique usernames from registrations with status: done
    unique_usernames = db.registrations.distinct("username", {"status": "done"})

    # MongoDB query with search
    query = {"username": {"$in": unique_usernames}}
    if search_value:
        query["$or"] = [
            {"name": {"$regex": search_value, "$options": "i"}},
            {"nik": {"$regex": search_value, "$options": "i"}},
        ]

    # Adjust the query for sorting
    sort_column = ["_id","name", "nik", "action"][order_column_index]
    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING

    # Fetch user details from users collection based on unique usernames
    data_pasien_list = (
        db.users.find(query)
        .sort(sort_column, sort_direction)
        .skip(start)
        .limit(length)
    )

    # Process the data_pasien_list to include 'has_rekam_medis' field
    data_pasien = []
    for d in data_pasien_list:
        has_rekam_medis = bool(db.rekam_medis.find_one({'nik': d['nik']}))
        data_pasien.append({
            'username': d['username'],
            'nik': d['nik'],
            'name': d['name'],
            'has_rekam_medis': has_rekam_medis
        })

    # Total records count (unfiltered)
    total_records = db.users.count_documents({'username': {'$in': unique_usernames}})

    # Total records count after filtering
    filtered_records = db.users.count_documents(query)

    total_pages = (filtered_records + length - 1) // length  # Calculate total pages
    # Create the meta pagination object
    pagination = Pagination(start + 1, length, total_pages, filtered_records)

    response = api_response(
        True, 200, "success", "Data berhasil diambil", data_pasien, pagination.__dict__, draw, start, length, total_records, filtered_records
    )
    return jsonify(response.__dict__)
  

@app.route('/api/jadwal')
def api_jadwal():
    # Get parameters from DataTables request
    draw = int(request.args.get('draw', 0))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    search_value = request.args.get('search[value]', '')
    order_column_index = int(request.args.get('order[0][column]', 0))  
    order_direction = request.args.get('order[0][dir]', 'asc')

    # MongoDB query with search
    query = {}
    if search_value:
        query["$or"] = [
            {"nama": {"$regex": search_value, "$options": "i"}},
            {"poli": {"$regex": search_value, "$options": "i"}},
            {"hari": {"$regex": search_value, "$options": "i"}},
            {"jam_buka": {"$regex": search_value, "$options": "i"}},
            {"jam_tutup": {"$regex": search_value, "$options": "i"}},
        ]

    # Adjust the query for sorting
    sort_column = ["nama", "poli", "hari", "jam_buka", "jam_tutup"][order_column_index]
    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING
    collation = {'locale': 'en', 'strength': 2}
    data = list(db.jadwal.find(query).sort(sort_column, sort_direction).collation(collation).skip(start).limit(length))

    for d in data:
        d['_id'] = str(d['_id'])
    
    # Total records count (unfiltered)
    total_records = db.jadwal.count_documents({})

    # Total records count after filtering
    filtered_records = db.jadwal.count_documents(query)

    total_pages = (filtered_records + length - 1) // length

    # Create the meta pagination object
    pagination = Pagination(start+1, length, total_pages, filtered_records)

    response = api_response(True, 200, "success", "Data berhasil diambil", data, pagination.__dict__, draw, start, length, total_records, filtered_records)

    return jsonify(response.__dict__)


@app.route('/api/jadwal', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
def api_jadwal_post(decoded_token):
    body = request.is_json
    if body:
        raise HttpException(False, 415, "failed", "Data harus dalam bentuk form data")
    
    nama = request.form.get('nama')
    if not nama:
        raise HttpException(False, 400, "failed", "Nama tidak boleh kosong")
    poli = request.form.get('poli')
    if not poli:
        raise HttpException(False, 400, "failed", "Poli tidak boleh kosong")
    hari = request.form.getlist('hari')
    if not hari:
        raise HttpException(False, 400, "failed", "Hari tidak boleh kosong")
    jam_buka = request.form.get('jam_buka')
    if not jam_buka:
        raise HttpException(False, 400, "failed", "Jam buka tidak boleh kosong")
    jam_tutup = request.form.get('jam_tutup')
    if not jam_tutup:
        raise HttpException(False, 400, "failed", "Jam tutup tidak boleh kosong")
    if not isinstance(hari, list):
        raise HttpException(False, 400, "failed", "Hari harus merupakan list")
    if any(x for x in hari if x.lower() not in ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu']):
        raise HttpException(False, 400, "failed", "Hari tidak valid")
    if not is_valid_time(jam_buka):
        raise HttpException(False, 400, "failed", "Format jam buka tidak valid")
    if not is_valid_time(jam_tutup):
        raise HttpException(False, 400, "failed", "Format jam tutup tidak valid")
    if datetime.strptime(jam_buka, '%H:%M') > datetime.strptime(jam_tutup, '%H:%M'):
        raise HttpException(False, 400, "failed", "Jam buka tidak boleh lebih besar dari jam tutup")
    jadwal_data = {
        "nama": nama,
        "poli": poli,
        "hari": hari,
        "jam_buka": jam_buka,
        "jam_tutup": jam_tutup,
    }
    result = db.jadwal.insert_one(jadwal_data)
    jadwal_data["_id"] = str(result.inserted_id)
    response = api_response(True, 200, "success", "Jadwal berhasil ditambahkan", jadwal_data)
    return jsonify(response.__dict__)


@app.route('/api/jadwal/<id>')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
def api_detail_jadwal(decoded_token, id):
    data = db.jadwal.find_one({"_id": ObjectId(id)}, {"_id": False})
    if not data:
        raise HttpException(False, 400, "failed", "Data tidak ditemukan")
    response = api_response(True, 200, "success", "Data berhasil diambil", data)
    return jsonify(response.__dict__)


@app.route('/api/jadwal/<id>', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
def api_jadwal_put(decoded_token, id):
    body = request.is_json
    if body:
        raise HttpException(False, 415, "failed", "Data harus dalam bentuk form data")
    doc = {}
    nama = request.form.get('nama')
    if nama:
        doc['nama'] = nama
    poli = request.form.get('poli')
    if poli:
        doc['poli'] = poli
    hari = request.form.getlist('hari')
    if hari:
        if not isinstance(hari, list):
            raise HttpException(False, 400, "failed", "Hari harus merupakan list")
        if any(x for x in hari if x.lower() not in ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu']):
            raise HttpException(False, 400, "failed", "Hari tidak valid")
        doc['hari'] = hari
    jam_buka = request.form.get('jam_buka')
    jam_tutup = request.form.get('jam_tutup')
    if jam_buka and not jam_tutup:
        raise HttpException(False, 400, "failed", "Jam tutup tidak boleh kosong")
    if not jam_buka and jam_tutup:
        raise HttpException(False, 400, "failed", "Jam buka tidak boleh kosong")
    if jam_buka and jam_tutup:
        if not is_valid_time(jam_buka):
            raise HttpException(False, 400, "failed", "Format jam buka tidak valid")
        if not is_valid_time(jam_tutup):
            raise HttpException(False, 400, "failed", "Format jam tutup tidak valid")
        if datetime.strptime(jam_buka, '%H:%M') > datetime.strptime(jam_tutup, '%H:%M'):
            raise HttpException(False, 400, "failed", "Jam buka tidak boleh lebih besar dari jam tutup")
        doc['jam_buka'] = jam_buka
        doc['jam_tutup'] = jam_tutup


    db.jadwal.update_one({"_id": ObjectId(id)}, {"$set": doc})

    response = api_response(True, 200, "success", "Jadwal berhasil diperbarui")
    return jsonify(response.__dict__)



# Handle Hapus Jadwal
@app.route("/api/hapus_jadwal/<id>", methods=["POST"])
def hapus_jadwal(id):
    token_receive = get_authorization()
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})
        if user_info['role'] != 'pegawai':
            return jsonify({'result': 'fail', 'message': 'You must login as pegawai'})
        # hapus jadwal data dari database
        db.jadwal.delete_one({"_id": ObjectId(id)})

        return jsonify({"result": "success", "message": "Jadwal berhasil dihapus"})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'message': 'Your login token has expired'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'message': 'There was an error decoding your token'})


@app.route('/api/jadwal/<id>', methods=['DELETE'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
def api_jadwal_delete(decoded_token, id):
    data = db.jadwal.find_one({"_id": ObjectId(id)}, {"_id": False})
    if not data:
        raise HttpException(False, 400, "failed", "Data tidak ditemukan")
    db.jadwal.delete_one({"_id": ObjectId(id)})
    response = api_response(True, 200, "success", "Jadwal berhasil dihapus")
    return jsonify(response.__dict__)



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
