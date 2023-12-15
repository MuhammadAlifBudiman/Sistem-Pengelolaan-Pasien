from hmac import new
from flask import render_template, jsonify, request, redirect, url_for
import secrets
from tarfile import data_filter
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import os
from os.path import join, dirname
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from bson import ObjectId
from flask_bcrypt import Bcrypt
from pagination import Pagination, paginate_data
from exceptions import HttpException, handle_http_exception
from apiresponse import ApiResponse, api_response, DataTablesApiResponse, api_response_for_datatables
from functools import wraps

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


def get_authorization():
    cookie = request.cookies.get(TOKEN_KEY)
    header = request.headers.get('Authorization')
    if cookie:
        return cookie
    if header:
        return header.split()[1]

    return None


def is_valid_nik(nik):
    return nik.isdigit() and len(nik) == 16


def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%d-%m-%Y')
        return True
    except ValueError:
        return False


def is_valid_time(time_str):
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False


def is_valid_gender(gender):
    return gender.lower() in ['laki-laki', 'perempuan']


def is_valid_phone_number(phone_number):
    return phone_number.isdigit() and 10 <= len(phone_number) <= 13




#################### TEMPLATE ROUTES ####################

# Return Home Page
@app.route('/', methods=['GET'])
def home():
    msg = request.args.get('msg')
    token_receive = request.cookies.get(TOKEN_KEY)
    scripts = ['js/index.js']
    css = ['css/index.css']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload['id']})
        return render_template('pages/index.html', user_info=user_info, active_page='home', scripts=scripts, css=css, msg=msg)
    except jwt.ExpiredSignatureError:
        return render_template('pages/index.html', msg="Your login token has expired", active_page='home', scripts=scripts, css=css)
    except jwt.exceptions.DecodeError:
        return render_template('pages/index.html', msg=msg if msg is not None else "There was a problem", active_page='home', scripts=scripts, css=css)


# Return Login Page
@app.route('/login', methods=['GET'])
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
def pendaftaran_get():
    token_receive = request.cookies.get(TOKEN_KEY)
    scripts = ['js/pendaftaran.js']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username})
        return render_template('pages/pendaftaran.html', user_info=user_info, active_page='pendaftaran', scripts=scripts)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


# Return Riwayat Pendaftaran Page
@app.route("/riwayat_pendaftaran")
def riwayat_pendaftaran():
    token_receive = request.cookies.get(TOKEN_KEY)
    scripts = ['js/riwayat_pendaftaran.js']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username})
        return render_template("pages/riwayat_pendaftaran.html", user_info=user_info, active_page='riwayat_pendaftaran', scripts=scripts)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


# Return Riwayat Checkup Page
@app.route("/riwayat_checkup")
def riwayat_checkup():
    token_receive = get_authorization()
    scripts = ['js/riwayat_checkup.js']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})
        return render_template("pages/riwayat_checkup.html", user_info=user_info, active_page='riwayat_checkup', scripts=scripts)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


# Return Profile Page
@app.route("/profile")
def profile():
    token_receive = get_authorization()
    scripts = ['js/profile.js']
    css = ['css/profile.css']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload['id']}, {
                                      '_id': False, 'password': False})
        # format tgl_lahir to yyyy-mm-dd
        user_info["tgl_lahir"] = datetime.strptime(
            user_info["tgl_lahir"], "%d-%m-%Y").strftime("%Y-%m-%d")
        return render_template('pages/profile.html', user_info=user_info, active_page='profile', scripts=scripts, css=css)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


# Return Kelola Pendaftaran Page
@app.route("/kelola_pendaftaran")
def kelola_pendaftaran():
    token_receive = request.cookies.get(TOKEN_KEY)
    scripts = ['js/kelola_pendaftaran.js']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username})
        # Ambil data dari MongoDB sesuai dengan kebutuhan Anda
        data = list(db.registrations.find(
            {"status": {"$in": ["pending", "approved", "done"]}},
            {"name": True, "poli": True, "tanggal": True,
                "keluhan": True, "status": True, "_id": True, "antrian": True}
        ))


        # Tambahkan nomor urut pada setiap data
        # for index, row in enumerate(data, start=1):
        #     row['no_urut'] = index

        return render_template('pages/kelola_pendaftaran.html', data=data, user_info=user_info, active_page='kelola_pendaftaran', scripts=scripts)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


# Return Dashboard Page
@app.route("/dashboard")
def dashboard():
    token_receive = get_authorization()
    scripts = ['js/dashboard.js']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})
        return render_template("pages/dashboard.html", user_info=user_info, active_page='dashboard', scripts=scripts)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


# Return Rekam Medis Page
@app.route("/rekam_medis")
def get_rekam_medis():
    token_receive = get_authorization()
    scripts = ['js/rekam_medis.js']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})
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
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


# Return Kelola Jadwal Page
@app.route('/kelola_praktik')
def kelola_praktik():
    token_receive = get_authorization()
    scripts = ['js/praktik.js']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})
        if user_info['role'] != 'pegawai':
            return redirect(url_for("login", msg="You must login as pegawai"))
        return render_template('pages/praktik.html', user_info=user_info, active_page='kelola_praktik', scripts=scripts)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))





#################### API ROUTES ####################

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
                                    {"$eq": [
                                        "$registrations.status", "approved"]},
                                    {"$eq": [
                                        "$registrations.tanggal", datetime.now().strftime("%Y-%m-%d")]}
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
                                        "$registrations.tanggal", datetime.now().strftime("%Y-%m-%d")]}
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

    response = api_response(True, 200, "success", "Antrian fetched successfully", antrian_data)
    return jsonify(response.__dict__)


# Handle Register
@app.route("/api/register", methods=["POST"])
def api_register():
    body = request.is_json
    if not body:
        raise HttpException(False, 415, "failed", "Data Must be in JSON Format")
    
    data = request.get_json()
    if not data:
        raise HttpException(False, 400, "failed", "Invalid JSON Data")

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
        raise HttpException(False, 400, "failed", "NIK harus 16 digit angka")

    existing_nik = db.users.find_one({'nik': nik})
    if existing_nik:
        raise HttpException(False, 400, "failed", "NIK sudah digunakan")

    # Cek apakah format tanggal lahir valid
    if not is_valid_date(tgl_lahir):
        raise HttpException(False, 400, "failed", "Format tanggal lahir tidak valid")

    # Cek apakah tanggal lahir valid
    if datetime.strptime(tgl_lahir, '%d-%m-%Y') > datetime.now():
        raise HttpException(False, 400, "failed", "Tanggal lahir tidak valid")

    # Cek apakah jenis kelamin valid
    if not is_valid_gender(gender):
        raise HttpException(False, 400, "failed", "Jenis kelamin tidak valid")

    # Cek apakah nomor telepon valid
    if not is_valid_phone_number(no_telp):
        raise HttpException(False, 400, "failed", "Nomor telepon tidak valid")

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
        raise HttpException(False, 400, "failed", "Password tidak sesuai")

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
    response = api_response(True, 201, "success", "Register berhasil", {'user_id': str(result.inserted_id), 'username': username})
    return jsonify(response.__dict__)


# Handle Login
@app.route("/api/login", methods=["POST"])
def sign_in():
    body = request.is_json
    if body:
        raise HttpException(False, 415, "failed", "Data Must be in Form Data")
    # Sign in
    username_receive = request.form.get("username")
    password_receive = request.form.get("password")

    if not username_receive:
        raise HttpException(False, 400, "failed", "Username tidak boleh kosong")
    if not password_receive:
        raise HttpException(False, 400, "failed", "Password tidak boleh kosong")

    user = db.users.find_one({"username": username_receive})

    if user and 'password' in user and 'salt' in user:
        # Use bcrypt to verify the password with the stored salt
        if bcrypt.check_password_hash(user["password"], user["salt"] + password_receive + user["salt"]):
            payload = {
                "id": username_receive,
                # the token will be valid for 24 hours
                "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            response = api_response(True, 200, "success", "Login berhasil", {'token': token})
            return jsonify(response.__dict__)
        else:
            raise HttpException(False, 400, "failed", "We could not find a user with that id/password combination")
    else:
        raise HttpException(False, 400, "failed", "We could not find a user with that id/password combination")


# API Pendaftaran Dashboard
# Coba pagination buat datatables
@app.route('/api/pendaftaran')
def api_pendaftaran():
    token_receive = get_authorization()
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # Get parameters from DataTables request
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('length', 10))  # Number of records per page
        draw = int(request.args.get('draw', 0))
        start = int(request.args.get('start', 0))
        length = int(request.args.get('length', 10))
        search_value = request.args.get('search[value]', '')

        # MongoDB query with search
        query = {}
        if search_value:
            query["$or"] = [
                {"name": {"$regex": search_value, "$options": "i"}},
                {"poli": {"$regex": search_value, "$options": "i"}},
                {"tanggal": {"$regex": search_value, "$options": "i"}},
                {"keluhan": {"$regex": search_value, "$options": "i"}},
                {"status": {"$regex": search_value, "$options": "i"}},
            ]

        data = list(db.registrations.find(query).skip(start).limit(length))

        # data = list(db.registrations.find(
        #     {"status": {"$in": ["pending", "approved", "done"]}},
        #     {"name": True, "poli": True, "tanggal": True,
        #         "keluhan": True, "status": True, "_id": True, "antrian": True}
        # ))
        for d in data:
            d['_id'] = str(d['_id'])
        
        total_items = len(data)
        total_pages = (total_items + per_page - 1) // per_page  # Calculate total pages
        # Paginate the data
        paginated_data = paginate_data(data, page, per_page)

        # Total records count (unfiltered)
        total_records = db.registrations.count_documents({})

        # Total records count after filtering
        filtered_records = db.registrations.count_documents(query)

        # Create the pagination object
        pagination = Pagination(page, per_page, total_pages, total_items)

        # response = api_response(True, 200, "success", "Data fetched successfully", paginated_data, pagination.__dict__)

        # return jsonify(response.__dict__)
        response = api_response_for_datatables(draw, total_records, filtered_records, data)

        return jsonify(response.__dict__)

    except jwt.ExpiredSignatureError:
        raise HttpException(False, 401, "failed", "Your login token has expired")
    except jwt.exceptions.DecodeError:
        raise HttpException(False, 401, "failed", "There was an error decoding your token")

# Return Antrian Pasien
@app.route('/get_antrian_data', methods=['GET'])
def get_antrian_data():
    token_receive = request.cookies.get(TOKEN_KEY)

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')

        if username:

            antrian_data = list(db.registrations.find(
                {
                    "username": username,
                    "status": {"$in": ["pending", "approved"]}
                },
                {
                    "antrian": True,
                    "name": True,
                    "nik": True,
                    "tanggal": True,
                    "status": True,
                    "_id": False
                }
            ))

            # for index, data in enumerate(antrian_data, start=1):
            #     data['no_urut'] = index

            # app.logger.info(f"Data Antrian: {antrian_data}")
            # print(antrian_data)
            if any(data['status'] in ['rejected', 'done'] for data in antrian_data):
                print("jalan")
                return render_template('pendaftaran.html', has_pending_or_approved=False)

            return jsonify({'antrian_data': antrian_data, 'has_pending_or_approved': True})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        pass

    return render_template('pendaftaran.html', has_pending_or_approved=False)

# Pendaftaran Pasien (POST)
@app.route('/api/pendaftaran', methods=['POST'])
def pendaftaran_post():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username})

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

            db.registrations.insert_one(data_pendaftaran)

            # Pindahkan pengecekan status ke sini
            has_pending_or_approved = db.registrations.count_documents({
                "status": {"$in": ["pending", "approved"]},
                "username": user_data['username']
            }) > 0

            antrian_data = list(db.registrations.find(
                {"status": {"$in": ["pending", "approved"]},
                    "username": user_data['username']},
                {"no_urut": True, "name": True, "nik": True,
                    "tanggal": True, "status": True, "_id": False, "antrian": True}
            ))

            return jsonify({'antrian_data': antrian_data, 'has_pending_or_approved': has_pending_or_approved, 'result': 'success', 'message': 'Pendaftaran berhasil'})
        return jsonify({'result': 'fail', 'message': 'Pendaftaran gagal'})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


@app.route('/api/antrian/check')
def check_antrian():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')

        if username:
            # Ambil data pengguna dari koleksi users
            user_data = db.users.find_one({'username': username})

            if user_data:
                # Pindahkan pengecekan status ke sini
                has_pending_or_approved = db.registrations.count_documents({
                    "status": {"$in": ["pending", "approved"]},
                    "username": user_data['username']
                }) > 0

                return jsonify({'has_pending_or_approved': has_pending_or_approved})
            else:
                return jsonify({'has_pending_or_approved': False})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        pass

    return jsonify({'has_pending_or_approved': False})
# Return Riwayat Pendaftaran Pasien
@app.route('/api/riwayat_pendaftaran', methods=['GET'])
def riwayat_pendaftaran_api():
    token_receive = get_authorization()
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        pendaftaran_data = list(db.registrations.find(
            {'username': username}, {'_id': 0}))
        return jsonify({'riwayat': pendaftaran_data})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'message': 'Your login token has expired'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'message': 'There was an error decoding your token'})


# Return Riwayat Checkup Pasien
@app.route("/api/riwayat_checkup")
def api_riwayat_checkup():
    token_receive = get_authorization()
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})

        data_list_checkup_user = list(db.list_checkup_user.find(
            {'nik': user_info['nik']}, {'_id': False}))
        return jsonify({'data_list_checkup_user': data_list_checkup_user})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'message': 'Your login token has expired'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'message': 'There was an error decoding your token'})


# Return Profile User
@app.route("/api/profile")
def api_profile():
    token_receive = get_authorization()
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload['id']}, {
                                      '_id': False, 'password': False})
        return jsonify({'result': 'success', 'user_info': user_info, 'message': 'Profile fetched successfully'})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'message': 'Your login token has expired'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'message': 'There was an error decoding your token'})


# Handle Edit Profile
@app.route('/api/profile/edit', methods=['POST'])
def edit_profile():
    token_receive = get_authorization()
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

        # Prepare the update document
        doc = {}
        if name:
            doc['name'] = name
        if nik:
            if not is_valid_nik(nik):
                return jsonify({'result': 'fail', 'message': 'NIK harus 16 digit angka'})
            existing_nik = db.users.find_one({'nik': nik})
            if existing_nik and existing_nik['username'] != username:
                return jsonify({'result': 'fail', 'message': 'NIK sudah digunakan'})
            doc['nik'] = nik
        if tgl_lahir:
            if not is_valid_date(tgl_lahir):
                return jsonify({'result': 'fail', 'message': 'Format tanggal lahir tidak valid'})
            if datetime.strptime(tgl_lahir, '%d-%m-%Y') > datetime.now():
                return jsonify({'result': 'fail', 'message': 'Tanggal lahir tidak valid'})
            doc['tgl_lahir'] = tgl_lahir
        if gender:
            if not is_valid_gender(gender):
                return jsonify({'result': 'fail', 'message': 'Jenis kelamin tidak valid'})
            doc['gender'] = gender
        if agama:
            doc['agama'] = agama
        if status:
            doc['status'] = status
        if alamat:
            doc['alamat'] = alamat
        if no_telp:
            if not is_valid_phone_number(no_telp):
                return jsonify({'result': 'fail', 'message': 'Nomor telepon tidak valid'})
            doc['no_telp'] = no_telp

        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file.filename != '':
                filename = secure_filename(file.filename)
                extension = filename.split(".")[-1]
                if extension not in ["jpg", "jpeg", "png"]:
                    return jsonify({'result': 'fail', 'message': 'Profile picture harus berupa file gambar'})
                file_path = f"profile_pics/{username}.{extension}"
                file.save("./static/" + file_path)
                doc["profile_pic"] = file_path

        db.users.update_one({"username": username}, {"$set": doc})

        return jsonify({'result': 'success', 'message': 'Profile updated successfully'})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'message': 'Your login token has expired'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'message': 'There was an error decoding your token'})


# Return Data Pendaftaran Pasien
@app.route("/api/kelola_pendaftaran")
def get_kelola_pendaftaran():
    token_receive = get_authorization()
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')

        if username:
            data = list(db.registrations.find(
                {"status": {"$in": ["pending", "approved", "done"]}},
                {"name": True, "poli": True, "tanggal": True,
                    "keluhan": True, "status": True, "_id": True, "antrian": True}
            ))

            for d in data:
                d['_id'] = str(d['_id'])

            return jsonify({'data': data, 'result': 'success', 'message': 'Data fetched successfully'})

    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'message': 'Your login token has expired'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'message': 'There was an error decoding your token'})


# Handle Kelola Pendaftaran
@app.route('/update_status', methods=['POST'])
def update_status():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')

        if username:
            registration_id = request.form.get('registrationId')
            new_status = request.form.get('status')

            # Pastikan pengguna yang memperbarui status adalah pegawai yang sesuai
            user_data = db.users.find_one(
                {'username': username, 'role': 'pegawai'})
            if user_data:
                allowed_statuses = ["pending", "approved", "rejected", "done"]
                data_pendaftaran = db.registrations.find_one(
                    {"_id": ObjectId(registration_id)})

                if new_status in allowed_statuses:
                    if new_status == "rejected":
                        # Logika untuk menolak pendaftaran (mengubah status menjadi rejected)
                        db.registrations.update_one(
                            {'_id': ObjectId(registration_id)},
                            {'$set': {'status': new_status}}
                        )
                        return jsonify({"message": "Pendaftaran berhasil ditolak"})

                    elif new_status == "approved":
                        # Calculate the antrian based on the number of registrations for the same date and poli
                        antrian = db.registrations.count_documents({
                            "poli": data_pendaftaran["poli"],
                            "tanggal": data_pendaftaran["tanggal"],
                            'status': {'$in': ['approved', 'done']}
                        })

                        # Logika untuk menyetujui pendaftaran (mengubah status menjadi approved)
                        db.registrations.update_one(
                            {'_id': ObjectId(registration_id)},
                            {'$set': {'status': new_status,
                                      'antrian': f"{antrian + 1:03d}"}}
                        )

                        # antrian_data = list(db.registrations.find(
                        #     {"status": {"$in": ["pending", "approved", "done"]}},
                        #     {"name": True, "poli": True, "tanggal": True, "keluhan": True, "status": True, "_id": True}
                        # ))
                        return jsonify({"message": "Pendaftaran berhasil disetujui"})

                    elif new_status == "done":
                        # Logika untuk menyelesaikan pendaftaran (mengubah status menjadi done)
                        db.registrations.update_one(
                            {'_id': ObjectId(registration_id)},
                            {'$set': {'status': new_status}}
                        )

                        db.list_checkup_user.insert_one({
                            'nama': data_pendaftaran['name'],
                            'nik': data_pendaftaran['nik'],
                            'tgl_periksa': data_pendaftaran['tanggal'],
                            'poli': data_pendaftaran['poli'],
                            'keluhan': data_pendaftaran['keluhan']
                        })
                        return jsonify({"message": "Pendaftaran selesai"})

                else:
                    return jsonify({"message": "Status tidak valid"})

        return jsonify({"message": "Gagal memperbarui status formulir"})

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token kedaluwarsa. Silakan login kembali."})
    except jwt.exceptions.DecodeError:
        return jsonify({"message": "Token tidak valid. Silakan login kembali."})


# Return Data Pendaftaran Semua Pasien
@app.route("/api/dashboard_pendaftaran")
def dashboard_pendaftaran():
    token_receive = get_authorization()
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})

        data_list_pendaftaran = list(db.registrations.find({}, {'_id': False}))
        return jsonify({'data_list_pendaftaran': data_list_pendaftaran})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'message': 'Your login token has expired'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'message': 'There was an error decoding your token'})


# Return Data Checkup Semua Pasien
@app.route("/api/dashboard_checkup")
def dashboard_checkup():
    token_receive = get_authorization()
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})

        data_list_checkup = list(db.list_checkup_user.find({}, {'_id': False}))
        return jsonify({'data_list_checkup': data_list_checkup})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'message': 'Your login token has expired'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'message': 'There was an error decoding your token'})


# Return Data Rekam Medis Semua Pasien
@app.route("/api/dashboard_rekam_medis")
def dashboard_rekam_medis():
    token_receive = get_authorization()
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})

        data_list_rekam_medis = list(db.rekam_medis.find({}, {'_id': False}))
        return jsonify({'data_list_rekam_medis': data_list_rekam_medis})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'message': 'Your login token has expired'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'message': 'There was an error decoding your token'})


# Return Data Rekam Medis Semua Pasien
@app.route("/api/rekam_medis")
def api_get_rekam_medis():
    token_receive = get_authorization()
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})
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
        return jsonify({'data_rekam_medis': data_rekam_medis, 'result': 'success', 'message': 'Data fetched successfully'})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'message': 'Your login token has expired'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'message': 'There was an error decoding your token'})


# Handle Buat Rekam Medis
@app.route("/buat_rekam_medis/<nik>", methods=["POST"])
def buat_rekam_medis(nik):
    no_kartu = request.form.get('no')
    dokter = request.form.get('dokter')
    hasil_anamnesa = request.form.get('hasil_anamnesa')
    user_info = db.users.find_one({'nik': nik})
    data_reg = db.registrations.find_one({'nik': nik})
    nama = user_info['name']
    data_rekam_medis = {
        'no_kartu': no_kartu,
        'nama': nama,
        'nik': nik,
        'umur': user_info['tgl_lahir'],
        'alamat': user_info['alamat'],
        'no_telp': user_info['no_telp']
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

    return 'Success'


# Return Data Rekam Medis Berdasarkan NIK
@app.route("/lihat_rekam_medis/<nik>", methods=["GET"])
def lihat_rekam_medis(nik):
    data_rekam_medis = list(db.rekam_medis.find({'nik': nik, "_id": False}))
    list_checkup_user = list(db.list_checkup_user.find({'nik': nik}))
    for user in list_checkup_user:
        user['_id'] = str(user['_id'])
    return jsonify({'data_rekam_medis': data_rekam_medis, 'list_checkup_user': list_checkup_user})


# Handle Edit Rekam Medis
@app.route("/api/get-edit_rekam_medis/<nik>", methods=["GET"])
def get_edit_rekam_medis(nik):
    dokter = request.form.get('dokter')
    hasil_anamnesa = request.form.get('hasil_anamnesa')
    data_list_checkup_user = {
        'dokter': dokter,
        'hasil_anamnesa': hasil_anamnesa
    }
    return jsonify({'data_list_checkup_user': data_list_checkup_user})


# Handle Edit Rekam Medis
@app.route("/api/edit-rekam_medis/<id>", methods=["POST"])
def edit_rekam_medis(id):
    dokter = request.form.get('dokter')
    hasil_anamnesa = request.form.get('hasil_anamnesa')
    data_list_checkup_user = {
        'dokter': dokter,
        'hasil_anamnesa': hasil_anamnesa
    }
    db.list_checkup_user.update_one(
        {'_id': ObjectId(id)}, {'$set': data_list_checkup_user}, upsert=True)
    data_list_checkup_user = db.list_checkup_user.find_one(
        {'_id': ObjectId(id)})
    data_list_checkup_user['_id'] = str(data_list_checkup_user['_id'])
    print(data_list_checkup_user)

    return jsonify({'data_list_checkup_user': data_list_checkup_user})


# Return Semua Jadwal Praktik
@app.route('/api/get_jadwal', methods=['GET'])
def get_jadwal():
    try:
        # Mengambil data jadwal
        jadwal_data = list(db.jadwal.find())
        for jadwal in jadwal_data:
            jadwal["_id"] = str(jadwal["_id"])
        return jsonify({"result": "success", "jadwal": jadwal_data, "message": "Jadwal fetched successfully"})
    except Exception as e:
        return jsonify({"result": "fail", "error": str(e)})


# Return Jadwal Praktik Berdasarkan ID
@app.route("/api/get_jadwal/<id>", methods=["GET"])
def get_jadwal_by_id(id):
    jadwal = db.jadwal.find_one({"_id": ObjectId(id)})
    if not jadwal:
        return jsonify({"result": "fail", "message": "Jadwal not found"})
    jadwal["_id"] = str(jadwal["_id"])

    return jsonify({"result": "success", "jadwal": jadwal, "message": "Jadwal fetched successfully"})


# Handle Tambah Jadwal
@app.route("/api/tambah_jadwal", methods=["POST"])
def api_tambah_jadwal():
    token_receive = get_authorization()
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})
        if user_info['role'] != 'pegawai':
            return jsonify({'result': 'fail', 'message': 'You must login as pegawai'})
        nama = request.form.get("nama")
        poli = request.form.get("poli")
        hari = request.form.getlist("hari")
        jam_buka = request.form.get("jam_buka")
        jam_tutup = request.form.get("jam_tutup")

        if not nama:
            return jsonify({'result': 'fail', 'message': 'Nama tidak boleh kosong'})

        if not poli:
            return jsonify({'result': 'fail', 'message': 'Poli tidak boleh kosong'})

        if not hari:
            return jsonify({'result': 'fail', 'message': 'Hari tidak boleh kosong'})

        if not jam_buka:
            return jsonify({'result': 'fail', 'message': 'Jam buka tidak boleh kosong'})

        if not jam_tutup:
            return jsonify({'result': 'fail', 'message': 'Jam tutup tidak boleh kosong'})

        if not isinstance(hari, list):
            return jsonify({'result': 'fail', 'message': 'Hari harus merupakan list'})

        if any(x for x in hari if x.lower() not in ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu']):
            return jsonify({'result': 'fail', 'message': 'Hari tidak valid'})

        if not is_valid_time(jam_buka):
            return jsonify({'result': 'fail', 'message': 'Format jam buka tidak valid'})

        if not is_valid_time(jam_tutup):
            return jsonify({'result': 'fail', 'message': 'Format jam tutup tidak valid'})

        # Insert jadwal data to MongoDB
        jadwal_data = {
            "nama": nama,
            "poli": poli,
            "hari": hari,
            "jam_buka": jam_buka,
            "jam_tutup": jam_tutup,
        }

        result = db.jadwal.insert_one(jadwal_data)
        jadwal_data["_id"] = str(result.inserted_id)

        return jsonify({"result": "success", "jadwal": jadwal_data, "message": "Jadwal added successfully"})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'message': 'Your login token has expired'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'message': 'There was an error decoding your token'})


# Handle Edit Jadwal
@app.route("/api/edit_jadwal/<id>", methods=["POST"])
def edit_jadwal(id):
    token_receive = get_authorization()
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload.get('id')
        user_info = db.users.find_one({'username': username}, {'_id': False})
        if user_info['role'] != 'pegawai':
            return jsonify({'result': 'fail', 'message': 'You must login as pegawai'})
        nama = request.form.get("nama")
        poli = request.form.get("poli")
        hari = request.form.getlist("hari")
        jam_buka = request.form.get("jam_buka")
        jam_tutup = request.form.get("jam_tutup")

        doc = {}
        if nama:
            doc['nama'] = nama
        if poli:
            doc['poli'] = poli
        if hari:
            if not isinstance(hari, list):
                return jsonify({'result': 'fail', 'message': 'Hari harus merupakan list'})

            if any(x for x in hari if x.lower() not in ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu']):
                return jsonify({'result': 'fail', 'message': 'Hari tidak valid'})
            doc['hari'] = hari
        if jam_buka:
            if not is_valid_time(jam_buka):
                return jsonify({'result': 'fail', 'message': 'Format jam buka tidak valid'})
            doc['jam_buka'] = jam_buka
        if jam_tutup:
            if not is_valid_time(jam_tutup):
                return jsonify({'result': 'fail', 'message': 'Format jam tutup tidak valid'})
            doc['jam_tutup'] = jam_tutup

        # Update jadwal data
        db.jadwal.update_one({"_id": ObjectId(id)}, {"$set": doc})

        jadwal = db.jadwal.find_one({"_id": ObjectId(id)})
        jadwal["_id"] = str(jadwal["_id"])

        return jsonify({"result": "success", "jadwal": jadwal, "message": "Jadwal updated successfully"})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'message': 'Your login token has expired'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'message': 'There was an error decoding your token'})


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


@app.route("/kelola_pendaftaran", methods=["GET"])
def get_pending_and_approved_registrations():
    data = db.registrations.find({'status': {'$in': ['pending', 'approve']}})
    return jsonify(list(data)),


@app.route("/approve_registration/<id>", methods=["PUT"])
def approve_registration(id):
    db.registrations.update_one({'_id': id}, {'$set': {'status': 'approve'}})
    return 'Success',


@app.route("/reject_registration/<id>", methods=["PUT"])
def reject_registration(id):
    db.registrations.update_one({'_id': id}, {'$set': {'status': 'reject'}})
    return 'Success',


@app.route("/done_registration/<nik>", methods=["PUT"])
def process_done_registration(nik):
    db.registrations.update_one({'nik': nik}, {'$set': {'status': 'done'}})
    exist = db.rekam_medis.find_one({'nik': nik})
    if exist:
        data_pendaftaran = db.registrations.find_one(
            {'nik': nik, 'status': 'done'})
        data_rm = db.rekam_medis.find_one({'nik': nik})
        data_list = {
            'nik': data_rm['nik'],
            'tgl_periksa': data_rm['tgl_periksa'],
            'poli': data_rm['poli'],
            'keluhan': data_rm['keluhan']
        }
        db.list_checkup_user.insert_one(data_list)
    else:
        data_pendaftaran = db.registrations.find_one(
            {'nik': nik, 'status': 'done'})

        data_list = {
            'nik': data_pendaftaran['nik'],
            'tgl_periksa': data_pendaftaran('tgl'),
            'poli': data_pendaftaran['poli'],
            'keluhan': data_pendaftaran['keluhan']
        }
        db.list_checkup_user.insert_one(data_list)

    return 'Success',


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
