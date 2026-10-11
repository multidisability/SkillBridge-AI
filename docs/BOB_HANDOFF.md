# Panduan melanjutkan proyek di IBM Bob

Repo ini disiapkan agar dapat dibuka dan dikembangkan dengan IBM Bob. Pembuatan kode di workspace ini belum menghasilkan riwayat percakapan IBM Bob; jangan menyajikan tangkapan layar atau log prompt rekaan sebagai bukti submission.

## Langkah di Bob

1. Buka folder `skillbridge-ai` di IBM Bob IDE. Lampirkan PDF materi sesi 3 dari folder induk sebagai konteks.
2. Di **Ask mode**, minta Bob menjelaskan arsitektur dari `docs/SDD.md` dan mengidentifikasi bagian yang belum sesuai rubrik capstone.
3. Di **Plan mode**, berikan prompt tiga lapis berikut untuk rencana perubahan yang spesifik.
4. Di **Agent mode**, implementasikan satu perubahan per putaran; jalankan tes dan simpan bukti perubahan prompt serta hasilnya.

### Prompt tiga lapis untuk Bob

**Layer 1 — Role & Context**

> Bertindak sebagai senior full-stack engineer untuk capstone IBM SkillsBuild. Proyek ini bernama SkillBridge AI, ditujukan bagi mahasiswa Indonesia yang ingin memetakan bukti keterampilan terhadap lowongan magang. Baca `docs/SDD.md` dan pertahankan kontrak API yang ada.

**Layer 2 — Task & Requirements**

> Tinjau alur input profil + lowongan → ekstraksi syarat → pencocokan bukti → rencana belajar 7 hari. Perbaiki satu masalah yang saya sebutkan pada setiap iterasi. Pastikan setiap status `supported` mempunyai kutipan profil yang benar-benar berasal dari input. Jalankan tiga contoh anonim dan tes backend.

**Layer 3 — Constraints & Output**

> Gunakan React + Vite + TypeScript, CSS biasa, FastAPI, Pydantic, dan SDK `google-genai`. Simpan `GEMINI_API_KEY` di server. Jangan menambah akun atau database pada MVP. Tunjukkan diff, hasil tes, dan alasan perubahan. Perbarui SDD bila perilaku publik berubah.

## Catatan iterasi yang perlu diisi saat Bob digunakan

| Versi | Masalah yang terlihat | Layer yang diubah | Perubahan prompt/kode | Hasil tes/demo |
|---|---|---|---|---|
| v1 | Isi setelah demo pertama | Isi | Isi | Isi |
| v2 | Isi setelah revisi akurasi | Isi | Isi | Isi |
| v3 | Isi setelah revisi UX | Isi | Isi | Isi |

Simpan tangkapan layar riwayat prompt Bob, diagram sistem, dan keluaran demo yang benar-benar dijalankan. Berkas pendukung submission dijelaskan di `SUBMISSION_CHECKLIST.md`.
