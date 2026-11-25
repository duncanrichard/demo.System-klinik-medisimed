/*
 Jalankan di SSMS. Skrip ini menyalin stored procedure penyimpanan E-Resep
 dari database lama IMMO ke database lokal aplikasi.
 Jika target berbeda, ganti baris USE di bawah.
*/
USE [IMMO_IMPORT_20261125];
GO

IF NOT EXISTS (
    SELECT 1
    FROM IMMO.sys.procedures AS procedure_source
    INNER JOIN IMMO.sys.schemas AS schema_source
        ON schema_source.schema_id = procedure_source.schema_id
    WHERE schema_source.name = N'dbo'
      AND procedure_source.name = N'add_EresepDokter'
)
BEGIN
    THROW 50001, 'Stored procedure dbo.add_EresepDokter tidak ditemukan pada database sumber IMMO.', 1;
END;
GO

DECLARE @procedure_definition NVARCHAR(MAX);

SELECT @procedure_definition = module_source.definition
FROM IMMO.sys.procedures AS procedure_source
INNER JOIN IMMO.sys.schemas AS schema_source
    ON schema_source.schema_id = procedure_source.schema_id
INNER JOIN IMMO.sys.sql_modules AS module_source
    ON module_source.object_id = procedure_source.object_id
WHERE schema_source.name = N'dbo'
  AND procedure_source.name = N'add_EresepDokter';

EXEC sys.sp_executesql @procedure_definition;
GO

IF OBJECT_ID(N'dbo.add_EresepDokter', N'P') IS NULL
    THROW 50002, 'Procedure tidak berhasil dibuat pada database tujuan.', 1;

SELECT name AS stored_procedure
FROM sys.procedures
WHERE object_id = OBJECT_ID(N'dbo.add_EresepDokter', N'P');
GO
