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

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

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

# How to use

# Seed all collections
# python3 seeder.py --user --jadwal --registration --rekam-medis --list-checkup-user

# Recreate database
# python3 seeder.py --user --jadwal --registration --rekam-medis --list-checkup-user --reload

# Seed users collection
# python3 seeder.py --user

# Seed jadwal collection
# python3 seeder.py --jadwal

# Seed registrations_pasien collection
# python3 seeder.py --registration

# Seed rekam_medis collection
# python3 seeder.py --rekam-medis

# Seed list_checkup_user collection
# python3 seeder.py --list-checkup-user

fake = Faker('id_ID')

# Function to generate fake user data
def generate_fake_user(role):
    db = mongo.cx[app.config['MONGO_DBNAME']]
    while True:
        username = fake.unique.user_name()
        nik = str(fake.unique.random_number(16))

        # Check if the generated username or nik already exists in the database
        existing_user = db.users.find_one(
            {'$or': [{'username': username}, {'nik': nik}]})

        if existing_user is None:
            break
    password = "$2b$10$xm2V57w6d8/Q4RzMYp9GDeiahaWW5HLmD1TxaS2TLurYXscUAATHS"  # Password.12
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

# Function to seed the users collection with a specific number of users for each role
def seed_users(num_pasien=10, num_pegawai=2):
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]
        roles = {'pasien': num_pasien, 'pegawai': num_pegawai}

        for role, count in roles.items():
            for _ in range(count):
                user_data = generate_fake_user(role)
                db.users.insert_one(user_data)

        print("Users seeded.")


# Function to seed the jadwal collection
def seed_jadwal(num_jadwal=3):
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]
        poli_choices = ['Umum', 'Gigi', 'Mata', 'Jantung', 'THT',
                        'Syaraf', 'Kesehatan Jiwa', 'Anak', 'Fisioterapi']
        hari_choices = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat']

        for _ in range(num_jadwal):  # Adjust the number of jadwal entries as needed
            # Generate random time values
            jam_buka = fake.time(pattern="%H:%M")
            jam_tutup = fake.time(pattern="%H:%M")

            # Ensure jam_buka is less than jam_tutup
            while jam_buka >= jam_tutup:
                jam_buka = fake.time(pattern="%H:%M")
                jam_tutup = fake.time(pattern="%H:%M")

            # Calculate the difference between jam_buka and jam_tutup
            time_format = "%H:%M"
            diff = datetime.strptime(
                jam_tutup, time_format) - datetime.strptime(jam_buka, time_format)

            # Ensure the difference is at least 2 hours and at most 4 hours
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


# Function to seed the registrations_pasien collection
def seed_registrations_pasien(num_registration=3):
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]
        status_choices = ['pending', 'approved', 'done', 'rejected']

        for user in db.users.find({'role': 'pasien'}):
            for _ in range(random.randint(1, num_registration)):
                # Check if the user already has a pending registration for today
                pending_registration = db.registrations.find_one({
                    'username': user['username'],
                    'status': 'pending'
                })

                if pending_registration:
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
                        'tanggal': (datetime.now() - timedelta(days=random.randint(0, 3))).strftime('%d-%m-%Y'),
                        'keluhan': fake.sentence(),
                        'status': fake.random_element(elements=['approved', 'done', 'rejected'])
                    }

                    # Choose poli randomly from jadwal collection
                    jadwal_poli = db.jadwal.aggregate([
                        {'$sample': {'size': 1}},
                        {'$project': {'_id': 0, 'poli': 1}}
                    ]).next()

                    registration_data['poli'] = jadwal_poli['poli']

                    if registration_data['status'] in ['approved', 'done']:
                        # Calculate the antrian based on the number of registrations for the same date and poli
                        count_same_date_poli = db.registrations.count_documents({
                            'tanggal': registration_data['tanggal'],
                            'poli': registration_data['poli'],
                            'status': {'$in': ['approved', 'done']}
                        })

                        registration_data['antrian'] = f"{count_same_date_poli + 1:03d}"
                    # Check if there are more "done" registrations than "approved" registrations on the same date
                    if registration_data['status'] == 'done':
                        rekam_medis_exists = bool(db.rekam_medis.find_one(
                            {'nik': user['nik']}))
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

                        if not rekam_medis_exists:
                            continue

                        if done_count >= approved_count:
                            continue  # Skip this registration if the "done" count is greater or equal to "approved"
                    db.registrations.insert_one(registration_data)

                else:
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
                        'tanggal': (datetime.now() - timedelta(days=random.randint(0, 3))).strftime('%d-%m-%Y'),
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
                        # Calculate the antrian based on the number of registrations for the same date and poli
                        count_same_date_poli = db.registrations.count_documents({
                            'tanggal': registration_data['tanggal'],
                            'poli': registration_data['poli'],
                            'status': {'$in': ['approved', 'done']}
                        })

                        registration_data['antrian'] = f"{count_same_date_poli + 1:03d}"

                    if registration_data['status'] == 'pending':
                        # Set only one registration as pending for today
                        registration_data['tanggal'] = datetime.now().strftime(
                            '%d-%m-%Y')

                    # Check if there are more "done" registrations than "approved" registrations on the same date
                    if registration_data['status'] == 'done':
                        rekam_medis_exists = bool(db.rekam_medis.find_one(
                            {'nik': user['nik']}))
                        registration_data_exists = bool(db.registrations.find_one(
                            {'username': user['username'], 'status': ['done']}))
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

                        if not rekam_medis_exists and registration_data_exists:
                            continue

                        if done_count >= approved_count:
                            continue  # Skip this registration if the "done" count is greater or equal to "approved"
                    db.registrations.insert_one(registration_data)

        print("Registrations seeded.")


# Function to seed the rekam_medis collection
def seed_rekam_medis():
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]

        # Iterate through the registrations_pasien collection
        for registration in db.registrations.find({'status': 'done'}):
            # Check if rekam_medis already exists for this user
            existing_rekam_medis = db.rekam_medis.find_one(
                {'nik': registration['nik']})

            if existing_rekam_medis:
                continue  # Skip if rekam_medis already exists for this user

            # Calculate umur based on tgl_lahir
            tgl_lahir = datetime.strptime(
                registration['tgl_lahir'], '%d-%m-%Y')
            umur = (datetime.now() - tgl_lahir).days // 365

            # Generate nomor rekam medis
            nomor_rekam_medis = generate_nomor_rekam_medis()

            # Create rekam_medis data
            rekam_medis_data = {
                'no_kartu': nomor_rekam_medis,
                'nama': registration['name'],
                'nik': registration['nik'],
                'umur': str(umur),
                'alamat': registration['alamat'],
                'no_telp': registration['no_telp'],
            }

            # Insert rekam_medis data into the rekam_medis collection
            db.rekam_medis.insert_one(rekam_medis_data)

        print("Rekam medis seeded.")


# Function to generate nomor rekam medis
def generate_nomor_rekam_medis():
    # Assuming 6-digit nomor rekam medis with the format XX-XX-XX
    nomor_rekam_medis = '-'.join([str(random.randint(0, 99)).zfill(2)
                                 for _ in range(3)])
    return nomor_rekam_medis

# Function to seed the list_checkup_user collection
def seed_list_checkup_user():
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]

        # Iterate through the registrations_pasien collection with status 'done'
        for registration in db.registrations.find({'status': 'done'}):

            # Get dokter name from jadwal
            jadwal = db.jadwal.find_one({'poli': registration['poli']})
            dokter_name = jadwal['nama']

            # Create list_checkup_user data
            checkup_data = {
                'nik': registration['nik'],
                'dokter': dokter_name,
                'hasil_anamnesa': fake.text(),
                'keluhan': fake.sentence(),
                'nama': registration['name'],
                'poli': registration['poli'],
                'tgl_periksa': registration['tanggal'],
            }

            # Insert list_checkup_user data into the list_checkup_user collection
            db.list_checkup_user.insert_one(checkup_data)

        print("List checkup user seeded.")

# Function to drop and recreate the database
def recreate_database():
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]
        db.users.delete_many({})
        db.jadwal.delete_many({})
        db.registrations.delete_many({})
        db.rekam_medis.delete_many({})
        db.list_checkup_user.delete_many({})
        print("Collections cleared.")


if __name__ == '__main__':
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
    parser.add_argument('--list-checkup-user', action='store_true', help='Seed list_checkup_user collection'),
    parser.add_argument('--reload', action='store_true',
                        help='Drop and recreate the database')

    args = parser.parse_args()

    if args.reload:
        recreate_database()

    if args.user:
        seed_users(num_pasien=20, num_pegawai=2)

    if args.jadwal:
        seed_jadwal(num_jadwal=15)

    if args.registration:
        seed_registrations_pasien(num_registration=50)

    if args.rekam_medis:
        seed_rekam_medis()

    if args.list_checkup_user:
        seed_list_checkup_user()
