# Receipt Apoteker

## Intent

Memberikan dokumen serah terima BMHP per transaksi yang dapat dicetak oleh Apoteker dan ditandatangani oleh pihak yang mengambil serta menyerahkan.

## Goals

- Tambahkan aksi `Receipt` pada setiap transaksi di antrean Apoteker.
- Cetak seluruh treatment dalam transaksi beserta jumlah treatment dan kebutuhan BMHP.
- Tampilkan identitas pasien, dokter, BC, dan perawat dari data transaksi.
- Sediakan area tanda tangan `Yang Mengambil` dan `Yang Menyerahkan`.
- Batasi akses receipt berdasarkan sesi login dan cabang pengguna.

## Non-goals

- Tidak mengubah status persiapan BMHP, transaksi, pembayaran, atau stok.
- Tidak menyimpan tanda tangan atau nama pihak yang menandatangani.
- Tidak membuat file PDF di server.

## Approaches

1. Halaman cetak khusus per transaksi (dipilih). Data diambil ulang dari server agar lengkap, konsisten, dan tervalidasi terhadap cabang pengguna.
2. Mencetak isi modal Detail dengan JavaScript. Ditolak karena data petugas belum tersedia pada modal dan format cetak lebih rapuh.

## Design

- Tombol `Receipt` ditempatkan di kolom Aksi, di samping tombol `Detail`.
- Endpoint receipt menerima nomor transaksi pada path, mewajibkan login, dan hanya mengambil transaksi dari cabang pada sesi pengguna.
- Header receipt menampilkan identitas cabang, nomor dan tanggal transaksi, kode dan nama pasien, dokter, BC, serta perawat.
- Tabel mencetak semua treatment dengan kolom `Jumlah Treatment`, `BMHP`, dan `Jumlah BMHP` yang terpisah. Jumlah BMHP dihitung dari jumlah treatment dikalikan jumlah pada master pemetaan. Treatment tanpa pemetaan tetap muncul dengan keterangan `Belum ada BMHP`.
- Bagian akhir berisi dua area tanda tangan kosong dengan label `Yang Mengambil` dan `Yang Menyerahkan`, termasuk garis untuk nama jelas.
- Halaman menyediakan tombol `Cetak` yang memanggil dialog cetak browser dan tombol `Kembali` ke antrean. Kedua kontrol disembunyikan saat dicetak.
- Design Read: dokumen operasional klinik untuk Apoteker, menggunakan bahasa visual aplikasi yang sudah ada, dial ENERGY 1 / RHYTHM 1 / MOTION 1.
- Warna netral, tabel berbingkai, dan jarak yang rapat dipilih agar hasil cetak hemat ruang serta mudah diperiksa.
- Tipografi sistem dipertahankan agar konsisten dengan aplikasi dan stabil pada printer tanpa bergantung pada font eksternal.
