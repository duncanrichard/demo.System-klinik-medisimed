from django.db import migrations


MENU_NAME = "Master BMHP"
MENU_LINK = "/master_bmhp/"
MODULE = "IMMODERMA"


def _column_names(cursor):
    return [column[0] for column in cursor.description]


def _next_menu_id(cursor):
    index = 1
    while True:
        menu_id = f"BMHP{index:03d}"
        cursor.execute("SELECT 1 FROM PROPERTIES_NAVBAR WHERE id = %s", [menu_id])
        if cursor.fetchone() is None:
            return menu_id
        index += 1


def _insert_row(cursor, table, values):
    columns = list(values)
    quoted_columns = ", ".join(f"[{column}]" for column in columns)
    placeholders = ", ".join(["%s"] * len(columns))
    cursor.execute(
        f"INSERT INTO {table} ({quoted_columns}) VALUES ({placeholders})",
        [values[column] for column in columns],
    )


def add_bmhp_navigation(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM PROPERTIES_NAVBAR WHERE modul = %s AND submodul IS NULL AND name = %s",
            [MODULE, MENU_NAME],
        )
        if cursor.fetchone() is not None:
            return

        cursor.execute(
            "SELECT TOP 1 id FROM PROPERTIES_NAVBAR "
            "WHERE modul = %s AND submodul IS NULL AND name = %s ORDER BY nav_order, id",
            [MODULE, "Master Treatment"],
        )
        parent = cursor.fetchone()
        cursor.execute(
            "SELECT TOP 1 * FROM PROPERTIES_NAVBAR "
            "WHERE modul = %s AND submodul IS NULL AND name = %s ORDER BY nav_order, id",
            [MODULE, "Data Treatment"],
        )
        source = cursor.fetchone()
        source_columns = _column_names(cursor)

        if parent is None or source is None:
            raise RuntimeError("Parent Master Treatment atau menu Data Treatment tidak ditemukan.")

        parent_id = parent[0]
        source_menu = dict(zip(source_columns, source))
        menu_id = _next_menu_id(cursor)
        cursor.execute(
            "SELECT ISNULL(MAX(nav_order), 0) + 1 FROM PROPERTIES_NAVBAR WHERE parent = %s",
            [parent_id],
        )

        menu_values = source_menu.copy()
        menu_values.update(
            {
                "id": menu_id,
                "name": MENU_NAME,
                "parent": parent_id,
                "has_sub": 0,
                "link": MENU_LINK,
                "nav_order": cursor.fetchone()[0],
            }
        )
        _insert_row(cursor, "PROPERTIES_NAVBAR", menu_values)

        cursor.execute(
            "SELECT DISTINCT USER_PRIV, modul, submodul FROM PRIVILEGE_NAVBAR WHERE NAVBAR_PRIV = %s",
            [source_menu["id"]],
        )
        privilege_rows = cursor.fetchall()
        for privilege_row in privilege_rows:
            cursor.execute(
                "INSERT INTO PRIVILEGE_NAVBAR (USER_PRIV, NAVBAR_PRIV, modul, submodul) VALUES (%s, %s, %s, %s)",
                [privilege_row[0], menu_id, privilege_row[1], privilege_row[2]],
            )


def remove_bmhp_navigation(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM PROPERTIES_NAVBAR WHERE modul = %s AND submodul IS NULL AND name = %s",
            [MODULE, MENU_NAME],
        )
        menu_ids = [row[0] for row in cursor.fetchall()]
        for menu_id in menu_ids:
            cursor.execute("DELETE FROM PRIVILEGE_NAVBAR WHERE NAVBAR_PRIV = %s", [menu_id])
        cursor.execute(
            "DELETE FROM PROPERTIES_NAVBAR WHERE modul = %s AND submodul IS NULL AND name = %s",
            [MODULE, MENU_NAME],
        )


class Migration(migrations.Migration):
    dependencies = [("dashboard", "0001_initial")]

    operations = [migrations.RunPython(add_bmhp_navigation, remove_bmhp_navigation)]
