from django.db import migrations


SITUACIONES = {
    "ACTIVO": "Activo",
    "BAJA_TEMPORAL": "Baja temporal",
    "REINGRESO": "Reingreso",
    "EGRESADO": "Egresado",
}

RESULTADOS = {
    "APROBADO": "Aprobado",
    "REPROBADO": "Reprobado",
    "APROBADO_EXTRAORDINARIO": "Aprobado por extraordinario",
    "EE": "Marca EE",
    "ACREDITADA": "Acreditada",
    "APROBADO_NO_NUMERICO": "Aprobado no numérico",
    "EXCEPTUADO": "Exceptuado",
}


def seed_catalogos(apps, schema_editor):
    CatalogoSituacionAcademica = apps.get_model("trayectoria", "CatalogoSituacionAcademica")
    CatalogoResultadoAcademico = apps.get_model("trayectoria", "CatalogoResultadoAcademico")

    for clave, nombre in SITUACIONES.items():
        CatalogoSituacionAcademica.objects.update_or_create(
            clave=clave,
            defaults={"nombre": nombre, "activo": True},
        )

    for clave, nombre in RESULTADOS.items():
        CatalogoResultadoAcademico.objects.update_or_create(
            clave=clave,
            defaults={"nombre": nombre, "activo": True},
        )


def noop_reverse(apps, schema_editor):
    # No se eliminan catálogos para evitar pérdida de referencias históricas.
    return None


class Migration(migrations.Migration):
    dependencies = [
        ("trayectoria", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_catalogos, noop_reverse),
    ]
