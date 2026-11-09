# Instal Gold Analyst Pro Baru — Langsung dari HP Android

Aplikasi ini adalah **proyek baru**, bukan update yang menimpa Railway lama. Dashboard lama dan data lama tetap ada.

## Langkah 1 — GitHub

1. Download ZIP dan ekstrak lewat File Manager HP.
2. Buka https://github.com/new → buat repository private, misalnya `gold-analyst-multiasset`.
3. Upload **isi folder proyek** ke repository baru. Saat membuka repo, `Dockerfile`, `app.py`, `ai_engine.py`, `visuals.py`, `export_docx.py`, `static/`, `android-app/`, dan `.github/workflows/` harus berada di root. Jika folder tidak terupload lewat tampilan mobile, aktifkan **Situs desktop** pada Chrome.

## Langkah 2 — Railway

1. https://railway.com/dashboard → **New Project** → **Deploy from GitHub repo**, pilih repo baru.
2. Dockerfile ada di root. Kalau terlihat "Railpack failed" cek apakah repository berisi folder tambahan. Jangan gunakan Root Directory dari repo lama.
3. Tambahkan Railway Volume di service baru dengan mount `/data` untuk menyimpan database, screenshot, dan logo.
4. Di **Variables** isi nilai pribadi (jangan simpan di GitHub / chat):
   - `GEMINI_API_KEY` → API key dari https://aistudio.google.com/api-keys
   - `GEMINI_MODEL` → `gemini-3.8-flash` (cek apakah tersedia untuk key kamu)
   - `APP_SECRET` → string acak yang panjang
   - `SETUP_TOKEN` → kode rahasia yang akan kamu pakai saat pertama kali membuat admin
   - `COOKIE_SECURE` → `1`
   - `STORAGE_DIR` → `/data`
5. Generate Domain pada **Settings → Networking**. Cek `https://DOMAIN-KAMU/health` dan buka dashboard.
6. Isi form **Buat Admin Pertama**, termasuk kode `SETUP_TOKEN` yang kamu buat sendiri. Upload logo QuickPro satu kali.

## Langkah 3 — Tes 6 instrumen

Pilih XAUUSD / XAGUSD / EURUSD / GBPUSD / USDJPY / USOIL → upload D1, H4, H1 (M15 opsional) → Generate. Review hasil dan sumbu harga, lalu unduh PNG atau DOCX. Form tidak meminta entry manual.

## Langkah 4 — Android APK

GitHub repo baru → tab **Actions** → **Build Gold Analyst Pro APK** → **Run workflow** → download artifact `GoldAnalystPro-debug-APK` → ekstrak ZIP → install APK di HP. Saat pertama dibuka, masukkan **domain Railway baru**. APK tidak disertakan sebelum workflow berhasil membangunnya.

## Alternatif langsung dipakai dari HP

Tanpa APK pun, setelah dashboard Railway online kamu dapat membuka Chrome → menu **Tambahkan ke layar utama / Install app**. Ini menampilkan ikon aplikasi dari PWA dan memakai backend yang sama.

## Catatan penting

- Proses `Generate` masih perlu API Gemini; dukungan free tier tergantung kuota dan model.
- Hasil screenshot **bukan harga live**. Garis chart hanya ditampilkan jika kalibrasi sumbu cukup konsisten, lalu tetap perlu validasi manusia.
- Karena proyek baru, user dan laporan dari Railway lama **tidak ikut pindah otomatis**.
- APK dari GitHub Actions adalah **debug APK untuk internal**, bukan APK release bertanda tangan untuk Google Play.
