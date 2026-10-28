# IMMODERMA

Aplikasi klinik berbasis Django dan Microsoft SQL Server.

## Runtime yang didukung

- Python 3.12 sampai 3.14
- Django 5.2 LTS
- Microsoft ODBC Driver 18 for SQL Server
- SQL Server melalui `mssql-django`

Jangan deploy folder `venv/` atau `virtualenv/` dari Windows ke Ubuntu. Buat virtual environment baru di server.

## Konfigurasi

Salin nilai pada `.env.example` ke file environment yang hanya dapat dibaca oleh administrator, misalnya `/etc/immoderma/immoderma.env`. Jangan commit password database atau `SECRET_KEY`.

Minimal production wajib memiliki:

```text
IMMODERMA_DEBUG=false
IMMODERMA_SECRET_KEY=<random-secret>
IMMODERMA_ALLOWED_HOSTS=demo-medisismed.dsicorp.id
IMMODERMA_CSRF_TRUSTED_ORIGINS=https://demo-medisismed.dsicorp.id
IMMODERMA_DB_ENGINE=mssql
IMMODERMA_DB_NAME=IMMO
IMMODERMA_DB_HOST=<sql-server-host>
IMMODERMA_DB_USER=<sql-server-user>
IMMODERMA_DB_PASSWORD=<sql-server-password>
```

## Instalasi Ubuntu

```bash
sudo apt update
sudo apt install -y python3-venv unixodbc unixodbc-dev nginx
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py check --settings=IMMODERMA.settings_production
python manage.py collectstatic --noinput --settings=IMMODERMA.settings_production
```

Microsoft ODBC Driver 18 harus dipasang dari repository resmi Microsoft sesuai versi Ubuntu server. Fitur JasperReports bersifat opsional dan dipasang dengan `requirements-reporting.txt`; paket tersebut juga membutuhkan Java.

## Menjalankan lokal (Windows)

Pasang Microsoft ODBC Driver 18 dan pastikan SQL Server dapat diakses dari komputer pengembangan. Buat environment baru, isi konfigurasi database lewat environment variable, lalu jalankan server:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:IMMODERMA_DEBUG = 'true'
$env:IMMODERMA_SECRET_KEY = 'development-only-change-this'
$env:IMMODERMA_DB_NAME = 'IMMO'
$env:IMMODERMA_DB_HOST = '<sql-server-host>'
$env:IMMODERMA_DB_USER = '<sql-server-user>'
$env:IMMODERMA_DB_PASSWORD = '<sql-server-password>'
python manage.py check
python manage.py runserver
```

Buka `http://127.0.0.1:8000/`. Jangan gunakan `environment.py` untuk kredensial baru; file tersebut hanya dipertahankan sebagai kompatibilitas instalasi lama dan tidak ikut Git.

## Pemasukan realtime

Halaman baru tersedia di `/pemasukan_realtime/`. Halaman mengambil pembayaran pada cabang aktif, menyegarkan data setiap 30 detik, dan menyediakan **Export Excel** untuk tanggal yang dipilih. Bila menu belum terdaftar pada tabel privilege, akses URL tersebut secara langsung atau tambahkan menu dengan submodul `pemasukan_realtime` untuk kelompok pengguna yang berwenang.

Contoh unit systemd dan konfigurasi Nginx tersedia di `deploy/`. Sesuaikan lokasi `/opt/immoderma`, lalu aktifkan service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now immoderma
sudo nginx -t
sudo systemctl reload nginx
```

## Pemeriksaan setelah deploy

```bash
curl --fail https://demo-medisismed.dsicorp.id/health/
curl --fail https://demo-medisismed.dsicorp.id/health/database/
sudo journalctl -u immoderma -n 200 --no-pager
```

- `/health/` memeriksa proses Django tanpa mengakses database.
- `/health/database/` mengembalikan HTTP 503 bila SQL Server tidak dapat dihubungi.
- Log aplikasi disimpan secara rotasi di `DEBUG/immoderma.log`; log Gunicorn tetap tersedia di journal systemd.

## Pemeriksaan pengembangan

```bash
python manage.py check
python manage.py test
python -m compileall -q auth dashboard emr emrnew farmasi IMMODERMA pusdokkes setupdata
```
