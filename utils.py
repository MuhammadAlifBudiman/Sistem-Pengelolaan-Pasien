from flask import jsonify, request
from datetime import datetime, timedelta
from bson import ObjectId
import jwt
from exceptions import HttpException

def get_authorization(TOKEN_KEY):
    cookie = request.cookies.get(TOKEN_KEY)
    header = request.headers.get('Authorization')
    if cookie:
        return cookie
    if header:
        return header.split()[1]

    return None


def create_user_session(user_id, db):
    user_session = {
        'user_id': user_id,
        'status': 'ACTIVE'
    }

    result = db.user_sessions.insert_one(user_session)
    user_session["_id"] = result.inserted_id

    return user_session


def check_session_active(session_id, db):
    session = db.user_sessions.find_one({'_id': session_id})
    if session and session['status'] == 'ACTIVE':
        session['_id'] = str(session['_id'])
        return session
    return False


def check_user_session(token, SECRET_KEY, db):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = ObjectId(decoded_token["uid"])
        session_id = ObjectId(decoded_token["sid"])
        user_session = check_session_active(session_id, db)
        if user_session and user_session['user_id'] == user_id:
            return decoded_token
        return False
    except jwt.ExpiredSignatureError:
        raise HttpException(False, 401, "Failed", "Expired Token")  # Token has expired
    except jwt.InvalidTokenError:
        raise HttpException(False, 401, "Failed", "Invalid Token")
    

def logout_user_session(session_id, db):
    result = db.user_sessions.update_one(
        {'_id': session_id}, {'$set': {'status': 'LOGOUT'}})
    if result.modified_count == 0:
        return False
    return True

def get_antrian_today(db):
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
                "_id": "$poli"
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

    return antrian_data

def is_valid_nik(nik):
    return nik.isdigit() and len(nik) == 16


def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%d-%m-%Y')
        return True
    except ValueError:
        return False

def is_max_date_now(date_str):
    try:
        date = datetime.strptime(date_str, '%d-%m-%Y')
        return date <= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    except ValueError:
        return False
    
def is_min_date_now(date_str):
    try:
        date = datetime.strptime(date_str, '%d-%m-%Y')
        return date >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
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

def is_valid_no_kartu(no_kartu):
    return len(no_kartu) == 8 and no_kartu[2] == '-' and no_kartu[5] == '-' and no_kartu[:2].isdigit() and no_kartu[3:5].isdigit() and no_kartu[6:].isdigit()

# Function to parse dates in "dd-mm-yyyy" format
def parse_date(date_str):
    return datetime.strptime(date_str, '%d-%m-%Y')
