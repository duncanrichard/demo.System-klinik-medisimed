# Filter antrean Apoteker

## Tujuan

Memudahkan apoteker melihat antrean BMHP pada tanggal tertentu dan meninjau apakah suatu treatment sudah disiapkan.

## Rancangan

- Filter `Tanggal` menggunakan tanggal transaksi dan secara default diisi hari ini.
- Filter `Aksi` menyediakan Semua, Belum disiapkan, dan Sudah disiapkan. Nilai awalnya Belum disiapkan agar halaman tetap menjadi antrean kerja.
- Tabel dibagi menjadi 10 baris per halaman. Parameter filter dan halaman dipertahankan ketika pengguna menandai BMHP sebagai sudah disiapkan.
- Status disimpan dari tabel `APOTEKER_PERSIAPAN_BMHP`; tidak ada data status buatan.
- Tabel utama merangkum satu transaksi pasien. Tombol Detail membuka modal yang memuat seluruh treatment dalam transaksi tersebut. Treatment tanpa konfigurasi BMHP ditandai "Belum ada BMHP", sedangkan penandaan disiapkan hanya tersedia per treatment yang memiliki BMHP.

## Keputusan tampilan

Form filter ditempatkan langsung sebelum tabel agar pencarian menjadi tindakan utama. Tabel utama diringkas agar apoteker memilih transaksi terlebih dahulu, sedangkan tindakan individual tetap berada di baris treatment dalam modal. Kontrol menggunakan komponen form dan tombol Bootstrap yang sudah dipakai aplikasi, sehingga konsisten dengan halaman operasional lainnya.
