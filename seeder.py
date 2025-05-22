# seeder.py
# Seeder script for populating MongoDB collections for a Flask app.
#
# Usage examples:
#   - Seed all collections:
#       python3 seeder.py --user --jadwal --registration --approve-registrations --done-registrations --rekam-medis --list-checkup-user
#   - Recreate database:
#       python3 seeder.py --user --jadwal --registration --approve-registrations --done-registrations --rekam-medis --list-checkup-user --reload
#   - Seed specific collections:
#       python3 seeder.py --user
#       python3 seeder.py --jadwal
#       python3 seeder.py --registration
#       python3 seeder.py --rekam-medis
#       python3 seeder.py --list-checkup-user

from attr import has
from flask import Flask
from flask_pymongo import PyMongo
from pymongo import MongoClient
from faker import Faker
import os
import argparse
import random
from os.path import join, dirname
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Initialize Flask app and MongoDB connection
app = Flask(__name__)
MONGODB_CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING")
if not MONGODB_CONNECTION_STRING:
    raise ValueError(
        "MONGODB_CONNECTION_STRING environment variable is not set")
# Set the default database name
DB_NAME = os.environ.get("DB_NAME")
if not DB_NAME:
    raise ValueError("DB_NAME environment variable is not set")
app.config['MONGO_URI'] = MONGODB_CONNECTION_STRING
app.config['MONGO_DBNAME'] = DB_NAME
mongo = PyMongo(app)
client = MongoClient(MONGODB_CONNECTION_STRING)

# Initialize Faker for generating fake data
fake = Faker('id_ID')

# --- Seeder Functions ---


def generate_fake_user(role):
    """
    Generate a fake user document for the given role.
    Ensures unique username and NIK (16 digits).
    Args:
        role (str): User role ('pasien' or 'pegawai').
    Returns:
        dict: User document.
    """
    db = mongo.cx[app.config['MONGO_DBNAME']]
    while True:
        username = fake.unique.user_name()
        nik = str(fake.unique.random_number(16))
        # Ensure username and NIK are unique in the database
        existing_user = db.users.find_one(
            {'$or': [{'username': username}, {'nik': nik}]})
        if existing_user is None and len(nik) == 16:
            break
    # Password.12 (bcrypt hash)
    password = "$2b$10$xm2V57w6d8/Q4RzMYp9GDeiahaWW5HLmD1TxaS2TLurYXscUAATHS"
    salt = "6da84944bc8be809e39d6e63257cb840"
    user_data = {
        'profile_pic': 'profile_pics/profile_placeholder.png',
        'username': username,
        'name': fake.name(),
        'nik': nik,
        'tgl_lahir': fake.date_of_birth(minimum_age=18, maximum_age=60).strftime('%d-%m-%Y'),
        'gender': fake.random_element(elements=('laki-laki', 'perempuan')),
        'agama': fake.random_element(elements=('islam', 'kristen', 'hindu', 'budha', 'lainnya')),
        'status': fake.random_element(elements=('menikah', 'single')),
        'alamat': fake.address(),
        'no_telp': '628' + str(fake.random_int(min=10**7, max=10**10)),
        'password': password,
        'role': role,
        'salt': salt,
    }
    return user_data


def seed_users(num_pasien=10, num_pegawai=2):
    """
    Seed the users collection with fake pasien and pegawai users.
    Args:
        num_pasien (int): Number of pasien users to create.
        num_pegawai (int): Number of pegawai users to create.
    """
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]
        roles = {'pasien': num_pasien, 'pegawai': num_pegawai}
        for role, count in roles.items():
            for _ in range(count):
                user_data = generate_fake_user(role)
                db.users.insert_one(user_data)
        print("Users seeded.")


def seed_jadwal(num_jadwal=3):
    """
    Seed the jadwal collection with fake doctor schedules.
    Args:
        num_jadwal (int): Number of jadwal entries to create.
    """
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]
        poli_choices = ['Umum', 'Gigi', 'Mata', 'Jantung', 'THT',
                        'Syaraf', 'Kesehatan Jiwa', 'Anak', 'Fisioterapi']
        hari_choices = ['senin', 'selasa', 'rabu',
                        'kamis', 'jumat', 'sabtu', 'minggu']
        for _ in range(num_jadwal):
            # Generate random opening and closing times (2-4 hours apart)
            jam_buka = fake.time(pattern="%H:%M")
            jam_tutup = fake.time(pattern="%H:%M")
            while jam_buka >= jam_tutup:
                jam_buka = fake.time(pattern="%H:%M")
                jam_tutup = fake.time(pattern="%H:%M")
            time_format = "%H:%M"
            diff = datetime.strptime(
                jam_tutup, time_format) - datetime.strptime(jam_buka, time_format)
            while diff < timedelta(hours=2) or diff > timedelta(hours=4):
                jam_buka = fake.time(pattern="%H:%M")
                jam_tutup = fake.time(pattern="%H:%M")
                diff = datetime.strptime(
                    jam_tutup, time_format) - datetime.strptime(jam_buka, time_format)
            jadwal_data = {
                'nama': fake.name(),
                'poli': fake.random_element(elements=poli_choices),
                'hari': random.sample(hari_choices, k=random.randint(1, 5)),
                'jam_buka': jam_buka,
                'jam_tutup': jam_tutup
            }
            # Sort the 'hari' list according to the specified order
            jadwal_data['hari'].sort(key=hari_choices.index)
            db.jadwal.insert_one(jadwal_data)
        print("Jadwal seeded.")


def seed_registrations_pasien(num_registration=3):
    """
    Seed the registrations_pasien collection with fake patient registrations.
    Args:
        num_registration (int): Number of registrations per user.
    """
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]
        status_choices = ['done', 'rejected', 'canceled', 'expired']
        for user in db.users.find({'role': 'pasien'}):
            # Ensure each user has at least one pending or approved registration
            has_pending_or_approved = db.registrations.find_one(
                {'username': user['username'], 'status': {'$in': ['pending', 'approved']}})
            if not has_pending_or_approved:
                registration_data = {
                    'username': user['username'],
                    'name': user['name'],
                    'nik': user['nik'],
                    'tgl_lahir': user['tgl_lahir'],
                    'gender': user['gender'],
                    'agama': user['agama'],
                    'status_pernikahan': user['status'],
                    'alamat': user['alamat'],
                    'no_telp': user['no_telp'],
                    'tanggal': (datetime.now()).strftime('%d-%m-%Y'),
                    'keluhan': fake.sentence(),
                    'status': fake.random_element(elements=['approved', 'pending'])
                }
                # Choose poli randomly from jadwal collection
                jadwal_poli = db.jadwal.aggregate([
                    {'$sample': {'size': 1}},
                    {'$project': {'_id': 0, 'poli': 1}}
                ]).next()
                registration_data['poli'] = jadwal_poli['poli']
                if registration_data['status'] in ['approved']:
                    # Calculate the antrian (queue number)
                    count_same_date_poli = db.registrations.count_documents({
                        'tanggal': registration_data['tanggal'],
                        'poli': registration_data['poli'],
                        'status': {'$in': ['approved', 'done']}
                    })
                    registration_data['antrian'] = f"{count_same_date_poli + 1:03d}"
                db.registrations.insert_one(registration_data)
            # Create more registrations for the same user
            for _ in range(random.randint(1, num_registration)):
                registration_data = {
                    'username': user['username'],
                    'name': user['name'],
                    'nik': user['nik'],
                    'tgl_lahir': user['tgl_lahir'],
                    'gender': user['gender'],
                    'agama': user['agama'],
                    'status_pernikahan': user['status'],
                    'alamat': user['alamat'],
                    'no_telp': user['no_telp'],
                    'tanggal': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%d-%m-%Y'),
                    'keluhan': fake.sentence(),
                    'status': fake.random_element(elements=status_choices)
                }
                # Choose poli randomly from jadwal collection
                jadwal_poli = db.jadwal.aggregate([
                    {'$sample': {'size': 1}},
                    {'$project': {'_id': 0, 'poli': 1}}
                ]).next()
                registration_data['poli'] = jadwal_poli['poli']
                if registration_data['status'] in ['approved', 'done']:
                    count_same_date_poli = db.registrations.count_documents({
                        'tanggal': registration_data['tanggal'],
                        'poli': registration_data['poli'],
                        'status': {'$in': ['approved', 'done']}
                    })
                    registration_data['antrian'] = f"{count_same_date_poli + 1:03d}"
                # Ensure not more 'done' than 'approved' registrations for the same user/date
                if registration_data['status'] == 'done':
                    approved_count = db.registrations.count_documents({
                        'username': user['username'],
                        'status': 'approved',
                        'tanggal': registration_data['tanggal']
                    })
                    done_count = db.registrations.count_documents({
                        'username': user['username'],
                        'status': 'done',
                        'tanggal': registration_data['tanggal']
                    })
                    if done_count >= approved_count:
                        continue
                if registration_data['status'] == 'expired':
                    # Set expired registration to random date in the past
                    registration_data['tanggal'] = (
                        datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%d-%m-%Y')
                    count_same_date_poli = db.registrations.count_documents({
                        'tanggal': registration_data['tanggal'],
                        'poli': registration_data['poli'],
                        'status': {'$in': ['approved', 'done']}
                    })
                    registration_data['antrian'] = f"{count_same_date_poli + 1:03d}"
                db.registrations.insert_one(registration_data)
        print("Registrations seeded.")


def approve_registrations():
    """
    Approve all pending registrations in the registrations_pasien collection.
    Sets status to 'approved' and assigns queue number (antrian).
    """
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]
        for registration in db.registrations.find({'status': 'pending'}):
            count_same_date_poli = db.registrations.count_documents({
                'tanggal': registration['tanggal'],
                'poli': registration['poli'],
                'status': {'$in': ['approved', 'done']}
            })
            registration['antrian'] = f"{count_same_date_poli + 1:03d}"
            db.registrations.update_one(
                {'_id': registration['_id']}, {'$set': {'antrian': registration['antrian'], 'status': 'approved'}})
        print("Registrations approved.")


def done_registrations():
    """
    Mark all approved registrations as done in the registrations_pasien collection.
    Sets status to 'done' and updates queue number (antrian).
    """
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]
        for registration in db.registrations.find({'status': 'approved'}):
            count_same_date_poli = db.registrations.count_documents({
                'tanggal': registration['tanggal'],
                'poli': registration['poli'],
                'status': {'$in': ['approved', 'done']}
            })
            registration['antrian'] = f"{count_same_date_poli + 1:03d}"
            db.registrations.update_one(
                {'_id': registration['_id']}, {'$set': {'antrian': registration['antrian'], 'status': 'done'}})
        print("Registrations done.")


def seed_rekam_medis():
    """
    Seed the rekam_medis collection for users with 'done' registrations.
    Each user gets a unique medical record number (no_kartu).
    """
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]
        for registration in db.registrations.find({'status': 'done'}):
            # Skip if rekam_medis already exists for this user
            existing_rekam_medis = db.rekam_medis.find_one(
                {'nik': registration['nik']})
            if existing_rekam_medis:
                continue
            # Calculate age from tgl_lahir
            tgl_lahir = datetime.strptime(
                registration['tgl_lahir'], '%d-%m-%Y')
            umur = (datetime.now() - tgl_lahir).days // 365
            # Generate unique nomor rekam medis
            nomor_rekam_medis = generate_nomor_rekam_medis()
            while db.rekam_medis.find_one({'no_kartu': nomor_rekam_medis}):
                nomor_rekam_medis = generate_nomor_rekam_medis()
            rekam_medis_data = {
                'no_kartu': nomor_rekam_medis,
                'username': registration['username'],
                'nama': registration['name'],
                'nik': registration['nik'],
                'umur': str(umur),
                'alamat': registration['alamat'],
                'no_telp': registration['no_telp'],
            }
            db.rekam_medis.insert_one(rekam_medis_data)
        print("Rekam medis seeded.")


def generate_nomor_rekam_medis():
    """
    Generate a unique 6-digit medical record number in the format XX-XX-XX.
    Returns:
        str: Medical record number.
    """
    nomor_rekam_medis = '-'.join([str(random.randint(0, 99)).zfill(2)
                                 for _ in range(3)])
    return nomor_rekam_medis


def seed_list_checkup_user():
    """
    Seed the list_checkup_user collection for users with 'done' registrations.
    Each entry links a patient, doctor, and checkup details.
    """
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]
        for registration in db.registrations.find({'status': 'done'}):
            has_checkup = db.list_checkup_user.find_one(
                {'nik': registration['nik'], 'tgl_periksa': registration['tanggal'], 'poli': registration['poli'], 'dokter': {'$exists': True}, 'hasil_anamnesa': {'$exists': True}, 'keluhan': registration['keluhan'], 'nama': registration['name']})
            if has_checkup:
                continue
            # Get doctor name from jadwal
            dokter_name = db.jadwal.aggregate([
                {'$match': {'poli': registration['poli']}},
                {'$sample': {'size': 1}},
                {'$project': {'_id': 0, 'nama': 1}}
            ]).next()['nama']
            checkup_data = {
                'nik': registration['nik'],
                'dokter': dokter_name,
                'hasil_anamnesa': fake.text(),
                'keluhan': registration['keluhan'],
                'nama': registration['name'],
                'poli': registration['poli'],
                'tgl_periksa': registration['tanggal'],
            }
            db.list_checkup_user.insert_one(checkup_data)
        print("List checkup user seeded.")


def recreate_database():
    """
    Drop and recreate all collections in the database.
    Clears users, jadwal, registrations, rekam_medis, list_checkup_user, and user_sessions.
    """
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]
        db.users.delete_many({})
        db.jadwal.delete_many({})
        db.registrations.delete_many({})
        db.rekam_medis.delete_many({})
        db.list_checkup_user.delete_many({})
        db.user_sessions.delete_many({})
        print("Collections cleared.")


# --- Main CLI Entrypoint ---
if __name__ == '__main__':
    # Parse command-line arguments for seeding options
    parser = argparse.ArgumentParser(
        description="Seed MongoDB database for Flask app.")
    parser.add_argument('--user', action='store_true',
                        help='Seed users collection')
    parser.add_argument('--jadwal', action='store_true',
                        help='Seed jadwal collection')
    parser.add_argument('--registration', action='store_true',
                        help='Seed registrations_pasien collection')
    parser.add_argument('--rekam-medis', action='store_true',
                        help='Seed rekam_medis collection'),
    parser.add_argument('--list-checkup-user', action='store_true',
                        help='Seed list_checkup_user collection'),
    parser.add_argument('--approve-registrations', action='store_true',
                        help='Approve all pending registrations')
    parser.add_argument('--done-registrations', action='store_true',
                        help='Done all approved registrations')
    parser.add_argument('--reload', action='store_true',
                        help='Drop and recreate the database')
    args = parser.parse_args()
    # Run selected seeding operations based on arguments
    if args.reload:
        recreate_database()
    if args.user:
        seed_users(num_pasien=100, num_pegawai=1)
    if args.jadwal:
        seed_jadwal(num_jadwal=20)
    if args.registration:
        seed_registrations_pasien(num_registration=1)
    if args.rekam_medis:
        seed_rekam_medis()
    if args.list_checkup_user:
        seed_list_checkup_user()
    if args.approve_registrations:
        approve_registrations()
    if args.done_registrations:
        done_registrations()
