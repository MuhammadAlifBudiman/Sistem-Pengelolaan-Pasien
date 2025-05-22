# utils.py
# Utility functions for session management, validation, and date/time parsing in a Flask-based patient management system.

# Import Flask modules for HTTP request/response handling
from flask import jsonify, request
# Import datetime for date/time operations
from datetime import datetime, timedelta
from bson import ObjectId  # Import ObjectId for MongoDB document IDs
import jwt  # Import PyJWT for JWT token handling
from exceptions import HttpException  # Import custom HTTP exception class


def get_authorization(TOKEN_KEY):
    """
    Retrieve the authorization token from cookies or headers.
    Args:
        TOKEN_KEY (str): The key used to retrieve the token from cookies.
    Returns:
        str or None: The token string if found, else None.
    """
    cookie = request.cookies.get(TOKEN_KEY)
    header = request.headers.get('Authorization')
    if cookie:
        return cookie
    if header:
        return header.split()[1]
    return None


def create_user_session(user_id, db):
    """
    Create a new user session in the database.
    Args:
        user_id (ObjectId): The user's ID.
        db: The database connection object.
    Returns:
        dict: The created user session document.
    """
    user_session = {
        'user_id': user_id,
        'status': 'ACTIVE'
    }
    result = db.user_sessions.insert_one(user_session)
    user_session["_id"] = result.inserted_id
    return user_session


def check_session_active(session_id, db):
    """
    Check if a session is active in the database.
    Args:
        session_id (ObjectId): The session's ID.
        db: The database connection object.
    Returns:
        dict or bool: The session document if active, else False.
    """
    session = db.user_sessions.find_one({'_id': session_id})
    if session and session['status'] == 'ACTIVE':
        session['_id'] = str(session['_id'])
        return session
    return False


def check_user_session(token, SECRET_KEY, db):
    """
    Validate a user session using a JWT token.
    Args:
        token (str): The JWT token.
        SECRET_KEY (str): The secret key for decoding JWT.
        db: The database connection object.
    Returns:
        dict or bool: Decoded token if valid, else False. Raises HttpException on error.
    """
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = ObjectId(decoded_token["uid"])
        session_id = ObjectId(decoded_token["sid"])
        user_session = check_session_active(session_id, db)
        if user_session and user_session['user_id'] == user_id:
            return decoded_token
        return False
    except jwt.ExpiredSignatureError:
        raise HttpException(False, 401, "Failed",
                            "Expired Token")  # Token has expired
    except jwt.InvalidTokenError:
        raise HttpException(False, 401, "Failed", "Invalid Token")


def logout_user_session(session_id, db):
    """
    Log out a user session by updating its status to 'LOGOUT'.
    Args:
        session_id (ObjectId): The session's ID.
        db: The database connection object.
    Returns:
        bool: True if session was updated, else False.
    """
    result = db.user_sessions.update_one(
        {'_id': session_id}, {'$set': {'status': 'LOGOUT'}})
    if result.modified_count == 0:
        return False
    return True


def get_antrian_today(db):
    """
    Get today's queue (antrian) data for each 'poli'.
    Args:
        db: The database connection object.
    Returns:
        list: List of dicts containing 'poli', 'jumlah_pendaftar', and 'dalam_antrian'.
    """
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
        # Count approved and done registrations for today
        antrian['jumlah_pendaftar'] = db.registrations.count_documents({
            "poli": antrian['poli'],
            "tanggal": datetime.now().strftime("%d-%m-%Y"),
            "status": {"$in": ["approved", "done"]}
        })
        # Count done registrations for today
        antrian['dalam_antrian'] = db.registrations.count_documents({
            "poli": antrian['poli'],
            "tanggal": datetime.now().strftime("%d-%m-%Y"),
            "status": "done"
        })
    return antrian_data


def is_valid_nik(nik):
    """
    Validate Indonesian NIK (National ID Number).
    Args:
        nik (str): The NIK string.
    Returns:
        bool: True if valid, else False.
    """
    return nik.isdigit() and len(nik) == 16


def is_valid_date(date_str):
    """
    Validate date string in 'dd-mm-yyyy' format.
    Args:
        date_str (str): The date string.
    Returns:
        bool: True if valid, else False.
    """
    try:
        datetime.strptime(date_str, '%d-%m-%Y')
        return True
    except ValueError:
        return False


def is_max_date_now(date_str):
    """
    Check if the date is not after today.
    Args:
        date_str (str): The date string.
    Returns:
        bool: True if date is today or before, else False.
    """
    try:
        date = datetime.strptime(date_str, '%d-%m-%Y')
        return date <= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    except ValueError:
        return False


def is_min_date_now(date_str):
    """
    Check if the date is not before today.
    Args:
        date_str (str): The date string.
    Returns:
        bool: True if date is today or after, else False.
    """
    try:
        date = datetime.strptime(date_str, '%d-%m-%Y')
        return date >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    except ValueError:
        return False


def is_valid_time(time_str):
    """
    Validate time string in 'HH:MM' format.
    Args:
        time_str (str): The time string.
    Returns:
        bool: True if valid, else False.
    """
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False


def is_valid_gender(gender):
    """
    Validate gender string (must be 'laki-laki' or 'perempuan').
    Args:
        gender (str): The gender string.
    Returns:
        bool: True if valid, else False.
    """
    return gender.lower() in ['laki-laki', 'perempuan']


def is_valid_phone_number(phone_number):
    """
    Validate Indonesian phone number (10-13 digits).
    Args:
        phone_number (str): The phone number string.
    Returns:
        bool: True if valid, else False.
    """
    return phone_number.isdigit() and 10 <= len(phone_number) <= 13


def is_valid_no_kartu(no_kartu):
    """
    Validate card number in 'XX-XX-XX' format (8 chars, dashes at 3rd and 6th position).
    Args:
        no_kartu (str): The card number string.
    Returns:
        bool: True if valid, else False.
    """
    return len(no_kartu) == 8 and no_kartu[2] == '-' and no_kartu[5] == '-' and no_kartu[:2].isdigit() and no_kartu[3:5].isdigit() and no_kartu[6:].isdigit()

# Function to parse dates in "dd-mm-yyyy" format


def parse_date(date_str):
    """
    Parse a date string in 'dd-mm-yyyy' format to a datetime object.
    Args:
        date_str (str): The date string.
    Returns:
        datetime: The parsed datetime object.
    """
    return datetime.strptime(date_str, '%d-%m-%Y')
