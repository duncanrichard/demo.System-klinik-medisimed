/*
  Seeder stok Farmasi

  Menyetel stok tersedia setiap BARANG aktif menjadi 500 pada Gudang Semarang.
  Gudang dicari berdasarkan nama, sehingga kode gudang pada database tidak
  perlu diasumsikan G0001.

  Jalankan menggunakan login SQL Server yang memiliki hak INSERT dan UPDATE,
  misalnya sa. Skrip ini sengaja tidak dijalankan oleh aplikasi.
*/
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @WarehouseName nvarchar(100) = N'GUDANG SEMARANG';
DECLARE @WarehouseId varchar(50);
DECLARE @SeedQuantity decimal(18, 2) = 500;

IF OBJECT_ID(N'dbo.SALDOBARANG', N'U') IS NULL
BEGIN
    RAISERROR(N'Tabel dbo.SALDOBARANG tidak ditemukan.', 16, 1);
    RETURN;
END;

SELECT TOP (1) @WarehouseId = WH_ID
FROM dbo.WAREHOUSE
WHERE UPPER(LTRIM(RTRIM(NAME_WH))) = UPPER(LTRIM(RTRIM(@WarehouseName)))
ORDER BY WH_ID;

IF @WarehouseId IS NULL
BEGIN
    RAISERROR(N'Gudang dengan nama GUDANG SEMARANG tidak ditemukan.', 16, 1);
    RETURN;
END;

/*
  Baris SALDOBARANG baru membutuhkan tiga kolom utama di bawah. Hentikan
  proses lebih awal jika database ini memiliki kolom wajib lain tanpa nilai
  default, supaya tidak terjadi perubahan stok sebagian.
*/
IF EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID(N'dbo.SALDOBARANG')
      AND is_nullable = 0
      AND is_identity = 0
      AND is_computed = 0
      AND default_object_id = 0
      AND name NOT IN (N'FSBWH_ID', N'FSBBRG_ID', N'FSBSALDO_AWAL')
)
BEGIN
    RAISERROR(N'Skema SALDOBARANG memiliki kolom wajib tambahan. Periksa skema sebelum menjalankan seeder.', 16, 1);
    RETURN;
END;

BEGIN TRANSACTION;

/*
  Sesuaikan saldo awal dengan seluruh mutasi yang sudah terjadi supaya
  rumus stok tersedia aplikasi berakhir tepat di angka @SeedQuantity.
*/
UPDATE saldo
SET FSBSALDO_AWAL = @SeedQuantity
    - ISNULL(saldo.FSBPEMBELIAN, 0)
    - ISNULL(saldo.FSBRPENJUALAN, 0)
    - ISNULL(saldo.FSBLAIN_MASUK, 0)
    - ISNULL(saldo.FSBRKANVAS, 0)
    + ISNULL(saldo.FSBPENJUALAN, 0)
    + ISNULL(saldo.FSBRPEMBELIAN, 0)
    + ISNULL(saldo.FSBLAIN_KELUAR, 0)
    + ISNULL(saldo.FSBKANVAS, 0)
FROM dbo.SALDOBARANG AS saldo
INNER JOIN dbo.BARANG AS barang ON barang.BARANGC = saldo.FSBBRG_ID
WHERE saldo.FSBWH_ID = @WarehouseId
  AND ISNULL(barang.AKTIF, 0) <> 1;

INSERT INTO dbo.SALDOBARANG (FSBWH_ID, FSBBRG_ID, FSBSALDO_AWAL)
SELECT @WarehouseId, barang.BARANGC, @SeedQuantity
FROM dbo.BARANG AS barang
WHERE ISNULL(barang.AKTIF, 0) <> 1
  AND NOT EXISTS (
      SELECT 1
      FROM dbo.SALDOBARANG AS saldo
      WHERE saldo.FSBWH_ID = @WarehouseId
        AND saldo.FSBBRG_ID = barang.BARANGC
  );

COMMIT TRANSACTION;

SELECT
    @WarehouseId AS gudang,
    COUNT(*) AS jumlah_barang,
    MIN(
        ISNULL(saldo.FSBSALDO_AWAL, 0)
        + ISNULL(saldo.FSBPEMBELIAN, 0)
        + ISNULL(saldo.FSBRPENJUALAN, 0)
        + ISNULL(saldo.FSBLAIN_MASUK, 0)
        + ISNULL(saldo.FSBRKANVAS, 0)
        - ISNULL(saldo.FSBPENJUALAN, 0)
        - ISNULL(saldo.FSBRPEMBELIAN, 0)
        - ISNULL(saldo.FSBLAIN_KELUAR, 0)
        - ISNULL(saldo.FSBKANVAS, 0)
    ) AS stok_terendah,
    MAX(
        ISNULL(saldo.FSBSALDO_AWAL, 0)
        + ISNULL(saldo.FSBPEMBELIAN, 0)
        + ISNULL(saldo.FSBRPENJUALAN, 0)
        + ISNULL(saldo.FSBLAIN_MASUK, 0)
        + ISNULL(saldo.FSBRKANVAS, 0)
        - ISNULL(saldo.FSBPENJUALAN, 0)
        - ISNULL(saldo.FSBRPEMBELIAN, 0)
        - ISNULL(saldo.FSBLAIN_KELUAR, 0)
        - ISNULL(saldo.FSBKANVAS, 0)
    ) AS stok_tertinggi
FROM dbo.SALDOBARANG AS saldo
INNER JOIN dbo.BARANG AS barang ON barang.BARANGC = saldo.FSBBRG_ID
WHERE saldo.FSBWH_ID = @WarehouseId
  AND ISNULL(barang.AKTIF, 0) <> 1;
