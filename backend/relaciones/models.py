from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from catalogos.models import (
    ESTADO_ACTIVO,
    Antiguedad,
    GrupoAcademico,
    PeriodoEscolar,
    PlanEstudios,
    ProgramaAsignatura,
)
from usuarios.models import Usuario


OBSERVACIONES_EXTEMPORANEAS_MIN_LENGTH = 10
ROL_DISCENTE = "DISCENTE"
ROL_DOCENTE = "DOCENTE"


def usuario_activo_con_rol(usuario, rol):
    return (
        usuario.is_active
        and usuario.estado_cuenta == Usuario.ESTADO_ACTIVO
        and usuario.groups.filter(name=rol).exists()
    )


class Discente(models.Model):
    SITUACION_REGULAR = "regular"
    SITUACION_BAJA_TEMPORAL = "baja_temporal"
    SITUACION_BAJA_DEFINITIVA = "baja_definitiva"
    SITUACION_EGRESADO = "egresado"

    SITUACION_CHOICES = [
        (SITUACION_REGULAR, "Regular"),
        (SITUACION_BAJA_TEMPORAL, "Baja temporal"),
        (SITUACION_BAJA_DEFINITIVA, "Baja definitiva"),
        (SITUACION_EGRESADO, "Egresado"),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="perfiles_discente",
        verbose_name="Usuario",
    )
    matricula = models.CharField(max_length=30, unique=True, verbose_name="Matrícula")
    plan_estudios = models.ForeignKey(
        PlanEstudios,
        on_delete=models.PROTECT,
        related_name="discentes",
        verbose_name="Plan de estudio",
    )
    antiguedad = models.ForeignKey(
        Antiguedad,
        on_delete=models.PROTECT,
        db_column="generacion_id",
        related_name="discentes",
        verbose_name="Antigüedad",
    )
    situacion_actual = models.CharField(
        max_length=30,
        choices=SITUACION_CHOICES,
        default=SITUACION_REGULAR,
        verbose_name="Situación actual",
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        ordering = ["matricula"]
        verbose_name = "Discente"
        verbose_name_plural = "Discentes"
        constraints = [
            models.UniqueConstraint(
                fields=["usuario"],
                condition=models.Q(activo=True),
                name="uq_discente_activo_usuario",
            ),
        ]

    def clean(self):
        errors = {}

        if self.usuario_id:
            if not usuario_activo_con_rol(self.usuario, ROL_DISCENTE):
                errors["usuario"] = "Solo se puede asignar un usuario activo con rol DISCENTE."

        if self.plan_estudios_id and self.plan_estudios.estado != ESTADO_ACTIVO:
            errors["plan_estudios"] = "Solo se puede asignar un plan de estudios activo."

        if self.antiguedad_id:
            if self.antiguedad.estado != ESTADO_ACTIVO:
                errors["antiguedad"] = "Solo se puede asignar una antigüedad activa."
            elif self.plan_estudios_id and self.antiguedad.plan_estudios_id != self.plan_estudios_id:
                errors["antiguedad"] = "La antigüedad debe pertenecer al plan de estudios seleccionado."

        if self.activo and self.usuario_id:
            duplicado = Discente.objects.filter(usuario=self.usuario, activo=True)
            if self.pk:
                duplicado = duplicado.exclude(pk=self.pk)
            if duplicado.exists():
                errors["usuario"] = "Este usuario ya tiene un perfil de discente activo."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.matricula} - {self.usuario}"


class AdscripcionGrupo(models.Model):
    discente = models.ForeignKey(
        Discente,
        on_delete=models.PROTECT,
        related_name="adscripciones_grupo",
        verbose_name="Discente",
    )
    grupo_academico = models.ForeignKey(
        GrupoAcademico,
        on_delete=models.PROTECT,
        related_name="adscripciones_discente",
        verbose_name="Grupo académico",
    )
    vigente_desde = models.DateField(
        null=True,
        blank=True,
        default=timezone.localdate,
        verbose_name="Vigente desde",
    )
    vigente_hasta = models.DateField(null=True, blank=True, verbose_name="Vigente hasta")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        ordering = [
            "-activo",
            "grupo_academico__periodo__anio_escolar",
            "grupo_academico__clave_grupo",
            "discente__matricula",
        ]
        verbose_name = "Adscripción a grupo"
        verbose_name_plural = "Adscripciones a grupo"
        constraints = [
            models.UniqueConstraint(
                fields=["discente", "grupo_academico"],
                condition=models.Q(activo=True),
                name="uq_adscripciongrupo_activa_discente_grupo",
            )
        ]

    def _ensure_vigencia_defaults(self):
        if not self.vigente_desde:
            self.vigente_desde = timezone.localdate()

    def clean(self):
        self._ensure_vigencia_defaults()
        errors = {}

        if self.discente_id and not self.discente.activo:
            errors["discente"] = "Solo se puede adscribir un discente activo."

        if self.grupo_academico_id:
            if self.grupo_academico.estado != ESTADO_ACTIVO:
                errors["grupo_academico"] = "Solo se puede asignar un grupo académico activo."
            elif self.grupo_academico.periodo.estado != ESTADO_ACTIVO:
                errors["grupo_academico"] = "El periodo del grupo debe estar activo."

        if self.discente_id and self.grupo_academico_id:
            if self.discente.antiguedad_id != self.grupo_academico.antiguedad_id:
                errors["grupo_academico"] = (
                    "El grupo académico debe corresponder a la antigüedad del discente."
                )

            if self.activo:
                misma_adscripcion = AdscripcionGrupo.objects.filter(
                    discente=self.discente,
                    grupo_academico=self.grupo_academico,
                    activo=True,
                )
                mismo_periodo = AdscripcionGrupo.objects.filter(
                    discente=self.discente,
                    grupo_academico__periodo=self.grupo_academico.periodo,
                    activo=True,
                )
                if self.pk:
                    misma_adscripcion = misma_adscripcion.exclude(pk=self.pk)
                    mismo_periodo = mismo_periodo.exclude(pk=self.pk)
                if misma_adscripcion.exists():
                    errors["grupo_academico"] = "El discente ya tiene esta adscripción activa."
                elif mismo_periodo.exists():
                    errors["grupo_academico"] = (
                        "El discente ya tiene una adscripción activa en este periodo."
                    )

        if self.vigente_hasta and self.vigente_desde and self.vigente_hasta < self.vigente_desde:
            errors["vigente_hasta"] = "No puede ser anterior a 'vigente_desde'."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.discente} - {self.grupo_academico}"


class AsignacionDocente(models.Model):
    usuario_docente = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="asignaciones_docentes",
        verbose_name="Docente",
    )
    grupo_academico = models.ForeignKey(
        GrupoAcademico,
        on_delete=models.PROTECT,
        related_name="asignaciones_docentes",
        verbose_name="Grupo académico",
    )
    programa_asignatura = models.ForeignKey(
        ProgramaAsignatura,
        on_delete=models.PROTECT,
        db_column="materia_plan_id",
        related_name="asignaciones_docentes",
        verbose_name="Programa de asignatura",
    )
    vigente_desde = models.DateField(
        null=True,
        blank=True,
        default=timezone.localdate,
        verbose_name="Vigente desde",
    )
    vigente_hasta = models.DateField(null=True, blank=True, verbose_name="Vigente hasta")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        ordering = [
            "-activo",
            "grupo_academico__periodo__anio_escolar",
            "grupo_academico__clave_grupo",
            "programa_asignatura__materia__clave",
        ]
        verbose_name = "Asignación docente"
        verbose_name_plural = "Asignaciones docentes"
        constraints = [
            models.UniqueConstraint(
                fields=["grupo_academico", "programa_asignatura"],
                condition=models.Q(activo=True),
                name="uq_asignaciondocente_activa_grupo_programa",
            )
        ]

    @property
    def periodo(self):
        return self.grupo_academico.periodo

    def _ensure_vigencia_defaults(self):
        if not self.vigente_desde:
            self.vigente_desde = timezone.localdate()

    def clean(self):
        self._ensure_vigencia_defaults()
        errors = {}

        if self.usuario_docente_id:
            if not usuario_activo_con_rol(self.usuario_docente, ROL_DOCENTE):
                errors["usuario_docente"] = "Solo se puede asignar un usuario activo con rol DOCENTE."

        if self.grupo_academico_id:
            if self.grupo_academico.estado != ESTADO_ACTIVO:
                errors["grupo_academico"] = "Solo se puede asignar un grupo académico activo."
            elif self.grupo_academico.periodo.estado != ESTADO_ACTIVO:
                errors["grupo_academico"] = "El periodo del grupo debe estar activo."

        if self.programa_asignatura_id:
            if (
                self.programa_asignatura.plan_estudios.estado != ESTADO_ACTIVO
                or self.programa_asignatura.materia.estado != ESTADO_ACTIVO
            ):
                errors["programa_asignatura"] = (
                    "Solo se puede asignar un programa de asignatura activo."
                )

        if self.grupo_academico_id and self.programa_asignatura_id:
            if (
                self.programa_asignatura.plan_estudios_id
                != self.grupo_academico.antiguedad.plan_estudios_id
            ):
                errors["programa_asignatura"] = (
                    "El programa de asignatura debe pertenecer al plan del grupo."
                )
            elif not self.programa_asignatura.aplica_para_grupo(self.grupo_academico):
                if self.programa_asignatura.ubicacion_excepcional:
                    errors["programa_asignatura"] = (
                        "No existe una ubicación excepcional activa para la antigüedad "
                        "y semestre del grupo."
                    )
                else:
                    errors["programa_asignatura"] = (
                        "El semestre del programa debe coincidir con el semestre del grupo."
                    )

        if self.vigente_hasta and self.vigente_desde and self.vigente_hasta < self.vigente_desde:
            errors["vigente_hasta"] = "No puede ser anterior a 'vigente_desde'."

        if self.activo and self.grupo_academico_id and self.programa_asignatura_id:
            duplicada = AsignacionDocente.objects.filter(
                activo=True,
                grupo_academico=self.grupo_academico,
                programa_asignatura=self.programa_asignatura,
            )
            if self.pk:
                duplicada = duplicada.exclude(pk=self.pk)
            if duplicada.exists():
                errors["programa_asignatura"] = (
                    "Ya existe una asignación docente activa para este grupo y programa."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        if self.activo:
            from .services import sincronizar_carga_academica

            sincronizar_carga_academica(self)

    def __str__(self):
        return (
            f"{self.usuario_docente} - {self.grupo_academico.clave_grupo} - "
            f"{self.programa_asignatura} - {self.periodo}"
        )


class InscripcionMateria(models.Model):
    ESTADO_INSCRITA = "inscrita"
    ESTADO_BAJA = "baja"
    ESTADO_CERRADA = "cerrada"

    ESTADO_INSCRIPCION_CHOICES = [
        (ESTADO_INSCRITA, "Inscrita"),
        (ESTADO_BAJA, "Baja"),
        (ESTADO_CERRADA, "Cerrada"),
    ]

    discente = models.ForeignKey(
        Discente,
        on_delete=models.PROTECT,
        related_name="inscripciones_materia",
        verbose_name="Discente",
    )
    asignacion_docente = models.ForeignKey(
        AsignacionDocente,
        on_delete=models.PROTECT,
        related_name="inscripciones_materia",
        verbose_name="Asignación docente",
    )
    estado_inscripcion = models.CharField(
        max_length=20,
        choices=ESTADO_INSCRIPCION_CHOICES,
        default=ESTADO_INSCRITA,
        verbose_name="Estado de inscripción",
    )
    intento_numero = models.PositiveSmallIntegerField(default=1, verbose_name="Intento")
    calificacion_final = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Calificación final",
    )
    codigo_resultado_oficial = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Código de resultado oficial",
    )
    codigo_marca = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Código de marca",
    )
    cerrado_en = models.DateTimeField(null=True, blank=True, verbose_name="Cerrado en")

    class Meta:
        ordering = [
            "discente__matricula",
            "asignacion_docente__grupo_academico__periodo__anio_escolar",
            "asignacion_docente__programa_asignatura__materia__clave",
            "intento_numero",
        ]
        verbose_name = "Inscripción a asignatura"
        verbose_name_plural = "Inscripciones a asignatura"
        constraints = [
            models.UniqueConstraint(
                fields=["discente", "asignacion_docente"],
                condition=models.Q(estado_inscripcion="inscrita"),
                name="uq_inscripcionmateria_activa_discente_asignacion",
            )
        ]

    @property
    def activa(self):
        return self.estado_inscripcion == self.ESTADO_INSCRITA

    @property
    def programa_asignatura(self):
        return self.asignacion_docente.programa_asignatura

    def clean(self):
        errors = {}

        if self.intento_numero is not None and self.intento_numero < 1:
            errors["intento_numero"] = "Debe ser mayor a 0."

        if self.discente_id and not self.discente.activo:
            errors["discente"] = "Solo se puede inscribir un discente activo."

        if self.asignacion_docente_id:
            if not self.asignacion_docente.activo:
                errors["asignacion_docente"] = "Solo se puede usar una asignación docente activa."
            elif self.asignacion_docente.grupo_academico.estado != ESTADO_ACTIVO:
                errors["asignacion_docente"] = "El grupo de la asignación debe estar activo."

        if self.discente_id and self.asignacion_docente_id:
            programa = self.asignacion_docente.programa_asignatura
            grupo = self.asignacion_docente.grupo_academico
            if self.discente.plan_estudios_id != programa.plan_estudios_id:
                errors["asignacion_docente"] = (
                    "El programa de asignatura debe pertenecer al plan del discente."
                )
            elif self.discente.antiguedad_id != grupo.antiguedad_id:
                errors["asignacion_docente"] = (
                    "El grupo académico debe corresponder a la antigüedad del discente."
                )
            elif not AdscripcionGrupo.objects.filter(
                discente=self.discente,
                grupo_academico=grupo,
                activo=True,
            ).exists():
                errors["discente"] = (
                    "El discente debe tener adscripción activa al grupo de la asignación."
                )

            if self.activa:
                duplicada = InscripcionMateria.objects.filter(
                    discente=self.discente,
                    estado_inscripcion=self.ESTADO_INSCRITA,
                    asignacion_docente=self.asignacion_docente,
                )
                if self.pk:
                    duplicada = duplicada.exclude(pk=self.pk)
                if duplicada.exists():
                    errors["asignacion_docente"] = (
                        "Ya existe una inscripción activa para este discente y asignación docente."
                    )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.discente} - {self.asignacion_docente}"


class MovimientoAcademico(models.Model):
    CAMBIO_GRUPO = "cambio_grupo"
    ALTA_EXTEMPORANEA = "alta_extemporanea"
    BAJA_EXTEMPORANEA = "baja_extemporanea"

    TIPO_MOVIMIENTO_CHOICES = [
        (CAMBIO_GRUPO, "Cambio de grupo"),
        (ALTA_EXTEMPORANEA, "Alta extemporánea"),
        (BAJA_EXTEMPORANEA, "Baja extemporánea"),
    ]

    discente = models.ForeignKey(
        Discente,
        on_delete=models.PROTECT,
        related_name="movimientos_academicos",
        verbose_name="Discente",
    )
    periodo = models.ForeignKey(
        PeriodoEscolar,
        on_delete=models.PROTECT,
        db_column="periodo_escolar_id",
        related_name="movimientos_academicos",
        verbose_name="Periodo escolar",
    )
    tipo_movimiento = models.CharField(
        max_length=30,
        choices=TIPO_MOVIMIENTO_CHOICES,
        verbose_name="Tipo de movimiento",
    )
    grupo_origen = models.ForeignKey(
        GrupoAcademico,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="movimientos_origen",
        verbose_name="Grupo origen",
    )
    grupo_destino = models.ForeignKey(
        GrupoAcademico,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="movimientos_destino",
        verbose_name="Grupo destino",
    )
    fecha_movimiento = models.DateField(
        default=timezone.localdate,
        verbose_name="Fecha de movimiento",
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        ordering = ["-fecha_movimiento", "discente__matricula"]
        verbose_name = "Movimiento académico"
        verbose_name_plural = "Movimientos académicos"

    def clean(self):
        errors = {}

        if self.discente_id and not self.discente.activo:
            errors["discente"] = "Solo se puede registrar movimiento para un discente activo."

        if self.periodo_id and self.periodo.estado != ESTADO_ACTIVO:
            errors["periodo"] = "Solo se puede asignar un periodo activo."

        for field_name in ("grupo_origen", "grupo_destino"):
            grupo = getattr(self, field_name)
            if grupo and grupo.estado != ESTADO_ACTIVO:
                errors[field_name] = "Solo se puede asignar un grupo académico activo."
            elif grupo and self.periodo_id and grupo.periodo_id != self.periodo_id:
                errors[field_name] = "El grupo debe pertenecer al periodo seleccionado."

        if self.tipo_movimiento == self.CAMBIO_GRUPO:
            if not self.grupo_origen_id:
                errors["grupo_origen"] = "El grupo origen es obligatorio para cambios de grupo."
            if not self.grupo_destino_id:
                errors["grupo_destino"] = "El grupo destino es obligatorio para cambios de grupo."
            if (
                self.grupo_origen_id
                and self.grupo_destino_id
                and self.grupo_origen_id == self.grupo_destino_id
            ):
                errors["grupo_destino"] = "El grupo destino debe ser distinto al grupo origen."

        if self.discente_id:
            for field_name in ("grupo_origen", "grupo_destino"):
                grupo = getattr(self, field_name)
                if grupo and grupo.antiguedad_id != self.discente.antiguedad_id:
                    errors[field_name] = (
                        "El grupo debe corresponder a la antigüedad del discente."
                    )

        if self.tipo_movimiento in (self.ALTA_EXTEMPORANEA, self.BAJA_EXTEMPORANEA):
            if len((self.observaciones or "").strip()) < OBSERVACIONES_EXTEMPORANEAS_MIN_LENGTH:
                errors["observaciones"] = (
                    "Las altas y bajas extemporáneas requieren observaciones mínimas."
                )

        if errors:
            raise ValidationError(errors)

    def aplicar_cambio_grupo(self):
        if self.tipo_movimiento != self.CAMBIO_GRUPO:
            return None

        with transaction.atomic():
            adscripciones_mismo_periodo = AdscripcionGrupo.objects.select_for_update().filter(
                discente=self.discente,
                grupo_academico__periodo=self.periodo,
                activo=True,
            )
            adscripcion_origen = adscripciones_mismo_periodo.filter(
                grupo_academico=self.grupo_origen
            ).first()
            adscripcion_destino = adscripciones_mismo_periodo.filter(
                grupo_academico=self.grupo_destino
            ).first()

            if not adscripcion_origen:
                if not adscripcion_destino:
                    raise ValidationError(
                        {
                            "grupo_origen": (
                                "El grupo origen debe coincidir con la adscripción activa "
                                "del discente en el periodo seleccionado."
                            )
                        }
                    )
            else:
                otra_adscripcion_activa = (
                    adscripciones_mismo_periodo.exclude(pk=adscripcion_origen.pk)
                    .exclude(grupo_academico=self.grupo_destino)
                    .first()
                )
                if otra_adscripcion_activa:
                    raise ValidationError(
                        {
                            "discente": (
                                "El discente tiene otra adscripción activa en el periodo; "
                                "corrige esa inconsistencia antes de aplicar el movimiento."
                            )
                        }
                    )

                adscripcion_origen.activo = False
                adscripcion_origen.vigente_hasta = self.fecha_movimiento
                adscripcion_origen.save(update_fields=["activo", "vigente_hasta"])

            if adscripcion_destino:
                destino = adscripcion_destino
            else:
                destino = AdscripcionGrupo.objects.create(
                    discente=self.discente,
                    grupo_academico=self.grupo_destino,
                    vigente_desde=self.fecha_movimiento,
                    activo=True,
                )

            self._validar_inscripciones_origen_sin_actas_vivas()
            self._dar_baja_inscripciones_origen()
            self._crear_inscripciones_destino()
            return destino

    def _inscripciones_origen_activas(self):
        return InscripcionMateria.objects.select_for_update().filter(
            discente=self.discente,
            asignacion_docente__grupo_academico=self.grupo_origen,
            asignacion_docente__grupo_academico__periodo=self.periodo,
            estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA,
        )

    def _validar_inscripciones_origen_sin_actas_vivas(self):
        from evaluacion.models import Acta, DetalleActa

        inscripciones_origen = self._inscripciones_origen_activas()
        tiene_acta_viva = DetalleActa.objects.filter(
            inscripcion_materia__in=inscripciones_origen,
        ).exclude(acta__estado_acta=Acta.ESTADO_ARCHIVADO).exists()
        if tiene_acta_viva:
            raise ValidationError(
                {
                    "discente": (
                        "No se puede aplicar el cambio de grupo porque existen actas "
                        "no archivadas para inscripciones del grupo origen."
                    )
                }
            )

    def _dar_baja_inscripciones_origen(self):
        self._inscripciones_origen_activas().update(
            estado_inscripcion=InscripcionMateria.ESTADO_BAJA
        )

    def _crear_inscripciones_destino(self):
        asignaciones_destino = AsignacionDocente.objects.filter(
            activo=True,
            grupo_academico=self.grupo_destino,
        )
        for asignacion in asignaciones_destino:
            existe_activa = InscripcionMateria.objects.filter(
                discente=self.discente,
                asignacion_docente=asignacion,
                estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA,
            ).exists()
            if existe_activa:
                continue

            InscripcionMateria.objects.create(
                discente=self.discente,
                asignacion_docente=asignacion,
                estado_inscripcion=InscripcionMateria.ESTADO_INSCRITA,
                intento_numero=1,
            )

    def save(self, *args, **kwargs):
        creando = self._state.adding
        with transaction.atomic():
            self.full_clean()
            resultado = super().save(*args, **kwargs)
            if creando:
                self.aplicar_cambio_grupo()
            return resultado

    def __str__(self):
        return f"{self.discente} - {self.get_tipo_movimiento_display()}"
