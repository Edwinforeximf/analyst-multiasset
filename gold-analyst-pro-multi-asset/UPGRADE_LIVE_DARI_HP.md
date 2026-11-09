# Gold Analyst Pro — Live Data V2 (Upgrade Railway dari HP)

**Tujuan:** Aplikasi yang sama, akun dan laporan lama tetap aman. Tambahkan mode harga pasar indikatif (bukan kuotasi broker) untuk XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, USOIL. Mode screenshot tetap tersedia. Status arah publik tampil **BUY/SELL Bias**; keputusan apakah skenario layak dieksekusi tetap terpisah.

## Cara update tanpa menghapus data

1. Simpan cadangan repository dan, bila sudah ada, backup Railway Volume `/data` beserta database `reports.db`.
2. Ekstrak ZIP; folder di dalamnya **gold-analyst-pro-multi-asset**. Jangan mengupload ZIP saja ke GitHub. Di repository yang sudah digunakan oleh Railway, buka folder tempat `app.py` dan `Dockerfile` berada. **Ganti** `app.py`, `ai_engine.py`, `visuals.py`, `export_docx.py`, `static/index.html`, dan `Dockerfile`. **Tambahkan** `market_feed.py` dan `live_engine.py` dalam folder yang sama dengan `app.py`. Untuk mempermudah, upload seluruh isi folder baru, tapi jangan menimpa folder data/volume.
3. Railway → Service → Settings: biarkan **Root Directory** yang sekarang sudah berhasil. Jika struktur upload sama seperti paket awal, root biasanya `/gold-analyst-pro-multi-asset`. Builder: Dockerfile pada folder itu.
4. Railway → **Variables**: pertahankan `APP_SECRET`, `SETUP_TOKEN`, `GEMINI_API_KEY`, `COOKIE_SECURE=1`, `STORAGE_DIR=/data`. **Jangan mengganti `APP_SECRET`** atau sesi login akan terputus. Jangan buat admin lagi; akun lama tetap ada di volume.
5. Tambahkan `TWELVEDATA_API_KEY` dari https://twelvedata.com/. Contoh konfigurasi: `MAX_QUOTE_AGE_SECONDS=300`. `LIVE_SYMBOL_USOIL=WTI/USD` hanya perlu jika ingin override; default sudah WTI/USD sesuai katalog Twelve Data. Verifikasi akun/paketmu memberi akses data **WTI/USD** serta candle intraday.
6. (Opsional) `GEMINI_LIVE_EDITORIAL=1` untuk penyuntingan *narasi* oleh Gemini. Default `0` agar level harga dan teks teknikal murni perhitungan transparan. Mode Screenshot tetap menggunakan Gemini.
7. **Commit changes**. Lihat Railway Build Logs dan Deploy Logs terbaru sampai `Application startup complete` lalu tes `https://<domain-railway>/health`.
8. Login akun admin lama → Generate → **Live Feed** → pilih EURUSD → **Cek Harga & Waktu** → **Generate Live BUY/SELL Outlook**. Setelah berhasil uji dokumen DOCX. Coba instrumen lain sesuai akses akunmu.

## Apa arti BUY / SELL di versi ini?

- **BUY/SELL adalah bias arah teknikal** berdasarkan EMA9/EMA21 D1, H4, H1 + indikator RSI dan ATR.
- **Kelayakan eksekusi adalah status terpisah**: lulus filter atau BELUM SIAP EKSEKUSI. Tidak ada tombol trading otomatis, tidak ada transaksi dan tidak ada klaim akurasi tertentu.
- Proyeksi Entry/SL/TP dari indikator teknikal, **bukan harga yang bisa dieksekusi**. Reviewer harus memeriksa bid/ask, spread, volatilitas, margin dan sumber berita sebelum dipublikasikan. Jika API tidak tersedia atau tanggal harga kedaluwarsa, generator **gagal dengan pesan jelas**, bukan mengarang sinyal.
- Selain hasil valid, riset bias saja juga bisa dikirim untuk **review**, tetapi itu tidak berarti sinyal transaksi siap pakai.

## Ketentuan data penting untuk broker

- Twelve Data menyediakan quote indikatif dan OHLC agregat; bukan harga MT5/CFD broker kamu. Nama USOIL alias internal dapat berbeda dari spot WTI/USD, termasuk spread, sesi, kontrak dan rollover. Jangan membandingkan seolah sama.
- **Lisensi redistribusi/public display berbeda dari akses API internal.** Pastikan izin penggunaan komersial dan publikasi ke nasabah sebelum menampilkan ulang quote di website/konten pemasaran. Tinjau paket di https://twelvedata.com/pricing dan kebijakan licensinya; jangan mengasumsikan tier gratis mengizinkan publikasi.
- Pengujian memakai mock candle; **belum ada panggilan API real** di paket sumber ini, sehingga ketersediaan symbol dan harga aktual harus diuji dengan API key kamu.
- Penggunaan API mencakup ~4 request per generate (1 quote + D1/H4/H1), tambah 1 request bila tombol Cek Harga dipakai. Batas gratis bisa tercapai. Output data live internal bukan stream per-tick; quote dianggap valid maksimal 5 menit (bisa diubah).
- Opsi jangka panjang yang lebih cocok: **feed broker resmi / MT5 bridge** (dengan izin broker) untuk bid, ask, spread, tick, dan candle yang sama dengan platform nasabah. Integrasi MT5 Python memakai terminal MT5, bukan memasang paket MT5 langsung pada Railway Linux.

## Struktur file yang berubah

```text
app.py                     # routes screenshot dan live, migrasi DB aman
market_feed.py             # Twelve Data API + validasi timestamp/quote/OHLC
live_engine.py             # BUY/SELL bias deterministik, scenario levels dan readiness
ai_engine.py               # engine screenshot lama
visuals.py                 # chart data live terkalibrasi + render premium
export_docx.py             # TXT/DOCX (hasil live dan screenshot)
static/index.html          # pemilih Live / Screenshot, quote source, reports
Dockerfile                 # COPY modul market_feed dan live_engine
```

## Bila ada error

- `TWELVEDATA_API_KEY belum dikonfigurasi`: isi di Railway Variables (bukan GitHub).
- `429`, `credits`, atau `plan`: quota/provider tidak mencukupi.
- `USOIL` atau `WTI/USD` tidak tersedia: periksa paket/data symbol provider dan mapping `LIVE_SYMBOL_USOIL`.
- `Harga kedaluwarsa` / `Candle ... kedaluwarsa`: pasar libur/tertutup atau data terlambat; tidak membuat analisis live.
- `No module named 'market_feed'`: Dockerfile belum disalin atau file berada di folder yang salah.
- `APP_SECRET wajib diisi`: pertahankan variabel Railway dari deploy sebelumnya.
- Setelah berhasil, bila tampilan Android lama masih muncul, reload penuh Chrome / cache PWA (berkaitan dengan service worker).
