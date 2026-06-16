# Sistem Pengelolaan Pasien dengan Flask dan MongoDB

## Deskripsi Proyek

Sistem Pengelolaan Pasien ini dirancang sebagai solusi inovatif untuk meningkatkan pengalaman pasien dan mengoptimalkan pengelolaan data di fasilitas kesehatan. Dengan menggunakan Flask sebagai framework utama dan MongoDB sebagai basis data, proyek ini bertujuan meningkatkan efisiensi pendaftaran pasien, kualitas layanan kesehatan, dan pengelolaan data pasien.

## Kelompok Google
- Muhammad Alif Budiman dari Universitas Negeri Jakarta (Ketua)
- Ahmad Iqbal Ferdinand Romadhon dari Institut Teknologi, Sains, dan Kesehatan RS.DR. Soepraoen Kesdam V/BRW
- Dea Elsiyani Pratiwi dari Universitas Kahuripan Kediri

#### API Docs:

[POSTMAN](https://documenter.getpostman.com/view/24748798/2s9YkuaeTS)
[SWAGGER](/apidocs) (tersedia setelah deploy — buka `https://<nama-service>.onrender.com/apidocs`)

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
- **Deploy:** Render.

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

### Kebutuhan Lokal

- Python 3.11.9+
- MongoDB Atlas (atau MongoDB lokal untuk pengembangan)

### Setup Lokal

1. Clone repository.
2. Buat virtual environment dan aktifkan:

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

3. Install dependensi:

```bash
pip install -r requirements.txt
```

4. Buat file `.env` dari contoh:

```bash
cp .env.example .env
# Edit .env dan isi nilai yang sesuai
```

Isi `.env`:

```
MONGODB_CONNECTION_STRING=mongodb+srv://USERNAME:PASSWORD@CLUSTER_HOST/?retryWrites=true&w=majority
DB_NAME=sistem_pengelolaan_pasien
TOKEN_KEY=access_token
SECRET_KEY=<generate dengan perintah di bawah>
FLASK_DEBUG=false
PORT=5000
```

Generate `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

5. Jalankan seeder (opsional):

```bash
python seeder.py
```

6. Jalankan aplikasi (mode pengembangan):

```bash
python app.py
```

7. Akses melalui browser: [http://localhost:5000](http://localhost:5000)

### Perintah Produksi Lokal (Linux/WSL)

```bash
PORT=8000 gunicorn -w 1 --threads 20 --timeout 120 --bind 0.0.0.0:$PORT app:app
```

---

## Konfigurasi Render

| Pengaturan         | Nilai                                                                             |
|--------------------|-----------------------------------------------------------------------------------|
| Runtime            | Python 3.11.9                                                                     |
| Region             | Singapore                                                                         |
| Plan               | Free                                                                              |
| Build Command      | `pip install --upgrade pip && pip install -r requirements.txt`                   |
| Start Command      | `gunicorn -w 1 --threads 20 --timeout 120 --bind 0.0.0.0:$PORT app:app`         |
| Health Check Path  | `/health`                                                                         |

### Environment Variables di Render

| Nama                       | Keterangan                                   |
|----------------------------|----------------------------------------------|
| `MONGODB_CONNECTION_STRING` | Connection string MongoDB Atlas              |
| `DB_NAME`                   | Nama database                               |
| `TOKEN_KEY`                 | Nama field token JWT di cookie              |
| `SECRET_KEY`                | Secret key untuk signing JWT                |

### MongoDB Atlas — Network Access

Setelah service Render dibuat:

1. Buka dashboard Render, temukan **Outbound IP addresses** service Anda.
2. Buka MongoDB Atlas → **Network Access** → **Add IP Address**.
3. Tambahkan semua rentang CIDR outbound Render (bukan `0.0.0.0/0` secara permanen).
4. Pastikan database user Atlas hanya memiliki izin minimum yang dibutuhkan aplikasi ini.

> **Catatan:** `0.0.0.0/0` dapat digunakan sementara saat pengujian awal, tetapi harus diganti dengan IP spesifik Render secepatnya.

---

## Keterbatasan Render Free

| Keterbatasan                | Detail                                                                               |
|-----------------------------|--------------------------------------------------------------------------------------|
| **Spin-down**               | Service mati otomatis setelah ~15 menit tidak aktif. Request pertama memerlukan cold start ~30–60 detik. |
| **Filesystem efemeral**     | Semua file yang diupload (termasuk foto profil) akan **hilang** setelah restart atau redeploy. |
| **Foto profil**             | Gunakan hanya data demo. Untuk produksi, migrasikan penyimpanan file ke Cloudinary atau AWS S3. |
| **Data pasien**             | Deployment publik hanya boleh menggunakan data dummy/demo, bukan data pasien nyata. |

## Kontribusi

Silakan berkontribusi dengan melakukan _pull request_ ke repositori ini. Jangan ragu untuk melaporkan _issue_ jika menemui masalah.

--- 

**Proyek ini dikembangkan sebagai bagian dari program MSIB LearningX Full Stack Web Development.**