import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogos", "0015_internal_backend_terminology"),
        ("evaluacion", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RenameField(
                    model_name="esquemaevaluacion",
                    old_name="materia_plan",
                    new_name="programa_asignatura",
                ),
                migrations.AlterModelOptions(
                    name="esquemaevaluacion",
                    options={
                        "ordering": [
                            "-activo",
                            "programa_asignatura__plan_estudios__clave",
                            "programa_asignatura__materia__clave",
                        ],
                        "verbose_name": "Esquema de evaluación",
                        "verbose_name_plural": "Esquemas de evaluación",
                    },
                ),
                migrations.AlterField(
                    model_name="esquemaevaluacion",
                    name="programa_asignatura",
                    field=models.ForeignKey(
                        db_column="materia_plan_id",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="esquemas_evaluacion",
                        to="catalogos.programaasignatura",
                        verbose_name="Programa de asignatura",
                    ),
                ),
                migrations.RemoveConstraint(
                    model_name="esquemaevaluacion",
                    name="uq_esquemaevaluacion_materiaplan_version",
                ),
                migrations.AddConstraint(
                    model_name="esquemaevaluacion",
                    constraint=models.UniqueConstraint(
                        fields=("programa_asignatura", "version"),
                        name="uq_esquemaevaluacion_materiaplan_version",
                    ),
                ),
            ],
        ),
    ]
