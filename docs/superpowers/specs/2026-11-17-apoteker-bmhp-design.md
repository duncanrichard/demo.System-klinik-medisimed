# Antrean Apoteker BMHP

## Intent

Berikan Apoteker antrean treatment yang membutuhkan BMHP segera setelah transaksi dibuat, tanpa menunggu pembayaran lunas.

## Goals

- Tambahkan menu bar **Apoteker** dengan hak akses yang menyalin menu Farmasi.
- Tampilkan pasien, transaksi, treatment, jumlah treatment, dan daftar BMHP yang harus disiapkan.
- Hitung kebutuhan BMHP sebagai jumlah treatment dikalikan jumlah BMHP pada master treatment.
- Sediakan aksi **Sudah disiapkan** per detail treatment.

## Non-goals

- Tidak mengubah data pembayaran, stok, atau transaksi klinis.
- Tidak mengurangi stok BMHP secara otomatis.

## Approach

1. **Antrean berstatus persiapan (dipilih):** simpan status berdasarkan nomor transaksi dan nomor detail treatment. Status membuat treatment hilang dari antrean aktif setelah Apoteker menandainya selesai.
2. **Daftar tanpa status:** ditolak karena transaksi lama akan tetap muncul dan dapat disiapkan berulang kali.

## Design

- Gunakan detail transaksi `TRANSAKSIPASIEND` sebagai sumber treatment, dengan pasien melalui `TRANSAKSIPASIEN`, `KUNJUNGANPASIEN`, dan `PASIEN`.
- Tambahkan tabel aplikasi untuk mencatat waktu serta pengguna yang menandai detail treatment selesai disiapkan.
- Halaman hanya mengambil treatment yang memiliki pemetaan pada `TREATMENT_BMHP` dan belum memiliki status persiapan.
- Aksi menggunakan POST dan menyimpan status tanpa menunggu pembayaran lunas.
- Dials: ENERGY 1 / RHYTHM 1 / MOTION 1. Alasannya: ini adalah antrean operasional klinik yang harus mudah dipindai dan tanpa gerakan dekoratif.

## Major UI decisions

- Tabel adalah fokus utama karena Apoteker perlu memindai antrean dan kebutuhan BMHP cepat.
- Daftar BMHP ditampilkan pada baris treatment agar pasien, treatment, dan kebutuhan tidak terpisah ke layar lain.
- Aksi hijau dipakai khusus untuk status selesai karena menandai perubahan operasional yang nyata.
