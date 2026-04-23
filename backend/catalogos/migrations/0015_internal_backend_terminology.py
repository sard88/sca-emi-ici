import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogos", "0014_alter_materiaplan_options_and_more"),
        ("evaluacion", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RenameModel(
                    old_name="Generacion",
                    new_name="Antiguedad",
                ),
                migrations.AlterModelTable(
                    name="antiguedad",
                    table="catalogos_generacion",
                ),
                migrations.AlterField(
                    model_name="antiguedad",
                    name="plan_estudios",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="antiguedades",
                        to="catalogos.planestudios",
                    ),
                ),
                migrations.RenameField(
                    model_name="periodoescolar",
                    old_name="semestre_operativo",
                    new_name="periodo_academico",
                ),
                migrations.AlterModelOptions(
                    name="periodoescolar",
                    options={
                        "ordering": ["-anio_escolar", "-periodo_academico", "clave"],
                        "verbose_name": "Periodo escolar",
                        "verbose_name_plural": "Periodo escolar",
                    },
                ),
                migrations.AlterField(
                    model_name="periodoescolar",
                    name="periodo_academico",
                    field=models.PositiveSmallIntegerField(
                        choices=[(1, "Primer semestre"), (2, "Segundo semestre")],
                        db_column="semestre_operativo",
                        null=True,
                        verbose_name="Periodo académico",
                    ),
                ),
                migrations.RenameField(
                    model_name="grupoacademico",
                    old_name="generacion",
                    new_name="antiguedad",
                ),
                migrations.AlterModelOptions(
                    name="grupoacademico",
                    options={
                        "ordering": [
                            "periodo__anio_escolar",
                            "periodo__periodo_academico",
                            "clave_grupo",
                        ],
                        "verbose_name": "Grupo académico",
                        "verbose_name_plural": "Grupos académicos",
                    },
                ),
                migrations.AlterField(
                    model_name="grupoacademico",
                    name="antiguedad",
                    field=models.ForeignKey(
                        db_column="generacion_id",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="grupos_academicos",
                        to="catalogos.antiguedad",
                        verbose_name="Antigüedad",
                    ),
                ),
                migrations.RemoveConstraint(
                    model_name="grupoacademico",
                    name="uq_grupo_generacion_periodo_clave",
                ),
                migrations.AddConstraint(
                    model_name="grupoacademico",
                    constraint=models.UniqueConstraint(
                        fields=("antiguedad", "periodo", "clave_grupo"),
                        name="uq_grupo_generacion_periodo_clave",
                    ),
                ),
                migrations.RenameModel(
                    old_name="MateriaPlan",
                    new_name="ProgramaAsignatura",
                ),
                migrations.AlterModelTable(
                    name="programaasignatura",
                    table="catalogos_materiaplan",
                ),
                migrations.AlterField(
                    model_name="programaasignatura",
                    name="plan_estudios",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="programas_asignatura",
                        to="catalogos.planestudios",
                        verbose_name="Plan de estudio",
                    ),
                ),
                migrations.AlterField(
                    model_name="programaasignatura",
                    name="materia",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="programas_asignatura",
                        to="catalogos.materia",
                        verbose_name="Materia",
                    ),
                ),
                migrations.RenameField(
                    model_name="programaasignatura",
                    old_name="anio_escolar_numero",
                    new_name="anio_formacion",
                ),
                migrations.AlterModelOptions(
                    name="programaasignatura",
                    options={
                        "ordering": [
                            "plan_estudios__clave",
                            "anio_formacion",
                            "semestre_numero",
                            "materia__clave",
                        ],
                        "verbose_name": "Programa de asignatura",
                        "verbose_name_plural": "Programas de asignatura",
                    },
                ),
                migrations.AlterField(
                    model_name="programaasignatura",
                    name="anio_formacion",
                    field=models.PositiveSmallIntegerField(
                        db_column="anio_escolar_numero",
                        default=1,
                        verbose_name="Año de formación",
                    ),
                ),
            ],
        ),
    ]
