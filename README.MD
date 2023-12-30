# Sistem Pengelolaan Pasien dengan Flask dan MongoDB

## Deskripsi Proyek

Sistem Pengelolaan Pasien ini dirancang sebagai solusi inovatif untuk meningkatkan pengalaman pasien dan mengoptimalkan pengelolaan data di fasilitas kesehatan. Dengan menggunakan Flask sebagai framework utama dan MongoDB sebagai basis data, proyek ini bertujuan meningkatkan efisiensi pendaftaran pasien, kualitas layanan kesehatan, dan pengelolaan data pasien.

#### API Docs:

[POSTMAN](https://documenter.getpostman.com/view/24748798/2s9YkuaeTS)
[SWAGGER](https://klinik-google.glitch.me/apidocs)

## Tujuan

1. Meningkatkan efisiensi dalam proses pendaftaran pasien melalui antarmuka yang user-friendly.
2. Meningkatkan kualitas layanan kesehatan.
3. Meningkatkan efisiensi dalam pengelolaan data pasien yang diperlukan.

## Manfaat

- **Untuk Pasien:** Mempermudah proses pendaftaran.
- **Untuk Pengelola Klinik:** Mempermudah dalam mengorganisir data-data pasien.

## Teknologi yang Digunakan

- **Bahasa Pemrograman:** HTML, CSS, Javascript, dan Python.
- **Database:** MongoDB.
- **Framework:** Flask.
- **Deploy:** Glitch.

## Fitur

1. **Autentikasi:**

   - Register akun pasien.
   - Login akun pegawai & pasien.

2. **Beranda:**

   - Homepage (landing page).
     Halaman ini berisi layanan klinik, tata cara pendaftaran, jadwal praktik dokter, dan antrian hari ini.

3. **Pendaftaran Pasien:**

   - Pendaftaran pasien.
   - Cancel pendaftaran.

4. **Riwayat:**

   - Riwayat pendaftaran pasien.
   - Riwayat checkup pasien.

5. **Profil:**

   - Lihat dan edit profil.

6. **Kelola Pendaftaran Pasien:**

   - Approve pendaftaran pasien.
   - Reject pendaftaran pasien.
   - Done pendaftaran pasien.

7. **Admin Dashboard:**

   - Dashboard admin.

8. **Export Data:**

   - Export data pendaftaran pasien ke CSV.
   - Export data checkup pasien ke CSV.

9. **Rekam Medis:**

   - Buat rekam medis pasien.
   - Edit checkup pasien.

10. **Kelola Jadwal Praktik Dokter:**
   - CRUD operasi untuk jadwal praktik dokter.

11. **Real-Time:**
   - Perubahan data dilakukan tanpa perlu refresh halaman

## Panduan Penggunaan

1. Pastikan Python, Flask, dan MongoDB telah terinstal.
2. Clone Repository
3. Install venv

```
python3 -m venv your_venv_name
```

3. Aktifkan venv

```
source venv/bin/activate # for macos and linux
```

4. Install semua library yang diperlukan dengan menjalankan `pip install -r requirements.txt`.
5. Konfigurasi file `.env` dengan informasi yang sesuai.

```
# Database configuration
MONGODB_CONNECTION_STRING=your_mongodb_uri
DB_NAME=your_database_name
SECRET_KEY=your_secret_key
TOKEN_KEY=your_token_key
```

6. Jalankan seeder (opsional)
7. Jalankan aplikasi dengan perintah `python app.py`.
8. Akses aplikasi melalui browser dengan URL [http://localhost:5000](http://localhost:5000).

## Kontribusi

Silakan berkontribusi dengan melakukan _pull request_ ke repositori ini. Jangan ragu untuk melaporkan _issue_ jika menemui masalah.
