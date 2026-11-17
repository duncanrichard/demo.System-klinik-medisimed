from django.db import migrations, models


MENU_NAME = "Apoteker"
MENU_ID_PREFIX = "APTK"


def _columns(cursor):
    return [column[0] for column in cursor.description]


def _next_menu_id(cursor):
    index = 1
    while True:
        menu_id = f"{MENU_ID_PREFIX}{index:03d}"
        cursor.execute("SELECT 1 FROM PROPERTIES_MENUBAR WHERE id = %s", [menu_id])
        if cursor.fetchone() is None:
            return menu_id
        index += 1


def _insert(cursor, table, values):
    fields = list(values)
    cursor.execute(
        f"INSERT INTO {table} ({', '.join(f'[{field}]' for field in fields)}) "
        f"VALUES ({', '.join(['%s'] * len(fields))})",
        [values[field] for field in fields],
    )


def add_apoteker_menu(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM PROPERTIES_MENUBAR WHERE modul = %s AND submodul IS NULL AND name = %s",
            ["IMMODERMA", MENU_NAME],
        )
        if cursor.fetchone() is not None:
            return

        cursor.execute(
            "SELECT TOP 1 * FROM PROPERTIES_MENUBAR "
            "WHERE modul = %s AND submodul IS NULL AND name = %s ORDER BY menu_order, id",
            ["IMMODERMA", "Farmasi"],
        )
        source = cursor.fetchone()
        source_columns = _columns(cursor)
        if source is None:
            raise RuntimeError("Menu Farmasi tidak ditemukan.")

        source_menu = dict(zip(source_columns, source))
        cursor.execute(
            "SELECT ISNULL(MAX(menu_order), 0) + 1 FROM PROPERTIES_MENUBAR "
            "WHERE modul = %s AND submodul IS NULL",
            ["IMMODERMA"],
        )
        menu_order = cursor.fetchone()[0]
        menu_id = _next_menu_id(cursor)
        menu_values = source_menu.copy()
        menu_values.update(
            {
                "id": menu_id,
                "name": MENU_NAME,
                "parent": None,
                "link": "apoteker/",
                "onclick": "##",
                "menu_order": menu_order,
            }
        )
        _insert(cursor, "PROPERTIES_MENUBAR", menu_values)

        cursor.execute(
            "SELECT DISTINCT USER_PRIV, modul, submodul FROM PRIVILEGE_MENUBAR WHERE MENUBAR_PRIV = %s",
            [source_menu["id"]],
        )
        for user_priv, modul, submodul in cursor.fetchall():
            cursor.execute(
                "INSERT INTO PRIVILEGE_MENUBAR (USER_PRIV, MENUBAR_PRIV, modul, submodul) "
                "VALUES (%s, %s, %s, %s)",
                [user_priv, menu_id, modul, submodul],
            )


def remove_apoteker_menu(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM PROPERTIES_MENUBAR WHERE modul = %s AND submodul IS NULL AND name = %s",
            ["IMMODERMA", MENU_NAME],
        )
        menu_ids = [row[0] for row in cursor.fetchall()]
        for menu_id in menu_ids:
            cursor.execute("DELETE FROM PRIVILEGE_MENUBAR WHERE MENUBAR_PRIV = %s", [menu_id])
        cursor.execute(
            "DELETE FROM PROPERTIES_MENUBAR WHERE modul = %s AND submodul IS NULL AND name = %s",
            ["IMMODERMA", MENU_NAME],
        )


class Migration(migrations.Migration):
    dependencies = [("dashboard", "0003_treatment_bmhp")]

    operations = [
        migrations.CreateModel(
            name="ApotekerPreparation",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("transaction_id", models.CharField(max_length=50, verbose_name="Nomor Transaksi")),
                ("transaction_detail_number", models.IntegerField(verbose_name="Nomor Detail Transaksi")),
                ("prepared_at", models.DateTimeField(auto_now_add=True, verbose_name="Waktu Disiapkan")),
                ("prepared_by", models.CharField(blank=True, max_length=100, verbose_name="Disiapkan Oleh")),
            ],
            options={"db_table": "APOTEKER_PERSIAPAN_BMHP"},
        ),
        migrations.AddConstraint(
            model_name="apotekerpreparation",
            constraint=models.UniqueConstraint(
                fields=("transaction_id", "transaction_detail_number"),
                name="unique_apoteker_preparation_detail",
            ),
        ),
        migrations.RunPython(add_apoteker_menu, remove_apoteker_menu),
    ]
