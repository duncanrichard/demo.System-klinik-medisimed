from django.db import migrations, models
import django.db.models.deletion


MENU_NAME = "Treatment BMHP"
MENU_LINK = "/treatment_bmhp/"
MENU_ID_PREFIX = "TBMHP"


def _columns(cursor):
    return [column[0] for column in cursor.description]


def _next_menu_id(cursor):
    index = 1
    while True:
        menu_id = f"{MENU_ID_PREFIX}{index:03d}"
        cursor.execute("SELECT 1 FROM PROPERTIES_NAVBAR WHERE id = %s", [menu_id])
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


def add_treatment_bmhp_navigation(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM PROPERTIES_NAVBAR WHERE modul = %s AND submodul IS NULL AND name = %s",
            ["IMMODERMA", MENU_NAME],
        )
        if cursor.fetchone() is not None:
            return

        cursor.execute(
            "SELECT TOP 1 * FROM PROPERTIES_NAVBAR "
            "WHERE modul = %s AND submodul IS NULL AND name = %s ORDER BY nav_order, id",
            ["IMMODERMA", "Master BMHP"],
        )
        source = cursor.fetchone()
        source_columns = _columns(cursor)
        if source is None:
            raise RuntimeError("Menu Master BMHP tidak ditemukan.")

        source_menu = dict(zip(source_columns, source))
        cursor.execute(
            "SELECT ISNULL(MAX(nav_order), 0) + 1 FROM PROPERTIES_NAVBAR WHERE parent = %s",
            [source_menu["parent"]],
        )
        menu_order = cursor.fetchone()[0]
        menu_values = source_menu.copy()
        menu_values.update(
            {
                "id": _next_menu_id(cursor),
                "name": MENU_NAME,
                "has_sub": 0,
                "link": MENU_LINK,
                "nav_order": menu_order,
            }
        )
        _insert(cursor, "PROPERTIES_NAVBAR", menu_values)

        cursor.execute(
            "SELECT DISTINCT USER_PRIV, modul, submodul FROM PRIVILEGE_NAVBAR WHERE NAVBAR_PRIV = %s",
            [source_menu["id"]],
        )
        for user_priv, modul, submodul in cursor.fetchall():
            cursor.execute(
                "INSERT INTO PRIVILEGE_NAVBAR (USER_PRIV, NAVBAR_PRIV, modul, submodul) VALUES (%s, %s, %s, %s)",
                [user_priv, menu_values["id"], modul, submodul],
            )


def remove_treatment_bmhp_navigation(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM PROPERTIES_NAVBAR WHERE modul = %s AND submodul IS NULL AND name = %s",
            ["IMMODERMA", MENU_NAME],
        )
        menu_ids = [row[0] for row in cursor.fetchall()]
        for menu_id in menu_ids:
            cursor.execute("DELETE FROM PRIVILEGE_NAVBAR WHERE NAVBAR_PRIV = %s", [menu_id])
        cursor.execute(
            "DELETE FROM PROPERTIES_NAVBAR WHERE modul = %s AND submodul IS NULL AND name = %s",
            ["IMMODERMA", MENU_NAME],
        )


class Migration(migrations.Migration):
    dependencies = [("dashboard", "0002_add_bmhp_navigation")]

    operations = [
        migrations.CreateModel(
            name="TreatmentBMHP",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("treatment_id", models.CharField(max_length=50, verbose_name="ID Treatment")),
                ("jumlah", models.DecimalField(decimal_places=3, max_digits=12, verbose_name="Jumlah")),
                ("satuan", models.CharField(max_length=30, verbose_name="Satuan")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("bmhp", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="treatment_usages", to="dashboard.bmhp")),
            ],
            options={"db_table": "TREATMENT_BMHP", "ordering": ["treatment_id", "bmhp__nama_bmhp"]},
        ),
        migrations.AddConstraint(
            model_name="treatmentbmhp",
            constraint=models.UniqueConstraint(fields=("treatment_id", "bmhp", "satuan"), name="unique_treatment_bmhp_unit"),
        ),
        migrations.RunPython(add_treatment_bmhp_navigation, remove_treatment_bmhp_navigation),
    ]
