from decimal import Decimal, ROUND_FLOOR

from django.db import migrations, models


CREDITOS_FACTOR = Decimal("0.0625")


def recalculate_creditos(apps, schema_editor):
    Materia = apps.get_model("catalogos", "Materia")

    for materia in Materia.objects.all().iterator():
        horas_totales = materia.horas_totales or 0
        materia.creditos = round(Decimal(horas_totales) * CREDITOS_FACTOR, 2)
        materia.save(update_fields=["creditos"])


def reverse_recalculate_creditos(apps, schema_editor):
    Materia = apps.get_model("catalogos", "Materia")

    for materia in Materia.objects.all().iterator():
        horas_totales = materia.horas_totales or 0
        valor = round(Decimal(horas_totales) * CREDITOS_FACTOR, 2)
        materia.creditos = int((valor + Decimal("0.5")).to_integral_value(rounding=ROUND_FLOOR))
        materia.save(update_fields=["creditos"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalogos", "0015_internal_backend_terminology"),
    ]

    operations = [
        migrations.AlterField(
            model_name="materia",
            name="creditos",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                editable=False,
                max_digits=5,
            ),
        ),
        migrations.RunPython(recalculate_creditos, reverse_recalculate_creditos),
    ]
