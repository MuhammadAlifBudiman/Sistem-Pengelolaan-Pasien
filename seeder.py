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
def seed_jadwal():
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]
        poli_choices = ['umum', 'gigi', 'mata']
        hari_choices = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat']

        for _ in range(3):  # Adjust the number of jadwal entries as needed
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
def seed_registrations_pasien():
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]
        status_choices = ['pending', 'approved', 'done', 'rejected']
        poli_choices = ['umum', 'gigi', 'mata']

        for user in db.users.find({'role': 'pasien'}):
            for _ in range(random.randint(1, 3)):
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
                        'poli': fake.random_element(elements=poli_choices),
                        'tanggal': (datetime.now() - timedelta(days=random.randint(0, 3))).strftime('%Y-%m-%d'),
                        'keluhan': fake.sentence(),
                        'status': fake.random_element(elements=['approved', 'done', 'rejected'])
                    }

                    if registration_data['status'] in ['approved', 'done']:
                        # Calculate the antrian based on the number of registrations for the same date and poli
                        count_same_date_poli = db.registrations.count_documents({
                            'tanggal': registration_data['tanggal'],
                            'poli': registration_data['poli'],
                            'status': {'$in': ['approved', 'done']}
                        })

                        registration_data['antrian'] = f"{count_same_date_poli + 1:03d}"
                        print(registration_data['antrian'])
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
                        'poli': fake.random_element(elements=poli_choices),
                        'tanggal': (datetime.now() - timedelta(days=random.randint(0, 3))).strftime('%Y-%m-%d'),
                        'keluhan': fake.sentence(),
                        'status': fake.random_element(elements=status_choices)
                    }

                    if registration_data['status'] in ['approved', 'done']:
                        # Calculate the antrian based on the number of registrations for the same date and poli
                        count_same_date_poli = db.registrations.count_documents({
                            'tanggal': registration_data['tanggal'],
                            'poli': registration_data['poli'],
                            'status': {'$in': ['approved', 'done']}
                        })

                        registration_data['antrian'] = f"{count_same_date_poli + 1:03d}"
                        print(registration_data['antrian'])
                    
                    if registration_data['status'] == 'pending':
                        # Set only one registration as pending for today
                        registration_data['tanggal'] = datetime.now().strftime('%Y-%m-%d')
                    db.registrations.insert_one(registration_data)

        print("Registrations seeded.")

# Function to drop and recreate the database
def recreate_database():
    with app.app_context():
        db = mongo.cx[app.config['MONGO_DBNAME']]
        db.users.delete_many({})
        db.jadwal.delete_many({})
        db.registrations.delete_many({})
        print("Collections cleared.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Seed MongoDB database for Flask app.")
    parser.add_argument('--reload', action='store_true',
                        help='Drop and recreate the database')

    args = parser.parse_args()

    if args.reload:
        recreate_database()

    seed_users()
    seed_jadwal()
    seed_registrations_pasien()
