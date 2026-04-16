from django.db import migrations


def crear_rol_discente(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    db_alias = schema_editor.connection.alias
    Group.objects.using(db_alias).get_or_create(name="DISCENTE")


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("usuarios", "0002_usuario_correo_asignacioncargo"),
    ]

    operations = [
        migrations.RunPython(crear_rol_discente, migrations.RunPython.noop),
    ]
