export interface Example {
  id: string
  label: string
  caption: string
  profile: string
  job: string
}

export const examples: Example[] = [
  {
    id: 'strong',
    label: 'Profil kuat',
    caption: 'Beberapa kemampuan sudah punya bukti yang jelas.',
    profile:
      'Saya membuat dashboard penjualan menggunakan SQL untuk menulis query analisis dan Python untuk membersihkan data. Dalam proyek kampus, saya mempresentasikan hasil analisis kepada tim non-teknis dan menjelaskan tiga rekomendasi bisnis.',
    job:
      'Lowongan Data Analyst Intern. Dibutuhkan kemampuan SQL untuk menulis query analisis. Mampu menggunakan Python untuk membersihkan data. Mampu mempresentasikan hasil analisis kepada tim non-teknis. Pengalaman membuat dashboard menjadi nilai tambah.',
  },
  {
    id: 'gaps',
    label: 'Ada kesenjangan',
    caption: 'Rencana belajar memprioritaskan syarat yang belum terbukti.',
    profile:
      'Saya pernah mengolah data penjualan dengan Microsoft Excel dan membuat laporan mingguan untuk organisasi kampus. Saya juga menyampaikan temuan utama dalam rapat divisi setiap bulan.',
    job:
      'Lowongan Data Analyst Intern. Kandidat perlu menggunakan SQL untuk mengambil data dari database, Python untuk pembersihan data, dan membuat dashboard interaktif. Kemampuan menjelaskan temuan kepada pemangku kepentingan juga dibutuhkan.',
  },
  {
    id: 'ambiguous',
    label: 'Profil ambigu',
    caption: 'Pengalaman umum tidak otomatis dianggap bukti teknis.',
    profile:
      'Saya membantu tim menyusun laporan dan mendukung sebuah proyek analisis di kampus. Saya tertarik pada bidang data, belajar secara mandiri, dan ingin berkembang sebagai analis.',
    job:
      'Lowongan Business Intelligence Intern. Wajib mampu menulis query SQL, membangun visualisasi data, dan menjelaskan metrik bisnis kepada tim produk. Kandidat diharapkan teliti dalam mendokumentasikan definisi metrik.',
  },
]
