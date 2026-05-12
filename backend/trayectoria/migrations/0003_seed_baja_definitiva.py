from django.db import migrations


def seed_baja_definitiva(apps, schema_editor):
    CatalogoSituacionAcademica = apps.get_model("trayectoria", "CatalogoSituacionAcademica")
    CatalogoSituacionAcademica.objects.update_or_create(
        clave="BAJA_DEFINITIVA",
        defaults={"nombre": "Baja definitiva", "activo": True},
    )


def noop_reverse(apps, schema_editor):
    # No se elimina el catálogo para conservar referencias históricas.
    return None


class Migration(migrations.Migration):
    dependencies = [
        ("trayectoria", "0002_seed_catalogos_base"),
    ]

    operations = [
        migrations.RunPython(seed_baja_definitiva, noop_reverse),
    ]
