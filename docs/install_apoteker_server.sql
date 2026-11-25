/*
  Jalankan sebagai SQL Server administrator pada IMMO_Medisimed.
  Aman dijalankan ulang. Tidak mengubah BMHP, TREATMENT_BMHP, atau transaksi.
*/
SET XACT_ABORT ON;
BEGIN TRANSACTION;

IF OBJECT_ID(N'dbo.APOTEKER_PERSIAPAN_BMHP', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.APOTEKER_PERSIAPAN_BMHP (
        id INT IDENTITY(1, 1) NOT NULL,
        transaction_id NVARCHAR(50) NOT NULL,
        transaction_detail_number INT NOT NULL,
        prepared_at DATETIME2 NOT NULL CONSTRAINT DF_APOTEKER_PERSIAPAN_BMHP_PREPARED_AT DEFAULT SYSUTCDATETIME(),
        prepared_by NVARCHAR(100) NOT NULL CONSTRAINT DF_APOTEKER_PERSIAPAN_BMHP_PREPARED_BY DEFAULT N'',
        CONSTRAINT PK_APOTEKER_PERSIAPAN_BMHP PRIMARY KEY CLUSTERED (id),
        CONSTRAINT UQ_APOTEKER_PERSIAPAN_BMHP_TRANSACTION_DETAIL UNIQUE (transaction_id, transaction_detail_number)
    );
END;

DECLARE @farmasi_id NVARCHAR(50);
DECLARE @apoteker_id NVARCHAR(50);
DECLARE @next_order INT;
DECLARE @columns NVARCHAR(MAX);
DECLARE @select_columns NVARCHAR(MAX);
DECLARE @sql NVARCHAR(MAX);

SELECT TOP (1) @farmasi_id = id
FROM dbo.PROPERTIES_MENUBAR
WHERE modul = N'IMMODERMA' AND submodul IS NULL AND name = N'Farmasi'
ORDER BY menu_order, id;

IF @farmasi_id IS NULL
    THROW 50001, 'Menu Farmasi tidak ditemukan. Menu Apoteker tidak dapat dibuat.', 1;

SELECT TOP (1) @apoteker_id = id
FROM dbo.PROPERTIES_MENUBAR
WHERE modul = N'IMMODERMA' AND submodul IS NULL AND name = N'Apoteker';

IF @apoteker_id IS NULL
BEGIN
    DECLARE @counter INT = 1;
    SET @apoteker_id = N'APTK001';
    WHILE EXISTS (SELECT 1 FROM dbo.PROPERTIES_MENUBAR WHERE id = @apoteker_id)
    BEGIN
        SET @counter += 1;
        SET @apoteker_id = N'APTK' + RIGHT(N'000' + CONVERT(NVARCHAR(10), @counter), 3);
    END;

    SELECT @next_order = ISNULL(MAX(menu_order), 0) + 1
    FROM dbo.PROPERTIES_MENUBAR
    WHERE modul = N'IMMODERMA' AND submodul IS NULL;

    SELECT @columns = STRING_AGG(QUOTENAME(name), N', '),
           @select_columns = STRING_AGG(
               CASE name
                   WHEN N'id' THEN N'@menu_id'
                   WHEN N'name' THEN N'N''Apoteker'''
                   WHEN N'parent' THEN N'NULL'
                   WHEN N'link' THEN N'N''apoteker/'''
                   WHEN N'onclick' THEN N'N''##'''
                   WHEN N'menu_order' THEN N'@menu_order'
                   ELSE QUOTENAME(name)
               END,
               N', '
           )
    FROM sys.columns
    WHERE object_id = OBJECT_ID(N'dbo.PROPERTIES_MENUBAR')
      AND is_identity = 0
      AND is_computed = 0;

    SET @sql = N'INSERT INTO dbo.PROPERTIES_MENUBAR (' + @columns + N') '
             + N'SELECT ' + @select_columns + N' '
             + N'FROM dbo.PROPERTIES_MENUBAR WHERE id = @source_menu_id;';

    EXEC sys.sp_executesql
        @sql,
        N'@menu_id NVARCHAR(50), @menu_order INT, @source_menu_id NVARCHAR(50)',
        @menu_id = @apoteker_id,
        @menu_order = @next_order,
        @source_menu_id = @farmasi_id;
END;

INSERT INTO dbo.PRIVILEGE_MENUBAR (USER_PRIV, MENUBAR_PRIV, modul, submodul)
SELECT DISTINCT source_privilege.USER_PRIV, @apoteker_id, source_privilege.modul, source_privilege.submodul
FROM dbo.PRIVILEGE_MENUBAR AS source_privilege
WHERE source_privilege.MENUBAR_PRIV = @farmasi_id
  AND NOT EXISTS (
      SELECT 1
      FROM dbo.PRIVILEGE_MENUBAR AS target_privilege
      WHERE target_privilege.USER_PRIV = source_privilege.USER_PRIV
        AND target_privilege.MENUBAR_PRIV = @apoteker_id
        AND target_privilege.modul = source_privilege.modul
        AND (target_privilege.submodul = source_privilege.submodul
             OR (target_privilege.submodul IS NULL AND source_privilege.submodul IS NULL))
  );

COMMIT TRANSACTION;

SELECT menu.id, menu.name, menu.link, menu.menu_order, COUNT(privilege_menu.MENUBAR_PRIV) AS jumlah_hak_akses
FROM dbo.PROPERTIES_MENUBAR AS menu
LEFT JOIN dbo.PRIVILEGE_MENUBAR AS privilege_menu ON privilege_menu.MENUBAR_PRIV = menu.id
WHERE menu.modul = N'IMMODERMA' AND menu.submodul IS NULL AND menu.name = N'Apoteker'
GROUP BY menu.id, menu.name, menu.link, menu.menu_order;
