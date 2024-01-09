import re
import secrets
from flask import Flask, render_template, request, jsonify, send_file, make_response
from pymongo import MongoClient, ASCENDING, DESCENDING
import os
from os.path import join, dirname
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from bson import ObjectId
from flask_bcrypt import Bcrypt
from pagination import *
from exceptions import HttpException, handle_http_exception
from apiresponse import api_response
from utils import *
from middlewares import *
from flask_socketio import SocketIO, Namespace
# import pandas as pd
from io import BytesIO
from flasgger import Swagger, swag_from

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
# Register the error handler
app.errorhandler(HttpException)(handle_http_exception)
bcrypt = Bcrypt(app)
socketio = SocketIO(app)
# Swagger Configuration
app.config['SWAGGER'] = {
    'title': 'Klinik Google',
    'description': 'API documentation for klinik google, API ini menggunakan JWT untuk autentikasi dan otorisasi',
    'version': '1.0.0',
}
Swagger(app)



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


class PendaftaranNamespace(Namespace):
    """
    A namespace for handling pendaftaran events.

    This class extends the `Namespace` class and provides methods for handling
    client connection, disconnection, and new pendaftaran events.

    Attributes:
        None

    Methods:
        on_connect: Called when a client connects to the namespace.
        on_disconnect: Called when a client disconnects from the namespace.
        on_new_pendaftaran: Called when a new pendaftaran event is received.

    """
    def on_connect(self):
        print('Client connected')

    def on_disconnect(self):
        print('Client disconnected')

    def on_new_pendaftaran(self, data):
        self.emit('new_pendaftaran', data)


class AntrianNamespace(Namespace):
    """
    A namespace class for handling antrian events.

    This class extends the `Namespace` class from the `socketio` library.
    It provides methods for handling client connections, disconnections,
    and new antrian events.

    Attributes:
        None

    Methods:
        on_connect: Handles the client connection event.
        on_disconnect: Handles the client disconnection event.
        on_new_antrian: Handles the new antrian event.

    """
    def on_connect(self):
        print('Client connected')

    def on_disconnect(self):
        print('Client disconnected')

    def on_new_antrian(self, data):
        self.emit('new_antrian', data)


class JadwalNamespace(Namespace):
    """
    A namespace class for handling Jadwal events.

    This class extends the `Namespace` class and provides methods for handling
    client connections, disconnections, and new Jadwal events.

    Attributes:
        None

    Methods:
        on_connect: Called when a client connects to the namespace.
        on_disconnect: Called when a client disconnects from the namespace.
        on_new_jadwal: Called when a new Jadwal event is received.

    """

    def on_connect(self):
        print('Client connected')

    def on_disconnect(self):
        print('Client disconnected')

    def on_new_jadwal(self, data):
        self.emit('new_jadwal', data)


# Register the namespace
socketio.on_namespace(PendaftaranNamespace('/pendaftaran'))
socketio.on_namespace(AntrianNamespace('/antrian'))
socketio.on_namespace(JadwalNamespace('/jadwal'))


#################### TEMPLATE ROUTES ####################

# Return Home Page
@app.route('/')
@validate_token_template(SECRET_KEY, TOKEN_KEY, db, allow_guest=True)
def home(decoded_token):
    """
    Renders the home page.

    Args:
        decoded_token (dict): The decoded token containing user information.

    Returns:
        str: The rendered HTML page.

    """
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
    """
    Renders the login page with optional message, JavaScript scripts, and CSS styles.

    Args:
        msg (str): Optional message to display on the login page.
    
    Returns:
        str: Rendered HTML template of the login page.
    """
    msg = request.args.get('msg')
    scripts = ['js/login.js']
    css = ['css/login.css']
    return render_template('pages/login.html', msg=msg, scripts=scripts, css=css)


# Return Register Page
@app.route("/register")
def register():
    """
    Renders the register.html template with the necessary scripts and CSS files.

    Returns:
        The rendered register.html template with the scripts and CSS files.
    """
    scripts = ['js/register.js']
    css = ['css/register.css']
    return render_template("pages/register.html", scripts=scripts, css=css)


# Return Pendaftaran Pasien Page (GET)
@app.route('/pendaftaran')
@validate_token_template(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_template(["pasien"])
def pendaftaran_get(decoded_token):
    """
    Handle GET request for '/pendaftaran' route.

    Args:
        decoded_token (dict): Decoded token containing user information.

    Returns:
        Response: Rendered template 'pages/pendaftaran.html' with user_info and scripts.
    """
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
    """
    This function handles the route '/riwayat_pendaftaran' and is accessible only to authorized 'pasien' role users.
    
    Parameters:
        decoded_token (dict): The decoded token containing user information.
        
    Returns:
        render_template: The rendered HTML template 'pages/riwayat_pendaftaran.html' with user_info and scripts as parameters.
    """
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
    """
    This function handles the '/riwayat_checkup' route.
    It requires a valid token with 'pasien' role to access.
    It retrieves the user's information from the database based on the decoded token.
    Then, it renders the 'riwayat_checkup.html' template with the user's information and necessary scripts.
    """
    scripts = ['js/riwayat_checkup.js']
    user_id = ObjectId(decoded_token.get("uid"))
    user_info = db.users.find_one({"_id": user_id}, {
        '_id': False, 'password': False})
    return render_template("pages/riwayat_checkup.html", user_info=user_info, active_page='riwayat_checkup', scripts=scripts)


# Return Profile Page
@app.route("/profile")
@validate_token_template(SECRET_KEY, TOKEN_KEY, db)
def profile(decoded_token):
    """
    Renders the profile page with user information.

    Args:
        decoded_token (dict): Decoded user token.

    Returns:
        render_template: Rendered profile page with user information.
    """
    scripts = ['js/profile.js']
    css = ['css/profile.css']
    user_id = ObjectId(decoded_token.get("uid"))
    user_info = db.users.find_one({"_id": user_id}, {
        '_id': False, 'password': False})
    if is_valid_date(user_info.get('tgl_lahir')):
        user_info['tgl_lahir'] = datetime.strptime(
            user_info.get('tgl_lahir'), '%d-%m-%Y').strftime('%Y-%m-%d')
    return render_template('pages/profile.html', user_info=user_info, active_page='profile', scripts=scripts, css=css)


# Return Kelola Pendaftaran Page
@app.route("/kelola_pendaftaran")
@validate_token_template(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_template(["pegawai"])
def kelola_pendaftaran(decoded_token):
    """
    Renders the 'kelola_pendaftaran.html' template and passes the user_info and scripts to it.

    Args:
        decoded_token (dict): The decoded token containing user information.

    Returns:
        render_template: The rendered template with user_info and scripts passed as parameters.
    """
    scripts = ['js/kelola_pendaftaran.js']
    user_id = ObjectId(decoded_token.get("uid"))
    user_info = db.users.find_one({"_id": user_id}, {
        '_id': False, 'password': False})

    return render_template('pages/kelola_pendaftaran.html', user_info=user_info, active_page='kelola_pendaftaran', scripts=scripts)


# Return Dashboard Page
@app.route("/dashboard")
@validate_token_template(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_template(["pegawai"])
def dashboard(decoded_token):
    """
    Renders the dashboard page with user information.

    Parameters:
    - decoded_token (dict): Decoded token containing user information.

    Returns:
    - rendered template: The rendered template of the dashboard page.
    """
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
    """
    Retrieves the medical records for a user.

    Parameters:
    - decoded_token (dict): The decoded token containing user information.

    Returns:
    - render_template: The rendered HTML template for displaying the medical records page.
    """
    scripts = ['js/rekam_medis.js']
    user_id = ObjectId(decoded_token.get("uid"))
    user_info = db.users.find_one({"_id": user_id}, {
        '_id': False, 'password': False})

    return render_template("pages/rekam_medis.html", user_info=user_info, active_page='rekam_medis', scripts=scripts)


# Return Kelola Jadwal Page
@app.route('/kelola_praktik')
@validate_token_template(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_template(["pegawai"])
def kelola_praktik(decoded_token):
    """
    Renders the 'kelola_praktik' page with user information and necessary scripts.

    Parameters:
    - decoded_token (dict): Decoded token containing user information.

    Returns:
    - render_template: Rendered HTML template with user information and scripts.
    """
    scripts = ['js/praktik.js']
    user_id = ObjectId(decoded_token.get("uid"))
    user_info = db.users.find_one({"_id": user_id}, {
        '_id': False, 'password': False})
    return render_template('pages/praktik.html', user_info=user_info, active_page='kelola_praktik', scripts=scripts)


#################### API ROUTES ####################

# Handle Register
@app.route("/api/register", methods=["POST"])
@swag_from('swagger_doc/register.yml')
def api_register():
    """
    Handle user registration through the API.

    This endpoint expects a POST request with a JSON payload containing user registration data.
    The data is validated for completeness, uniqueness, and format before storing it in the database.

    Parameters:
        None

    Returns:
        tuple: A tuple containing JSON response and HTTP status code.

    Raises:
        HttpException: If any validation check fails, an HttpException with appropriate
                       status code and error message is raised.
    """
    body = request.is_json
    if not body:
        raise HttpException(False, 415, "failed",
                            "Data harus dalam bentuk JSON")

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
        raise HttpException(False, 400, "failed",
                            "NIK harus terdiri dari 16 digit angka")

    existing_nik = db.users.find_one({'nik': nik})
    if existing_nik:
        raise HttpException(False, 400, "failed", "NIK sudah digunakan")

    # Cek apakah format tanggal lahir valid
    if not is_valid_date(tgl_lahir):
        raise HttpException(
            False, 400, "failed", "Format tanggal lahir tidak valid, gunakan format dd-mm-yyyy")

    # Cek apakah tanggal lahir valid
    if not is_max_date_now(tgl_lahir):
        raise HttpException(False, 400, "failed",
                            "Tanggal lahir tidak boleh lebih dari hari ini")

    # Cek apakah jenis kelamin valid
    if not is_valid_gender(gender):
        raise HttpException(False, 400, "failed", "Jenis kelamin tidak valid")

    # Cek apakah nomor telepon valid
    if not is_valid_phone_number(no_telp):
        raise HttpException(
            False, 400, "failed", "Nomor telepon tidak valid, gunakan format nomor 10 - 13 digit")

    # Cek apakah password sesuai
    if len(password) < 8:
        raise HttpException(False, 400, "failed",
                            "Password harus memiliki minimal 8 karakter")

    if not any(char.isupper() for char in password):
        raise HttpException(False, 400, "failed",
                            "Password harus memiliki minimal 1 huruf kapital")

    if not any(char.isdigit() for char in password):
        raise HttpException(False, 400, "failed",
                            "Password harus memiliki minimal 1 angka")

    if not any(not char.isalnum() for char in password):
        raise HttpException(
            False, 400, "failed", "Password harus memiliki minimal 1 karakter spesial")

    if password != confirm_password:
        raise HttpException(False, 400, "failed",
                            "Password dan konfirmasi password tidak sesuai")

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
    response = api_response(True, 201, "success", "Pendaftaran akun berhasil", {
                            'user_id': str(result.inserted_id), 'username': username})
    return jsonify(response.__dict__), 201


# Handle Login
@app.route("/api/login", methods=["POST"])
@swag_from('swagger_doc/login.yml')
def sign_in():
    """
    Endpoint for user authentication.

    This endpoint handles user login through a POST request to '/api/login'.
    The request should include a JSON body with 'username' and 'password' fields.

    :raises HttpException 415: If the request data is not in JSON format.
    :raises HttpException 400: If 'username' or 'password' is missing, or if the provided
                              credentials are incorrect.

    :return: A JSON response with a success message and a JWT token upon successful login.
    :rtype: Response
    """
    body = request.is_json
    if body:
        raise HttpException(False, 415, "failed",
                            "Data harus dalam bentuk form data")
    # Sign in
    username_receive = request.form.get("username")
    password_receive = request.form.get("password")

    if not username_receive:
        raise HttpException(False, 400, "failed",
                            "Username tidak boleh kosong")
    if not password_receive:
        raise HttpException(False, 400, "failed",
                            "Password tidak boleh kosong")

    user = db.users.find_one({"username": username_receive})
    if not user:
        raise HttpException(False, 400, "failed", "Username / password salah")

    # Use bcrypt to verify the password with the stored salt
    check_password = bcrypt.check_password_hash(
        user.get('password'), user.get('salt') + password_receive + user.get('salt'))
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

    response = api_response(True, 200, "success",
                            "Login berhasil", {TOKEN_KEY: token})
    response_data = make_response(jsonify(response.__dict__))
    response_data.headers.add(
        "Set-Cookie", f"{TOKEN_KEY}={token}; HttpOnly; Secure; Max-Age={60 * 60 * 24}; Path=/")
    return response_data


# Handle Logout
@app.route("/api/logout", methods=["POST"])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@swag_from('swagger_doc/logout.yml')
def logout(decoded_token):
    """
    Logs out a user by invalidating the session identified by the decoded token.

    This endpoint is accessible via a POST request to "/api/logout" and requires a valid access token.
    
    Args:
        decoded_token (dict): The decoded JWT token containing user information.

    Returns:
        flask.Response: A JSON response indicating the success of the logout operation.
            The response includes a message, status code, and relevant data.
    """
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
@swag_from('swagger_doc/pendaftaran.yml')
def api_pendaftaran(decoded_token):
    """
    Handle API requests for registration data.

    Parameters:
    - decoded_token (dict): Decoded token containing user information.

    Returns:
    - Flask Response: JSON response containing registration data or error message.

    This function is a Flask route handling API requests for registration data. It expects
    the following query parameters:
    - 'name': Filter registrations by name.
    - 'poli': Filter registrations by poli.
    - 'tanggal': Filter registrations by tanggal.
    - 'status_filter': Filter registrations by status.

    The function supports DataTables pagination parameters:
    - 'draw': Sequence number for the DataTables request.
    - 'start': Starting index for paginated results.
    - 'length': Number of records to fetch for paginated results.

    Additionally, the function supports searching, sorting, and filtering based on the DataTables request.

    The API response includes a JSON object with the following fields:
    - 'success' (bool): Indicates whether the request was successful.
    - 'code' (int): HTTP status code.
    - 'message' (str): Description of the response.
    - 'data' (list): List of registration data.
    - 'pagination' (dict): Meta pagination information.
    - 'datatables_pagination' (dict): DataTables pagination information.

    The function is decorated with route, token validation, role authorization, and Swagger documentation.
    """
    name = request.args.get('name')
    poli = request.args.get('poli')
    tanggal = request.args.get('tanggal')
    status_filter = request.args.getlist('status_filter')

    # Get parameters from DataTables request
    draw = request.args.get('draw')
    if draw:
        draw = int(draw)
    start = request.args.get('start')
    if start:
        start = int(start)
    length = request.args.get('length')
    if length:
        length = int(length)
    search_value = request.args.get('search[value]')
    status = request.args.getlist('status')
    order_column_index = int(request.args.get('order[0][column]', 0))
    order_direction = request.args.get('order[0][dir]')
    # Adjust the query for sorting
    if status:
        sort_column = ["antrian", "name", "poli", "tanggal",
                       "keluhan", "status"][order_column_index]
    else:
        sort_column = ["antrian", "name", "poli",
                       "tanggal", "status"][order_column_index]

    # Get parameters for your own pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    search = request.args.get('search')
    order = request.args.get('order')
    sort = request.args.get('sort', 'asc')

    if name == 'name' and status:
        list_nama = list(db.registrations.distinct(
            'name', {'status': {'$in': status}}))

        sorted_list_nama = sorted(list_nama, key=lambda x: x.lower())
        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_nama)
        return jsonify(response.__dict__)
    if name == 'name' and not status:
        list_nama = list(db.registrations.distinct('name'))
        sorted_list_nama = sorted(list_nama, key=lambda x: x.lower())
        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_nama)
        return jsonify(response.__dict__)
    if poli == 'poli' and status:
        list_poli = list(db.registrations.distinct(
            'poli', {'status': {'$in': status}}))
        sorted_list_poli = sorted(list_poli, key=lambda x: x.lower())
        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_poli)
        return jsonify(response.__dict__)
    if poli == 'poli' and not status:
        list_poli = list(db.registrations.distinct('poli'))
        sorted_list_poli = sorted(list_poli, key=lambda x: x.lower())
        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_poli)
        return jsonify(response.__dict__)
    if tanggal == 'tanggal' and status:
        list_tanggal = list(db.registrations.distinct(
            'tanggal', {'status': {'$in': status}}))
        sorted_list_tanggal = sorted(list_tanggal)
        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_tanggal)
        return jsonify(response.__dict__)
    if tanggal == 'tanggal' and not status:
        list_tanggal = list(db.registrations.distinct('tanggal'))
        sorted_list_tanggal = sorted(list_tanggal)
        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_tanggal)
        return jsonify(response.__dict__)

    # Define regex pattern for matching variations of "Approve"
    approve_pattern = re.compile(
        r'^a(p(p(r(o(v(e?)?)?)?)?)?)?$', re.IGNORECASE)
    reject_pattern = re.compile(r'^r(e(j(e(c(t?)?)?)?)?)?$', re.IGNORECASE)
    done_pattern = re.compile(r'^d(o(n(e?)?)?)?$', re.IGNORECASE)

    # Decide whether to use DataTables pagination or your own pagination
    if not draw:
        start = page - 1
        length = limit
        search_value = search
        sort_column = order
        order_direction = sort

    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING
    collation = {'locale': 'en', 'strength': 2}

    # MongoDB query with search
    query = {}
    if name:
        query['name'] = name
    if poli:
        query['poli'] = poli
    if tanggal:
        query['tanggal'] = tanggal
    if status_filter:
        status = status_filter
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

    if sort_column:
        data = list(db.registrations.find(query).sort(
            sort_column, sort_direction).collation(collation).skip(start).limit(length))
    else:
        data = list(db.registrations.find(query).collation(
            collation).skip(start).limit(length))

    for d in data:
        d['_id'] = str(d['_id'])

    # Total records count (unfiltered)
    total_records = db.registrations.count_documents({})

    if draw and status:
        total_records = db.registrations.count_documents({
            "status": {"$in": status}
        })

    # Total records count after filtering
    filtered_records = db.registrations.count_documents(query)

    total_pages = (filtered_records + length -
                   1) // length  # Calculate total pages

    # Create the meta pagination object
    pagination = Pagination(start+1, length, total_pages, filtered_records)

    # Create datatables pagination object
    datatables_pagination = DatatablesPagination(
        total_records, filtered_records, draw, start, length)

    # return jsonify(response.__dict__)
    response = api_response(True, 200, "success", "Data fetched successfully",
                            data, pagination.__dict__, datatables_pagination.__dict__)

    return jsonify(response.__dict__)


# Pendaftaran Pasien (POST)
@app.route('/api/pendaftaran', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pasien"])
@swag_from('swagger_doc/pendaftaran_post.yml')
def pendaftaran_post(decoded_token):
    """
    Handle the POST request for patient registration.

    This endpoint allows authorized users with the role "pasien" to submit
    a registration form for a medical appointment. The function validates the
    incoming request, checks the user's information, and ensures that the
    registration data meets the required criteria before storing it in MongoDB.

    Args:
        decoded_token (dict): Decoded user token containing user information.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.

    Raises:
        HttpException: An exception with specific details in case of validation errors.
    """
    body = request.is_json
    if body:
        raise HttpException(False, 415, "failed",
                            "Data harus dalam bentuk form data")

    user_id = ObjectId(decoded_token.get("uid"))
    # Ambil data pengguna dari koleksi users
    user_data = db.users.find_one({"_id": user_id}, {
        '_id': False, 'password': False})
    if not user_data:
        raise HttpException(False, 400, "failed",
                            "Data pengguna tidak ditemukan")

    poli = request.form.get('poli')
    # get all poli from collection jadwal in a list
    poli_list = list(db.jadwal.distinct('poli'))
    if not poli:
        raise HttpException(False, 400, "failed", "Poli tidak boleh kosong")
    if poli not in poli_list:
        raise HttpException(
            False, 400, "failed", f"Poli {poli} tidak tersedia, pilih dari {poli_list}")
    tanggal = request.form.get('tanggal')
    if not tanggal:
        raise HttpException(False, 400, "failed", "Tanggal tidak boleh kosong")
    if not is_valid_date(tanggal):
        raise HttpException(
            False, 400, "failed", "Format tanggal tidak valid, gunakan format dd-mm-yyyy")
    if not is_min_date_now(tanggal):
        raise HttpException(False, 400, "failed",
                            "Tanggal tidak boleh kurang dari hari ini")
    keluhan = request.form.get('keluhan')
    if not keluhan:
        raise HttpException(False, 400, "failed", "Keluhan tidak boleh kosong")
    has_pending_registration = bool(db.registrations.count_documents({
        "status": {"$in": ["pending"]},
        "username": user_data.get('username')
    }) > 0)
    if has_pending_registration:
        raise HttpException(
            False, 400, "failed", "Anda sudah memiliki pendaftaran yang sedang diproses")
    has_approved_registration = bool(db.registrations.count_documents({
        "status": {"$in": ["approved"]},
        "username": user_data.get('username')
    }) > 0)
    if has_approved_registration:
        raise HttpException(False, 400, "failed",
                            "Anda sudah memiliki pendaftaran yang disetujui")

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
    socketio.emit('new_pendaftaran', data_pendaftaran,
                  namespace='/pendaftaran')
    response = api_response(
        True, 201, "success", "Formulir telah diproses. Silakan tunggu.", data_pendaftaran)
    return jsonify(response.__dict__), 201


# Return Riwayat Pendaftaran Pasien
@app.route('/api/pendaftaran/me')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pasien"])
@swag_from('swagger_doc/pendaftaran_me.yml')
def riwayat_pendaftaran_api(decoded_token):
    """
    API endpoint to retrieve registration history for a user.

    This endpoint requires authentication using a valid token and specific roles.

    Parameters:
    - decoded_token (dict): The decoded user token containing user information.

    Returns:
    - Flask Response: JSON response containing registration history data.

    Raises:
    - HttpException: If user data is not found or there is an issue with the request.
    """
    user_id = ObjectId(decoded_token.get("uid"))
    user_data = db.users.find_one({"_id": user_id}, {
        '_id': False, 'password': False})
    username = user_data.get('username')

    # Get parameters from DataTables request
    draw = request.args.get('draw')
    if draw:
        draw = int(draw)
    start = request.args.get('start')
    if start:
        start = int(start)
    length = request.args.get('length')
    if length:
        length = int(length)
    search_value = request.args.get('search[value]')
    order_column_index = int(request.args.get('order[0][column]', 0))
    order_direction = request.args.get('order[0][dir]')
    # Adjust the query for sorting
    sort_column = ["_id", "name", "nik", "poli",
                   "tanggal", "status"][order_column_index]

    if not user_data:
        raise HttpException(False, 400, "failed",
                            "Data pengguna tidak ditemukan")

    # Get parameters for your own pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    search = request.args.get('search')
    order = request.args.get('order')
    sort = request.args.get('sort', 'asc')

    # Decide whether to use DataTables pagination or your own pagination
    if not draw:
        start = page - 1
        length = limit
        search_value = search
        sort_column = order
        order_direction = sort

    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING
    collation = {'locale': 'en', 'strength': 2}

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

    if sort_column:
        data = list(db.registrations.find(query).sort(
            sort_column, sort_direction).collation(collation).skip(start).limit(length))
    else:
        data = list(db.registrations.find(query).collation(
            collation).skip(start).limit(length))

    for d in data:
        d['_id'] = str(d['_id'])

    # Total records count (unfiltered)
    total_records = db.registrations.count_documents({'username': username})

    # Total records count after filtering
    filtered_records = db.registrations.count_documents(query)

    total_pages = (filtered_records + length -
                   1) // length  # Calculate total pages
    # Create the meta pagination object
    pagination = Pagination(start+1, length, total_pages, filtered_records)

    # Create datatables pagination object
    datatables_pagination = DatatablesPagination(
        total_records, filtered_records, draw, start, length)

    response = api_response(True, 200, "success", "Data berhasil diambil", data,
                            pagination.__dict__, datatables_pagination.__dict__)
    return jsonify(response.__dict__)


@app.route('/api/pendaftaran/<id>/approve', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
@swag_from('swagger_doc/pendaftaran_approve.yml')
def approve_pendaftaran(decoded_token, id):
    """
    Approve a registration based on the provided ID.

    Parameters:
    - decoded_token (dict): Decoded token containing user information.
    - id (str): The ID of the registration to be approved.

    Raises:
    - HttpException: If the ID is undefined, not valid, or if the registration is not found,
      already approved, done, rejected, expired, or canceled.

    Returns:
    - jsonify: JSON response indicating the success of the approval process.
    """
    if id == 'undefined':
        raise HttpException(False, 400, "failed", "ID tidak boleh kosong")

    if not ObjectId.is_valid(id):
        raise HttpException(False, 400, "failed", "ID tidak valid")

    data_pendaftaran = db.registrations.find_one(
        {"_id": ObjectId(id)})
    if not data_pendaftaran:
        raise HttpException(False, 400, "failed",
                            "Pendaftaran tidak ditemukan")
    if data_pendaftaran.get('status') == 'approved':
        raise HttpException(False, 400, "failed",
                            "Pendaftaran sudah disetujui")

    if data_pendaftaran.get('status') == 'done':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah selesai")

    if data_pendaftaran.get('status') == 'rejected':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah ditolak")

    if data_pendaftaran.get('status') == 'expired':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah expired")

    if data_pendaftaran.get('status') == 'canceled':
        raise HttpException(False, 400, "failed",
                            "Pendaftaran sudah dibatalkan")

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

    socketio.emit('new_antrian', get_antrian_today(db), namespace='/antrian')

    response = api_response(True, 200, "success",
                            "Pendaftaran berhasil disetujui")
    return jsonify(response.__dict__)


@app.route('/api/pendaftaran/<id>/reject', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
@swag_from('swagger_doc/pendaftaran_reject.yml')
def reject_pendaftaran(decoded_token, id):
    """
    Rejects a registration based on the provided ID.

    Parameters:
    - decoded_token (dict): Decoded API token containing user information.
    - id (str): Registration ID to be rejected.

    Returns:
    - Flask Response: JSON response indicating the success or failure of the rejection.

    Raises:
    - HttpException: If validation or rejection fails, an HTTP exception is raised with
      the appropriate status code and error message.
    """
    if id == 'undefined':
        raise HttpException(False, 400, "failed", "ID tidak boleh kosong")

    if not ObjectId.is_valid(id):
        raise HttpException(False, 400, "failed", "ID tidak valid")

    data_pendaftaran = db.registrations.find_one(
        {"_id": ObjectId(id)})

    if not data_pendaftaran:
        raise HttpException(False, 400, "failed",
                            "Pendaftaran tidak ditemukan")

    if data_pendaftaran.get('status') == 'approved':
        raise HttpException(False, 400, "failed",
                            "Pendaftaran sudah disetujui")

    if data_pendaftaran.get('status') == 'done':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah selesai")

    if data_pendaftaran.get('status') == 'rejected':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah ditolak")

    if data_pendaftaran.get('status') == 'expired':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah expired")

    if data_pendaftaran.get('status') == 'canceled':
        raise HttpException(False, 400, "failed",
                            "Pendaftaran sudah dibatalkan")

    # Logika untuk menolak pendaftaran (mengubah status menjadi rejected)
    db.registrations.update_one(
        {'_id': ObjectId(id)},
        {'$set': {'status': 'rejected'}}
    )

    response = api_response(True, 200, "success",
                            "Pendaftaran berhasil ditolak")
    return jsonify(response.__dict__)


@app.route('/api/pendaftaran/<id>/done', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
@swag_from('swagger_doc/pendaftaran_done.yml')
def done_pendaftaran(decoded_token, id):
    """
    Complete the registration process for a user with the specified ID.

    This endpoint is used to finalize the registration process for a user
    by updating the registration status to 'done'. Only authorized personnel
    with the role 'pegawai' can access this endpoint.

    Args:
        decoded_token (dict): The decoded JWT token containing user information.
        id (str): The unique identifier for the registration.

    Raises:
        HttpException: If the provided ID is empty ('undefined'), not valid,
                       or if the registration is not found, pending, done,
                       rejected, expired, or canceled.

    Returns:
        Response: A JSON response indicating the success of the registration
                  completion process.
    """
    if id == 'undefined':
        raise HttpException(False, 400, "failed", "ID tidak boleh kosong")

    if not ObjectId.is_valid(id):
        raise HttpException(False, 400, "failed", "ID tidak valid")

    data_pendaftaran = db.registrations.find_one(
        {"_id": ObjectId(id)})

    if not data_pendaftaran:
        raise HttpException(False, 400, "failed",
                            "Pendaftaran tidak ditemukan")

    if data_pendaftaran.get('status') == 'pending':
        raise HttpException(False, 400, "failed", "Pendaftaran masih diproses")

    if data_pendaftaran.get('status') == 'done':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah selesai")

    if data_pendaftaran.get('status') == 'rejected':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah ditolak")

    if data_pendaftaran.get('status') == 'expired':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah expired")

    if data_pendaftaran.get('status') == 'canceled':
        raise HttpException(False, 400, "failed",
                            "Pendaftaran sudah dibatalkan")

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

    socketio.emit('new_antrian', get_antrian_today(db), namespace='/antrian')

    response = api_response(True, 200, "success", "Pendaftaran selesai")
    return jsonify(response.__dict__)


@app.route('/api/pendaftaran/<id>/cancel', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pasien"])
@swag_from('swagger_doc/pendaftaran_cancel.yml')
def cancel_pendaftaran(decoded_token, id):
    """
    Cancel a registration by changing its status to 'canceled'.

    Args:
        decoded_token (str): The decoded token of the user.
        id (str): The ID of the registration to be canceled.

    Raises:
        HttpException: If the ID is empty, invalid, or the registration is not found,
            already done, rejected, expired, or canceled.

    Returns:
        dict: A JSON response indicating the success of the cancellation.
    """
    if id == 'undefined':
        raise HttpException(False, 400, "failed", "ID tidak boleh kosong")

    if not ObjectId.is_valid(id):
        raise HttpException(False, 400, "failed", "ID tidak valid")

    data_pendaftaran = db.registrations.find_one(
        {"_id": ObjectId(id)})

    if not data_pendaftaran:
        raise HttpException(False, 400, "failed",
                            "Pendaftaran tidak ditemukan")

    if data_pendaftaran.get('status') == 'done':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah selesai")

    if data_pendaftaran.get('status') == 'rejected':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah ditolak")

    if data_pendaftaran.get('status') == 'expired':
        raise HttpException(False, 400, "failed", "Pendaftaran sudah expired")

    if data_pendaftaran.get('status') == 'canceled':
        raise HttpException(False, 400, "failed",
                            "Pendaftaran sudah dibatalkan")

    # Logika untuk membatalkan pendaftaran (mengubah status menjadi canceled)
    db.registrations.update_one(
        {'_id': ObjectId(id)},
        {'$set': {'status': 'canceled'}}
    )

    data_pendaftaran["_id"] = str(data_pendaftaran["_id"])

    socketio.emit('new_pendaftaran', data_pendaftaran,
                  namespace='/pendaftaran')

    response = api_response(True, 200, "success", "Pendaftaran dibatalkan")
    return jsonify(response.__dict__)


@app.route('/api/pendaftaran/expire', methods=['POST'])
@swag_from('swagger_doc/pendaftaran_expire.yml')
def expire_pendaftaran():
    """
    Expire pendaftaran by updating the status of pending and approved registrations
    that have a tanggal (date) earlier than today's date to "expired".
    Emit a socketio event to notify clients about the change.
    Return a JSON response indicating the success of the operation.

    :return: JSON response
    """
    now = datetime.now()
    today = {'$dateFromString': {
        'dateString': now.strftime("%d-%m-%Y"), 'format': '%d-%m-%Y'}}
    # check if now is midnight
    if now.hour != 0 and now.minute != 0 and now.second != 0:
        raise HttpException(
            False, 400, "failed", "Pendaftaran tidak berhasil diubah, ini bukan waktu tengah malam")

    db.registrations.update_many(
        {
            "$and": [
                {"status": {"$in": ["pending", "approved"]}},
                {"$expr": {"$lt": [{"$dateFromString": {
                    "dateString": "$tanggal", "format": "%d-%m-%Y"}}, today]}}
            ]
        },
        {"$set": {"status": "expired"}}
    )

    socketio.emit('new_pendaftaran', {"data": "data"},
                  namespace='/pendaftaran')

    response = api_response(True, 200, "success",
                            "Pendaftaran berhasil diubah")
    return jsonify(response.__dict__)


# @app.route('/api/pendaftaran/export')
# @validate_token_api(SECRET_KEY, TOKEN_KEY, db)
# @authorized_roles_api(["pegawai"])
# @swag_from('swagger_doc/pendaftaran_export.yml')
# def export_pendaftaran(decoded_token):
#     """
#     Export pendaftaran data within a specified date range as a CSV file.

#     Parameters:
#     - decoded_token (dict): Decoded token containing user information.

#     Returns:
#     - Response: CSV file as a response with a dynamic file name.
#     """
#     user_id = ObjectId(decoded_token.get("uid"))
#     username = db.users.find_one({"_id": user_id}).get('username')
#     # Get startdate and enddate from query parameters
#     startdate_str = request.args.get('startdate')
#     enddate_str = request.args.get('enddate')

#     if not startdate_str:
#         raise HttpException(False, 400, "failed",
#                             "startdate tidak boleh kosong")

#     if not enddate_str:
#         raise HttpException(False, 400, "failed",
#                             "enddate tidak boleh kosong")

#     if not is_valid_date(startdate_str):
#         raise HttpException(False, 400, "failed",
#                             "Format tanggal tidak valid, gunakan format dd-mm-yyyy")
#     if not is_valid_date(enddate_str):
#         raise HttpException(False, 400, "failed",
#                             "Format tanggal tidak valid, gunakan format dd-mm-yyyy")

#     if parse_date(enddate_str) < parse_date(startdate_str):
#         raise HttpException(False, 400, "failed",
#                             "startdate harus lebih kecil dibanding enddate")

#     # Parse startdate and enddate to datetime objects
#     startdate_iso = {'$dateFromString': {
#         'dateString': startdate_str, 'format': '%d-%m-%Y'}}
#     enddate_iso = {'$dateFromString': {
#         'dateString': enddate_str, 'format': '%d-%m-%Y'}}

#     # Query registrations within the specified date range
#     registrations = db.registrations.find({
#         "$expr": {
#             "$and": [
#                 {"$gte": [{"$dateFromString": {
#                     "dateString": "$tanggal", "format": "%d-%m-%Y"}}, startdate_iso]},
#                 {"$lte": [{"$dateFromString": {
#                     "dateString": "$tanggal", "format": "%d-%m-%Y"}}, enddate_iso]}
#             ]
#         }
#     }, {"_id": False})

#     # Convert MongoDB cursor to a list of dictionaries
#     registrations_list = list(registrations)

#     # Create a DataFrame from the list
#     df = pd.DataFrame(registrations_list)

#     # Create a custom header
#     custom = pd.DataFrame({
#         'Username': df['username'] if len(registrations_list) > 0 else [''],
#         'Nama': df['name'] if len(registrations_list) > 0 else [''],
#         'NIK': df['nik'] if len(registrations_list) > 0 else [''],
#         'Tanggal Lahir': df['tgl_lahir'] if len(registrations_list) > 0 else [''],
#         'Jenis Kelamin': df['gender'] if len(registrations_list) > 0 else [''],
#         'Agama': df['agama'] if len(registrations_list) > 0 else [''],
#         'Status Pernikahan': df['status_pernikahan'] if len(registrations_list) > 0 else [''],
#         'Alamat': df['alamat'] if len(registrations_list) > 0 else [''],
#         'No Telp': df['no_telp'] if len(registrations_list) > 0 else [''],
#         'Tanggal Periksa': df['tanggal'] if len(registrations_list) > 0 else [''],
#         'Keluhan': df['keluhan'] if len(registrations_list) > 0 else [''],
#         'Poli': df['poli'] if len(registrations_list) > 0 else [''],
#         'Status Pendaftaran': df['status'] if len(registrations_list) > 0 else [''],
#         'No Antrian': df['antrian'] if len(registrations_list) > 0 else ['']
#     })

#     # Convert DataFrame to CSV format
#     output = BytesIO()
#     custom.to_csv(output, index=False, encoding='utf-8')
#     output.seek(0)

#     filename = f"pendaftaran-{username}-{startdate_str}-{enddate_str}.csv"

#     # Return CSV file as a response with a dynamic file name
#     return send_file(output, as_attachment=True, download_name=filename, mimetype='text/csv')


# Return Atrian Hari Ini
@app.route('/api/antrian/today')
@swag_from('swagger_doc/antrian_today.yml')
def get_antrian():
    """
    Get today's queue data.

    Returns:
        JSON: The response containing the queue data.
    """
    antrian_data = get_antrian_today(db)
    response = api_response(True, 200, "success",
                            "Antrian berhasil diambil", antrian_data)
    return jsonify(response.__dict__)


# Return Antrian Pasien
@app.route('/api/antrian/me')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pasien"])
@swag_from('swagger_doc/antrian_me.yml')
def get_antrian_data(decoded_token):
    """
    Get the queue data for the authenticated user.

    Parameters:
    - decoded_token (dict): Decoded token containing user information.

    Returns:
    - dict: Response containing the queue data for the user.
    """
    user_id = ObjectId(decoded_token.get("uid"))
    user_data = db.users.find_one({"_id": user_id}, {
        '_id': False, 'password': False})
    if not user_data:
        raise HttpException(False, 400, "failed",
                            "Data pengguna tidak ditemukan")

    antrian_data = list(db.registrations.find(
        {
            "username": user_data.get('username'),
            "status": {"$in": ["pending", "approved"]}
        }
    ))
    for antrian in antrian_data:
        antrian["_id"] = str(antrian["_id"])

    response = api_response(True, 200, "success",
                            "Data berhasil diambil", antrian_data)

    return jsonify(response.__dict__)


@app.route('/api/antrian/check')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pasien"])
@swag_from('swagger_doc/antrian_check.yml')
def check_antrian(decoded_token):
    """
    Check the queue status for a user.

    Parameters:
    - decoded_token (dict): Decoded user token.

    Returns:
    - JSON response: Response containing the queue status for the user.
    """
    user_id = ObjectId(decoded_token.get("uid"))
    user_data = db.users.find_one({"_id": user_id}, {
        '_id': False, 'password': False})
    if not user_data:
        raise HttpException(False, 400, "failed",
                            "Data pengguna tidak ditemukan")

    has_pending_or_approved = bool(db.registrations.count_documents({
        "status": {"$in": ["pending", "approved"]},
        "username": user_data.get('username')
    }) > 0)

    response = api_response(True, 200, "success", "Data berhasil dimabil", {
                            'has_pending_or_approved': has_pending_or_approved})
    return jsonify(response.__dict__)


# Return Riwayat Checkup Pasien
@app.route("/api/checkup/me")
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pasien"])
@swag_from('swagger_doc/checkup_me.yml')
def api_riwayat_checkup(decoded_token):
    """
    API endpoint to retrieve the checkup history of a user.

    Args:
        decoded_token (dict): Decoded token containing user information.

    Returns:
        dict: JSON response containing the checkup history data.

    Raises:
        HttpException: If user data is not found.
    """
    user_id = ObjectId(decoded_token.get("uid"))
    user_data = db.users.find_one({"_id": user_id}, {
        '_id': False, 'password': False})
    if not user_data:
        raise HttpException(False, 400, "failed",
                            "Data pengguna tidak ditemukan")
    nik = user_data.get('nik')
    # Get parameters from DataTables request
    draw = request.args.get('draw')
    if draw:
        draw = int(draw)
    start = request.args.get('start')
    if start:
        start = int(start)
    length = request.args.get('length')
    if length:
        length = int(length)
    search_value = request.args.get('search[value]')
    order_column_index = int(request.args.get('order[0][column]', 0))
    order_direction = request.args.get('order[0][dir]', 'asc')
    # Adjust the query for sorting
    sort_column = ["_id", "tgl_periksa", "poli", "dokter",
                   "keluhan", "hasil_anamnesa"][order_column_index]

    if not user_data:
        raise HttpException(False, 400, "failed",
                            "Data pengguna tidak ditemukan")

    # Get parameters for your own pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    search = request.args.get('search')
    order = request.args.get('order')
    sort = request.args.get('sort', 'asc')

    # Decide whether to use DataTables pagination or your own pagination
    if not draw:
        start = page - 1
        length = limit
        search_value = search
        sort_column = order
        order_direction = sort

    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING
    collation = {'locale': 'en', 'strength': 2}

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

    if sort_column:
        data = list(db.list_checkup_user.find(query).sort(
            sort_column, sort_direction).collation(collation).skip(start).limit(length))
    else:
        data = list(db.list_checkup_user.find(query).collation(
            collation).skip(start).limit(length))

    for d in data:
        d['_id'] = str(d['_id'])

    # Total records count (unfiltered)
    total_records = db.list_checkup_user.count_documents({'nik': nik})

    # Total records count after filtering
    filtered_records = db.list_checkup_user.count_documents(query)

    total_pages = (filtered_records + length -
                   1) // length  # Calculate total pages
    # Create the meta pagination object
    pagination = Pagination(start+1, length, total_pages, filtered_records)

    # Create datatables pagination object
    datatables_pagination = DatatablesPagination(
        total_records, filtered_records, draw, start, length)

    response = api_response(True, 200, "success", "Data berhasil diambil", data,
                            pagination.__dict__, datatables_pagination.__dict__)
    return jsonify(response.__dict__)


@app.route("/api/checkup")
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
@swag_from('swagger_doc/checkup.yml')
def api_riwayat_checkup_pegawai(decoded_token):
    name = request.args.get('name')
    dokter = request.args.get('dokter')
    poli = request.args.get('poli')
    tanggal = request.args.get('tanggal')
    # Get parameters from DataTables request
    draw = request.args.get('draw')
    if draw:
        draw = int(draw)
    start = request.args.get('start')
    if start:
        start = int(start)
    length = request.args.get('length')
    if length:
        length = int(length)
    search_value = request.args.get('search[value]', '')
    order_column_index = int(request.args.get('order[0][column]', 0))
    order_direction = request.args.get('order[0][dir]')
    sort_column = ["_id", "tgl_periksa", "nama", "dokter",
                   "poli", "keluhan", "hasil_anamnesa"][order_column_index]

    # Get parameters for your own pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    search = request.args.get('search')
    order = request.args.get('order')
    sort = request.args.get('sort', 'asc')

    if name == 'name':
        list_nama = list(db.list_checkup_user.distinct('nama'))

        sorted_list_nama = sorted(list_nama, key=lambda x: x.lower())
        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_nama)
        return jsonify(response.__dict__)
    if dokter == 'dokter':
        list_dokter = list(db.list_checkup_user.distinct('dokter'))
        sorted_list_dokter = sorted(list_dokter, key=lambda x: x.lower())
        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_dokter)
        return jsonify(response.__dict__)
    if poli == 'poli':
        list_poli = list(db.list_checkup_user.distinct('poli'))
        sorted_list_poli = sorted(list_poli, key=lambda x: x.lower())
        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_poli)
        return jsonify(response.__dict__)
    if tanggal == 'tanggal':
        list_tanggal = list(db.list_checkup_user.distinct('tgl_periksa'))
        sorted_list_tanggal = sorted(list_tanggal)
        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_tanggal)
        return jsonify(response.__dict__)

    # Decide whether to use DataTables pagination or your own pagination
    if not draw:
        start = page - 1
        length = limit
        search_value = search
        sort_column = order
        order_direction = sort

    # Adjust the query for sorting

    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING
    collation = {'locale': 'en', 'strength': 2}

    # MongoDB query with search
    query = {}
    if name:
        query['nama'] = name
    if dokter:
        query['dokter'] = dokter
    if poli:
        query['poli'] = poli
    if tanggal:
        query['tgl_periksa'] = tanggal
    if search_value:
        query["$or"] = [
            {"tgl_periksa": {"$regex": search_value, "$options": "i"}},
            {"poli": {"$regex": search_value, "$options": "i"}},
            {"nama": {"$regex": search_value, "$options": "i"}},
            {"dokter": {"$regex": search_value, "$options": "i"}},
            {"keluhan": {"$regex": search_value, "$options": "i"}},
            {"hasil_anamnesa": {"$regex": search_value, "$options": "i"}},
        ]

    if sort_column:
        data = list(db.list_checkup_user.find(query).sort(
            sort_column, sort_direction).collation(collation).skip(start).limit(length))
    else:
        data = list(db.list_checkup_user.find(query).collation(
            collation).skip(start).limit(length))

    for d in data:
        d['_id'] = str(d['_id'])

    # Total records count (unfiltered)
    total_records = db.list_checkup_user.count_documents({})

    # Total records count after filtering
    filtered_records = db.list_checkup_user.count_documents(query)

    total_pages = (filtered_records + length -
                   1) // length  # Calculate total pages
    # Create the meta pagination object
    pagination = Pagination(start+1, length, total_pages, filtered_records)

    # Create datatables pagination object
    datatables_pagination = DatatablesPagination(
        total_records, filtered_records, draw, start, length)

    response = api_response(True, 200, "success", "Data berhasil diambil",
                            data, pagination.__dict__, datatables_pagination.__dict__)
    return jsonify(response.__dict__)


@app.route("/api/checkup/<nik>")
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
@swag_from('swagger_doc/checkup_nik.yml')
def api_pasien_checkup(decoded_token, nik):
    if nik == 'undefined':
        raise HttpException(False, 400, "failed", "NIK tidak boleh kosong")
    if not is_valid_nik(nik):
        raise HttpException(False, 400, "failed", "NIK tidak valid")
    # Get parameters from DataTables request
    draw = request.args.get('draw')
    if draw:
        draw = int(draw)
    start = request.args.get('start')
    if start:
        start = int(start)
    length = request.args.get('length')
    if length:
        length = int(length)
    search_value = request.args.get('search[value]')
    order_column_index = int(request.args.get('order[0][column]', 0))
    order_direction = request.args.get('order[0][dir]', 'desc')
    sort_column = ["_id", "tgl_periksa", "dokter", "poli",
                   "keluhan", "hasil_anamnesa", "_id"][order_column_index]

    # Get parameters for your own pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    search = request.args.get('search')
    order = request.args.get('order')
    sort = request.args.get('sort', 'asc')

    # Decide whether to use DataTables pagination or your own pagination
    if not draw:
        start = page - 1
        length = limit
        search_value = search
        sort_column = order
        order_direction = sort

    # Adjust the query for sorting

    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING
    collation = {'locale': 'en', 'strength': 2}

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

    if sort_column:
        data = list(db.list_checkup_user.find(query).sort(
            sort_column, sort_direction).collation(collation).skip(start).limit(length))
    else:
        data = list(db.list_checkup_user.find(query).collation(
            collation).skip(start).limit(length))

    for d in data:
        d['_id'] = str(d['_id'])

    # Total records count (unfiltered)
    total_records = db.list_checkup_user.count_documents({'nik': nik})

    # Total records count after filtering
    filtered_records = db.list_checkup_user.count_documents(query)

    total_pages = (filtered_records + length - 1) // length

    # Create the meta pagination object
    pagination = Pagination(start+1, length, total_pages, filtered_records)

    # Create datatables pagination object
    datatables_pagination = DatatablesPagination(
        total_records, filtered_records, draw, start, length)

    response = api_response(True, 200, "success", "Data berhasil diambil",
                            data, pagination.__dict__, datatables_pagination.__dict__)
    return jsonify(response.__dict__)


@app.route('/api/checkup/<nik>/<id>')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
@swag_from('swagger_doc/checkup_detail.yml')
def api_detail_checkup(decoded_token, nik, id):
    if nik == 'undefined':
        raise HttpException(False, 400, "failed", "NIK tidak boleh kosong")
    if id == 'undefined':
        raise HttpException(False, 400, "failed", "ID tidak boleh kosong")
    if not is_valid_nik(nik):
        raise HttpException(False, 400, "failed", "NIK tidak valid")
    if not ObjectId.is_valid(id):
        raise HttpException(False, 400, "failed", "ID tidak valid")
    data = db.list_checkup_user.find_one({"_id": ObjectId(id)}, {"_id": False})
    if not data:
        raise HttpException(False, 400, "failed", "Data tidak ditemukan")
    response = api_response(True, 200, "success",
                            "Data berhasil diambil", data)
    return jsonify(response.__dict__)


@app.route('/api/checkup/<nik>/<id>', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
@swag_from('swagger_doc/checkup_edit.yml')
def edit_checkup(decoded_token, nik, id):
    if nik == 'undefined':
        raise HttpException(False, 400, "failed", "NIK tidak boleh kosong")
    if id == 'undefined':
        raise HttpException(False, 400, "failed", "ID tidak boleh kosong")
    if not is_valid_nik(nik):
        raise HttpException(False, 400, "failed", "NIK tidak valid")
    if not ObjectId.is_valid(id):
        raise HttpException(False, 400, "failed", "ID tidak valid")

    body = request.is_json
    if body:
        raise HttpException(False, 415, "failed",
                            "Data harus dalam bentuk form data")
    data = db.list_checkup_user.find_one({"_id": ObjectId(id)}, {"_id": False})
    if not data:
        raise HttpException(False, 400, "failed", "Data tidak ditemukan")

    doc = {}
    dokter = request.form.get('dokter')
    dokter_list = list(db.jadwal.distinct('nama'))
    if dokter:
        if dokter not in dokter_list:
            raise HttpException(
                False, 400, "failed", f"Dokter {dokter} tidak tersedia, pilih dari {dokter_list}")
        doc['dokter'] = dokter

    hasil_anamnesa = request.form.get('hasil_anamnesa')
    if hasil_anamnesa:
        doc['hasil_anamnesa'] = hasil_anamnesa

    db.list_checkup_user.update_one({"_id": ObjectId(id)}, {"$set": doc})

    response = api_response(True, 200, "success", "Data berhasil diperbarui")
    return jsonify(response.__dict__)


# @app.route('/api/checkup/export')
# @validate_token_api(SECRET_KEY, TOKEN_KEY, db)
# @authorized_roles_api(["pegawai"])
# @swag_from('swagger_doc/checkup_export.yml')
# def export_checkup(decoded_token):
#     user_id = ObjectId(decoded_token.get("uid"))
#     username = db.users.find_one({"_id": user_id}).get('username')
#     # Get startdate and enddate from query parameters
#     startdate_str = request.args.get('startdate')
#     enddate_str = request.args.get('enddate')

#     if not startdate_str:
#         raise HttpException(False, 400, "failed",
#                             "startdate tidak boleh kosong")

#     if not enddate_str:
#         raise HttpException(False, 400, "failed",
#                             "enddate tidak boleh kosong")

#     if startdate_str and not is_valid_date(startdate_str):
#         raise HttpException(False, 400, "failed",
#                             "Format tanggal tidak valid, gunakan format dd-mm-yyyy")
#     if enddate_str and not is_valid_date(enddate_str):
#         raise HttpException(False, 400, "failed",
#                             "Format tanggal tidak valid, gunakan format dd-mm-yyyy")

#     if parse_date(enddate_str) < parse_date(startdate_str):
#         raise HttpException(False, 400, "failed",
#                             "startdate harus lebih kecil dibanding enddate")

#     # Parse startdate and enddate to datetime objects
#     startdate_iso = {'$dateFromString': {
#         'dateString': startdate_str, 'format': '%d-%m-%Y'}}
#     enddate_iso = {'$dateFromString': {
#         'dateString': enddate_str, 'format': '%d-%m-%Y'}}

#     # Query registrations within the specified date range
#     checkup = db.list_checkup_user.find({
#         "$expr": {
#             "$and": [
#                 {"$gte": [{"$dateFromString": {
#                     "dateString": "$tgl_periksa", "format": "%d-%m-%Y"}}, startdate_iso]},
#                 {"$lte": [{"$dateFromString": {
#                     "dateString": "$tgl_periksa", "format": "%d-%m-%Y"}}, enddate_iso]}
#             ]
#         }
#     }, {"_id": False})

#     # Convert MongoDB cursor to a list of dictionaries
#     checkup_list = list(checkup)

#     # Create a DataFrame from the list
#     df = pd.DataFrame(checkup_list)

#     # Create a custom header
#     custom = pd.DataFrame({
#         'Nama': df['nama'] if len(checkup_list) > 0 else [''],
#         'NIK': df['nik'] if len(checkup_list) > 0 else [''],
#         'Tanggal Periksa': df['tgl_periksa'] if len(checkup_list) > 0 else [''],
#         'Keluhan': df['keluhan'] if len(checkup_list) > 0 else [''],
#         'Poli': df['poli'] if len(checkup_list) > 0 else [''],
#         'Dokter': df['dokter'] if len(checkup_list) > 0 else [''],
#         'Hasil Anamnesa': df['hasil_anamnesa'] if len(checkup_list) > 0 else ['']
#     })

#     # Convert DataFrame to CSV format
#     output = BytesIO()
#     custom.to_csv(output, index=False, encoding='utf-8')
#     output.seek(0)

#     filename = f"checkup-{username}-{startdate_str}-{enddate_str}.csv"

#     # Return CSV file as a response with a dynamic file name
#     return send_file(output, as_attachment=True, download_name=filename, mimetype='text/csv')


# Return Profile User
@app.route("/api/profile")
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@swag_from('swagger_doc/profile.yml')
def api_profile(decoded_token):
    user_id = ObjectId(decoded_token.get("uid"))
    user_data = db.users.find_one({"_id": user_id}, {
        '_id': False, 'password': False})
    response = api_response(True, 200, "success",
                            "Data berhasil diambil", user_data)
    return jsonify(response.__dict__)


# Handle Edit Profile
@app.route('/api/profile/edit', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@swag_from('swagger_doc/profile_edit.yml')
def edit_profile(decoded_token):
    user_id = ObjectId(decoded_token.get("uid"))
    user_data = db.users.find_one({"_id": user_id}, {
        '_id': False, 'password': False})
    body = request.is_json
    if body:
        raise HttpException(False, 415, "failed",
                            "Data harus dalam bentuk form data")

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
            raise HttpException(False, 400, "failed",
                                "NIK harus terdiri dari 16 digit angka")
        existing_nik = db.users.find_one({'nik': nik})
        if existing_nik and existing_nik['username'] != username:
            raise HttpException(False, 400, "failed", "NIK sudah digunakan")
        profile_doc['nik'] = nik
        checkup_doc['nik'] = nik
        registration_doc['nik'] = nik
        rekam_medis['nik'] = nik
    if tgl_lahir:
        if not is_valid_date(tgl_lahir):
            raise HttpException(
                False, 400, "failed", "Format tanggal lahir tidak valid, gunakan format dd-mm-yyyy")
        if not is_max_date_now(tgl_lahir):
            raise HttpException(False, 400, "failed",
                                "Tanggal lahir tidak boleh lebih dari hari ini")
        profile_doc['tgl_lahir'] = tgl_lahir
        registration_doc['tgl_lahir'] = tgl_lahir
        rekam_medis['umur'] = (
            datetime.now() - datetime.strptime(tgl_lahir, '%d-%m-%Y')).days // 365
    if gender:
        if not is_valid_gender(gender):
            raise HttpException(False, 400, "failed",
                                "Jenis kelamin tidak valid")
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
            raise HttpException(
                False, 400, "failed", "Nomor telepon tidak valid, gunakan format nomor 10 - 13 digit")
        profile_doc['no_telp'] = no_telp
        registration_doc['no_telp'] = no_telp
        rekam_medis['no_telp'] = no_telp

    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file.filename == '':
            raise HttpException(False, 400, "failed",
                                "Profile picture tidak boleh kosong")
        filename = secure_filename(file.filename)
        extension = filename.split(".")[-1]
        if extension not in ["jpg", "jpeg", "png"]:
            raise HttpException(False, 400, "failed",
                                "Profile picture harus berupa file gambar")
        file_path = f"profile_pics/{username}.{extension}"
        file.save("./static/" + file_path)
        profile_doc["profile_pic"] = file_path
    # update collection users
    db.users.update_one({"username": username}, {"$set": profile_doc})
    # update collection registrations
    db.registrations.update_many({"username": username}, {
                                 "$set": registration_doc})
    # update collection checkup
    db.list_checkup_user.update_many({"nik": old_nik}, {"$set": checkup_doc})
    # update collection rekam_medis
    db.rekam_medis.update_many({"nik": old_nik}, {"$set": rekam_medis})

    response = api_response(True, 200, "success",
                            "Profile berhasil diperbarui")

    return jsonify(response.__dict__)


@app.route('/api/rekam_medis')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
@swag_from('swagger_doc/rekam_medis.yml')
def api_rekam_medis(decoded_token):
    nik = request.args.get('nik')
    name = request.args.get('name')
    # Get parameters from DataTables request
    draw = request.args.get('draw')
    if draw:
        draw = int(draw)
    start = request.args.get('start')
    if start:
        start = int(start)
    length = request.args.get('length')
    if length:
        length = int(length)
    search_value = request.args.get('search[value]')
    order_column_index = int(request.args.get('order[0][column]', 0))
    order_direction = request.args.get('order[0][dir]')
    sort_column = ["_id", "nik", "nama", "umur"][order_column_index]

    # Get parameters for your own pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    search = request.args.get('search')
    order = request.args.get('order')
    sort = request.args.get('sort', 'asc')

    # Decide whether to use DataTables pagination or your own pagination
    if not draw:
        start = page - 1
        length = limit
        search_value = search
        sort_column = order
        order_direction = sort

    if nik == 'nik':
        list_nik = list(db.rekam_medis.distinct('nik'))
        sorted_list_nik = sorted(list_nik)
        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_nik)
        return jsonify(response.__dict__)
    if name == 'name':
        list_nama = list(db.rekam_medis.distinct('nama'))
        sorted_list_nama = sorted(list_nama, key=lambda x: x.lower())
        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_nama)
        return jsonify(response.__dict__)

    # Adjust the query for sorting
    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING
    collation = {'locale': 'en', 'strength': 2}

    # MongoDB query with search
    query = {}
    if nik:
        query['nik'] = nik
    if name:
        query['nama'] = name
    if search_value:
        query["$or"] = [
            {"nama": {"$regex": search_value, "$options": "i"}},
            {"nik": {"$regex": search_value, "$options": "i"}},
        ]

    if sort_column:
        data = list(db.rekam_medis.find(query).sort(
            sort_column, sort_direction).collation(collation).skip(start).limit(length))
    else:
        data = list(db.rekam_medis.find(query).collation(
            collation).skip(start).limit(length))

    for d in data:
        d['_id'] = str(d['_id'])

    # Total records count (unfiltered)
    total_records = db.rekam_medis.count_documents({})

    # Total records count after filtering
    filtered_records = db.rekam_medis.count_documents(query)

    total_pages = (filtered_records + length -
                   1) // length  # Calculate total pages
    # Create the meta pagination object
    pagination = Pagination(start+1, length, total_pages, filtered_records)

    # Create datatables pagination object
    datatables_pagination = DatatablesPagination(
        total_records, filtered_records, draw, start, length)

    response = api_response(True, 200, "success", "Data berhasil diambil",
                            data, pagination.__dict__, datatables_pagination.__dict__)
    return jsonify(response.__dict__)


@app.route('/api/rekam_medis', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
@swag_from('swagger_doc/rekam_medis_post.yml')
def api_rekam_medis_post(decoded_token):
    body = request.is_json
    if body:
        raise HttpException(False, 415, "failed",
                            "Data harus dalam bentuk form data")

    no_kartu = request.form.get('no')
    existing_no_kartu = bool(
        db.rekam_medis.count_documents({'no_kartu': no_kartu}) > 0)
    if not no_kartu:
        raise HttpException(False, 400, "failed",
                            "Nomor kartu tidak boleh kosong")
    if existing_no_kartu:
        raise HttpException(False, 400, "failed",
                            "Nomor kartu sudah digunakan")
    if not is_valid_no_kartu(no_kartu):
        raise HttpException(
            False, 400, "failed", "Format nomor kartu tidak valid, gunakan format xx-xx-xx")
    dokter = request.form.get('dokter')
    dokter_list = list(db.jadwal.distinct('nama'))
    if not dokter:
        raise HttpException(False, 400, "failed", "Dokter tidak boleh kosong")
    if dokter not in dokter_list:
        raise HttpException(
            False, 400, "failed", f"Dokter {dokter} tidak tersedia, pilih dari {dokter_list}")
    hasil_anamnesa = request.form.get('hasil_anamnesa')

    if not hasil_anamnesa:
        raise HttpException(False, 400, "failed",
                            "Hasil anamnesa tidak boleh kosong")
    if hasil_anamnesa == '':
        raise HttpException(False, 400, "failed",
                            "Hasil anamnesa tidak boleh kosong")
    nik = request.form.get('nik')
    if not nik:
        raise HttpException(False, 400, "failed", "NIK tidak boleh kosong")
    existing_rekam_medis = bool(db.rekam_medis.count_documents({'nik': nik}))
    if existing_rekam_medis:
        raise HttpException(False, 400, "failed", "Rekam medis sudah ada")
    user_data = db.users.find_one({'nik': nik})
    if not user_data:
        raise HttpException(False, 400, "failed",
                            "Data pengguna tidak ditemukan")
    data_reg = db.registrations.find_one({'nik': nik})
    if not data_reg:
        raise HttpException(False, 400, "failed",
                            "Data pendaftaran tidak ditemukan")
    nama = user_data.get('name')
    data_rekam_medis = {
        'no_kartu': no_kartu,
        'nama': nama,
        'username': user_data['username'],
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

    response = api_response(True, 200, "success",
                            "Rekam medis berhasil dibuat")
    return jsonify(response.__dict__), 201


@app.route('/api/rekam_medis/<nik>')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
@swag_from('swagger_doc/rekam_medis_nik.yml')
def api_detail_rekam_medis(decoded_token, nik):
    if nik == 'undefined':
        raise HttpException(False, 400, "failed", "NIK tidak boleh kosong")
    if not is_valid_nik(nik):
        raise HttpException(False, 400, "failed", "NIK tidak valid")

    data = db.rekam_medis.find_one({"nik": nik}, {"_id": False})
    if not data:
        raise HttpException(False, 400, "failed", "Data tidak ditemukan")
    response = api_response(True, 200, "success",
                            "Data berhasil diambil", data)
    return jsonify(response.__dict__)


# @app.route('/api/rekam_medis/export/<nik>')
# @validate_token_api(SECRET_KEY, TOKEN_KEY, db)
# @authorized_roles_api(["pegawai"])
# @swag_from('swagger_doc/rekam_medis_export.yml')
# def export_rekam_medis(decoded_token, nik):
#     if nik == 'undefined':
#         raise HttpException(False, 400, "failed", "NIK tidak boleh kosong")
#     if not is_valid_nik(nik):
#         raise HttpException(False, 400, "failed", "NIK tidak valid")

#     user_id = ObjectId(decoded_token.get("uid"))
#     username = db.users.find_one({"_id": user_id}).get('username')

#     # Query registrations within the specified date range
#     checkup_user = db.list_checkup_user.find({"nik": nik}, {"_id": False})
#     rekam_medis = db.rekam_medis.find_one({"nik": nik}, {"_id": False})

#     if not rekam_medis:
#         raise HttpException(False, 400, "failed",
#                             f"Rekam medis dengan NIK {nik} tidak ditemukan.")

#     # Convert MongoDB cursor to a list of dictionaries
#     list_checkup_user = list(checkup_user)

#     # Create a DataFrame from the list
#     df = pd.DataFrame(list_checkup_user)

#     custom_row = pd.DataFrame({
#         'No Kartu': [rekam_medis['no_kartu']],
#         'Username': [rekam_medis['username']],
#         'Nama': [rekam_medis['nama']],
#         'NIK': [rekam_medis['nik']],
#         'Umur': [rekam_medis['umur']],
#         'Alamat': [rekam_medis['alamat']],
#         'No Telp': [rekam_medis['no_telp']],
#     })

#     # Create second header DataFrame (corresponding to registration data fields)
#     second_header = pd.DataFrame({
#         'Nama Dokter': df['dokter'] if len(list_checkup_user) > 0 else [''],
#         'Tanggal Periksa': df['tgl_periksa'] if len(list_checkup_user) > 0 else [''],
#         'Poli': df['poli'] if len(list_checkup_user) > 0 else [''],
#         'Keluhan': df['keluhan'] if len(list_checkup_user) > 0 else [''],
#         'Hasil Anamnesa': df['hasil_anamnesa'] if len(list_checkup_user) > 0 else ['']
#     })

#     # Concatenate DataFrames
#     final_df = pd.concat([custom_row, second_header],
#                          axis=0, ignore_index=True,)

#     # Convert DataFrame to CSV format
#     output = BytesIO()
#     final_df.to_csv(output, index=False, encoding='utf-8')
#     output.seek(0)

#     filename = f"rekam-medis-{username}-{nik}.csv"

#     # Return CSV file as a response with a dynamic file name
#     return send_file(output, as_attachment=True, download_name=filename, mimetype='text/csv')


@app.route('/api/users/pasien')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
@swag_from('swagger_doc/users_pasien.yml')
def api_users_pasien(decoded_token):
    name = request.args.get('name')
    nik = request.args.get('nik')
    status_filter = request.args.get('status_filter')

    # Get parameters from DataTables request
    draw = request.args.get('draw')
    if draw:
        draw = int(draw)
    start = request.args.get('start')
    if start:
        start = int(start)
    length = request.args.get('length')
    if length:
        length = int(length)
    search_value = request.args.get('search[value]')
    order_column_index = int(request.args.get('order[0][column]', 0))
    order_direction = request.args.get('order[0][dir]', 'asc')

    # Get unique usernames from registrations with status: done
    unique_usernames = db.registrations.distinct(
        "username", {"status": "done"})
    if status_filter == 'True':
        unique_usernames = db.rekam_medis.distinct(
            "username")
    if status_filter == 'False':
        has_rekam = db.rekam_medis.distinct("username")
        unique_usernames = list(set(unique_usernames) - set(has_rekam))

    # Get parameters for your own pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    search = request.args.get('search')
    order = request.args.get('order')
    sort = request.args.get('sort', 'asc')

    if name == 'name':
        list_nama = list(db.registrations.distinct(
            "name", {"status": "done"}))

        sorted_list_nama = sorted(list_nama, key=lambda x: x.lower())

        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_nama)
        return jsonify(response.__dict__)
    if nik == 'nik':
        list_nik = list(db.registrations.distinct(
            "nik", {"status": "done"}))

        sorted_list_nik = sorted(list_nik)

        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_nik)
        return jsonify(response.__dict__)

    # Adjust the query for sorting
    sort_column = ["_id", "name", "nik", "_id"][order_column_index]

    # Decide whether to use DataTables pagination or your own pagination
    if not draw:
        start = page - 1
        length = limit
        search_value = search
        sort_column = order
        order_direction = sort

    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING
    collation = {'locale': 'en', 'strength': 2}

    # MongoDB query with search
    query = {"username": {"$in": unique_usernames}}
    if name:
        query['name'] = name
    if nik:
        query['nik'] = nik
    if search_value:
        query["$or"] = [
            {"name": {"$regex": search_value, "$options": "i"}},
            {"nik": {"$regex": search_value, "$options": "i"}},
        ]

    # Fetch user details from users collection based on unique usernames
    if sort_column:
        data_pasien_list = (
            db.users.find(query)
            .sort(sort_column, sort_direction)
            .collation(collation)
            .skip(start)
            .limit(length)
        )
    else:
        data_pasien_list = (
            db.users.find(query).collation(collation).skip(start).limit(length)
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
    total_records = db.users.count_documents(
        {'username': {'$in': unique_usernames}})

    # Total records count after filtering
    filtered_records = db.users.count_documents(query)

    total_pages = (filtered_records + length -
                   1) // length  # Calculate total pages
    # Create the meta pagination object
    pagination = Pagination(start + 1, length, total_pages, filtered_records)

    # Create datatables pagination object
    datatables_pagination = DatatablesPagination(
        total_records, filtered_records, draw, start, length)

    response = api_response(
        True, 200, "success", "Data berhasil diambil", data_pasien, pagination.__dict__, datatables_pagination.__dict__
    )
    return jsonify(response.__dict__)


@app.route('/api/jadwal')
@swag_from('swagger_doc/jadwal.yml')
def api_jadwal():
    nama = request.args.get('nama')
    poli = request.args.get('poli')
    hari = request.args.getlist('hari[]')

    # Get parameters from DataTables request
    draw = request.args.get('draw')
    if draw:
        draw = int(draw)
    start = request.args.get('start')
    if start:
        start = int(start)
    length = request.args.get('length')
    if length:
        length = int(length)
    search_value = request.args.get('search[value]')
    order_column_index = int(request.args.get('order[0][column]', 0))
    order_direction = request.args.get('order[0][dir]', 'asc')

    # Get parameters for your own pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    search = request.args.get('search')
    order = request.args.get('order')
    sort = request.args.get('sort', 'asc')

    # Adjust the query for sorting
    sort_column = ["nama", "poli", "hari",
                   "jam_buka", "jam_tutup"][order_column_index]

    # Decide whether to use DataTables pagination or your own pagination
    if not draw:
        start = page - 1
        length = limit
        search_value = search
        sort_column = order
        order_direction = sort

    sort_direction = ASCENDING if order_direction == 'asc' else DESCENDING
    collation = {'locale': 'en', 'strength': 2}

    if nama == 'nama':
        list_nama = list(db.jadwal.distinct('nama'))

        sorted_list_nama = sorted(list_nama, key=lambda x: x.lower())
        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_nama)
        return jsonify(response.__dict__)
    if poli == 'poli':
        list_poli = list(db.jadwal.distinct('poli'))

        sorted_list_poli = sorted(list_poli, key=lambda x: x.lower())
        response = api_response(True, 200, "success",
                                "Data berhasil diambil", sorted_list_poli)
        return jsonify(response.__dict__)

    # MongoDB query with search
    query = {}
    if nama:
        query['nama'] = nama
    if poli:
        query['poli'] = poli
    if hari:
        query['hari'] = {"$in": hari}
    if search_value:
        query["$or"] = [
            {"nama": {"$regex": search_value, "$options": "i"}},
            {"poli": {"$regex": search_value, "$options": "i"}},
            {"hari": {"$regex": search_value, "$options": "i"}},
            {"jam_buka": {"$regex": search_value, "$options": "i"}},
            {"jam_tutup": {"$regex": search_value, "$options": "i"}},
        ]

    if sort_column:
        data = list(db.jadwal.find(query).sort(sort_column, sort_direction).collation(
            collation).skip(start).limit(length))
    else:
        data = list(db.jadwal.find(query).collation(
            collation).skip(start).limit(length))

    for d in data:
        d['_id'] = str(d['_id'])

    # Total records count (unfiltered)
    total_records = db.jadwal.count_documents({})

    # Total records count after filtering
    filtered_records = db.jadwal.count_documents(query)

    total_pages = (filtered_records + length - 1) // length

    # Create the meta pagination object
    pagination = Pagination(start+1, length, total_pages, filtered_records)

    # Create datatables pagination object
    datatables_pagination = DatatablesPagination(
        total_records, filtered_records, draw, start, length)

    response = api_response(True, 200, "success", "Data berhasil diambil", data,
                            pagination.__dict__, datatables_pagination.__dict__)

    return jsonify(response.__dict__)


@app.route('/api/jadwal', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
@swag_from('swagger_doc/jadwal_post.yml')
def api_jadwal_post(decoded_token):
    body = request.is_json
    if body:
        raise HttpException(False, 415, "failed",
                            "Data harus dalam bentuk form data")
    list_hari = ['senin', 'selasa', 'rabu',
                 'kamis', 'jumat', 'sabtu', 'minggu']
    nama = request.form.get('nama')
    if not nama:
        raise HttpException(False, 400, "failed", "Nama tidak boleh kosong")
    poli = request.form.get('poli')
    if not poli:
        raise HttpException(False, 400, "failed", "Poli tidak boleh kosong")
    poli = poli.title()
    hari = request.form.getlist('hari')
    if not hari:
        raise HttpException(False, 400, "failed", "Hari tidak boleh kosong")
    jam_buka = request.form.get('jam_buka')
    if not jam_buka:
        raise HttpException(False, 400, "failed",
                            "Jam buka tidak boleh kosong")
    jam_tutup = request.form.get('jam_tutup')
    if not jam_tutup:
        raise HttpException(False, 400, "failed",
                            "Jam tutup tidak boleh kosong")
    if not isinstance(hari, list):
        raise HttpException(False, 400, "failed", "Hari harus merupakan list")
    if any(x for x in hari if x.lower() not in list_hari):
        raise HttpException(False, 400, "failed", "Hari tidak valid")
    hari = [x.lower() for x in hari]
    hari = sorted(hari, key=list_hari.index)
    if not is_valid_time(jam_buka):
        raise HttpException(False, 400, "failed",
                            "Format jam buka tidak valid")
    if not is_valid_time(jam_tutup):
        raise HttpException(False, 400, "failed",
                            "Format jam tutup tidak valid")
    if datetime.strptime(jam_buka, '%H:%M') > datetime.strptime(jam_tutup, '%H:%M'):
        raise HttpException(False, 400, "failed",
                            "Jam buka tidak boleh lebih besar dari jam tutup")
    jadwal_data = {
        "nama": nama,
        "poli": poli,
        "hari": hari,
        "jam_buka": jam_buka,
        "jam_tutup": jam_tutup,
    }

    result = db.jadwal.insert_one(jadwal_data)
    jadwal_data["_id"] = str(result.inserted_id)
    socketio.emit('new_jadwal', jadwal_data, namespace='/jadwal')

    response = api_response(True, 200, "success",
                            "Jadwal berhasil ditambahkan", jadwal_data)
    return jsonify(response.__dict__), 201


@app.route('/api/jadwal/<id>')
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
@swag_from('swagger_doc/jadwal_detail.yml')
def api_detail_jadwal(decoded_token, id):
    if id == 'undefined':
        raise HttpException(False, 400, "failed", "ID tidak boleh kosong")
    if not ObjectId.is_valid(id):
        raise HttpException(False, 400, "failed", "ID tidak valid")

    data = db.jadwal.find_one({"_id": ObjectId(id)}, {"_id": False})
    if not data:
        raise HttpException(False, 400, "failed", "Data tidak ditemukan")
    response = api_response(True, 200, "success",
                            "Data berhasil diambil", data)
    return jsonify(response.__dict__)


@app.route('/api/jadwal/<id>', methods=['POST'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
@swag_from('swagger_doc/jadwal_edit.yml')
def api_jadwal_put(decoded_token, id):
    if id == 'undefined':
        raise HttpException(False, 400, "failed", "ID tidak boleh kosong")
    if not ObjectId.is_valid(id):
        raise HttpException(False, 400, "failed", "ID tidak valid")

    data = db.jadwal.find_one({"_id": ObjectId(id)})
    if not data:
        raise HttpException(False, 400, "failed", "Data tidak ditemukan")

    body = request.is_json
    if body:
        raise HttpException(False, 415, "failed",
                            "Data harus dalam bentuk form data")
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
            raise HttpException(False, 400, "failed",
                                "Hari harus merupakan list")
        if any(x for x in hari if x.lower() not in ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu']):
            raise HttpException(False, 400, "failed", "Hari tidak valid")
        doc['hari'] = hari
    jam_buka = request.form.get('jam_buka')
    jam_tutup = request.form.get('jam_tutup')
    if jam_buka and not jam_tutup:
        raise HttpException(False, 400, "failed",
                            "Jam tutup tidak boleh kosong")
    if not jam_buka and jam_tutup:
        raise HttpException(False, 400, "failed",
                            "Jam buka tidak boleh kosong")
    if jam_buka and jam_tutup:
        if not is_valid_time(jam_buka):
            raise HttpException(False, 400, "failed",
                                "Format jam buka tidak valid")
        if not is_valid_time(jam_tutup):
            raise HttpException(False, 400, "failed",
                                "Format jam tutup tidak valid")
        if datetime.strptime(jam_buka, '%H:%M') > datetime.strptime(jam_tutup, '%H:%M'):
            raise HttpException(
                False, 400, "failed", "Jam buka tidak boleh lebih besar dari jam tutup")
        doc['jam_buka'] = jam_buka
        doc['jam_tutup'] = jam_tutup

    jadwal_data = db.jadwal.update_one({"_id": ObjectId(id)}, {"$set": doc})

    socketio.emit('new_jadwal', doc, namespace='/jadwal')

    response = api_response(True, 200, "success", "Jadwal berhasil diperbarui")
    return jsonify(response.__dict__)


@app.route('/api/jadwal/<id>', methods=['DELETE'])
@validate_token_api(SECRET_KEY, TOKEN_KEY, db)
@authorized_roles_api(["pegawai"])
@swag_from('swagger_doc/jadwal_delete.yml')
def api_jadwal_delete(decoded_token, id):
    if id == 'undefined':
        raise HttpException(False, 400, "failed", "ID tidak boleh kosong")
    if not ObjectId.is_valid(id):
        raise HttpException(False, 400, "failed", "ID tidak valid")

    data = db.jadwal.find_one({"_id": ObjectId(id)}, {"_id": False})
    if not data:
        raise HttpException(False, 400, "failed", "Data tidak ditemukan")

    result = db.jadwal.delete_one({"_id": ObjectId(id)})
    socketio.emit('new_jadwal', data, namespace='/jadwal')
    response = api_response(True, 200, "success", "Jadwal berhasil dihapus")
    return jsonify(response.__dict__)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
