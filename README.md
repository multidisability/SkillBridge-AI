# SkillBridge AI

SkillBridge AI membantu mahasiswa membandingkan pengalaman yang mereka tulis dengan syarat lowongan magang. Hasilnya menampilkan kutipan bukti untuk setiap keterampilan dan rencana belajar tujuh hari. Ini adalah prototipe capstone Hacktiv8 × IBM SkillsBuild yang disiapkan untuk dilanjutkan di IBM Bob.

## Yang sudah tersedia

- React, Vite, dan TypeScript untuk satu halaman analisis yang responsif.
- FastAPI untuk `POST /api/analyze` dan penyajian hasil build frontend.
- Dua tahap Gemini: ekstraksi syarat lowongan, lalu pencocokan bukti serta rencana belajar.
- JSON terstruktur dengan Pydantic dan pemeriksaan kutipan terhadap teks sumber.
- Tiga pasangan data anonim untuk demo. Tidak ada akun, database, atau penyimpanan profil.

IBM Bob adalah alat pengembangan proyek. Gemini merupakan model yang dipanggil saat pengguna menjalankan analisis. Dokumentasi penggunaan Bob ada di [`docs/BOB_HANDOFF.md`](docs/BOB_HANDOFF.md). Rancangan teknis ada di [`docs/SDD.md`](docs/SDD.md).

## Persiapan Windows PowerShell

Prasyarat: Python 3.11+, Node.js 20.19+ atau 22.12+, Git, dan Gemini API key. Instalasi dependensi dilakukan di folder proyek.

```powershell
cd skillbridge-ai
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
cd frontend
npm install
```

Atur `GEMINI_API_KEY` sebagai environment variable di terminal yang akan menjalankan backend. Jangan memasukkan kunci ke source code, `.env` yang dikomit, atau frontend.

```powershell
$env:GEMINI_API_KEY = "isi-kunci-anda"
```

Terminal 1, dari folder `skillbridge-ai/backend`:

```powershell
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Terminal 2, dari folder `skillbridge-ai/frontend`:

```powershell
npm run dev
```

Buka alamat yang ditampilkan Vite, biasanya `http://localhost:5173`. Vite meneruskan `/api` ke backend pada port 8000. Pilih salah satu contoh atau masukkan teks anonim sendiri. Jika kunci belum diatur, API memberi pesan konfigurasi yang jelas.

## Satu server untuk demo

Setelah frontend dibangun, FastAPI otomatis menyajikan hasil build pada `http://127.0.0.1:8000`:

```powershell
cd frontend
npm run build
cd ..\backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```

## Menjalankan pemeriksaan

```powershell
cd skillbridge-ai\frontend
npm run build
cd ..\backend
..\.venv\Scripts\python.exe -m pytest -q
```

Tes memakai respons model tiruan; tes tidak menghabiskan kuota Gemini. Pengujian live perlu kunci sendiri dan teks contoh anonim.

## Batasan hasil

Status **belum terbukti** berarti teks profil tidak memberikan bukti eksplisit, bukan kesimpulan tentang kemampuan seseorang. Aplikasi mengirim teks yang dimasukkan ke Gemini untuk diproses. Gunakan teks anonim dan jangan memasukkan data pribadi sensitif. Aplikasi tidak menyimpan teks profil atau lowongan.

Untuk submission, lihat [`docs/SUBMISSION_CHECKLIST.md`](docs/SUBMISSION_CHECKLIST.md). Tangkapan layar IBM Bob dan video harus direkam dari proses penggunaan yang sebenarnya.
