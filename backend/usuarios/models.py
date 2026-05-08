from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from catalogos.models import Carrera
from catalogos.validators import CLAVE_MAX_LENGTH, clave_format_validator


class GradoEmpleo(models.Model):
    TIPO_MILITAR_ACTIVO = "MILITAR_ACTIVO"
    TIPO_MILITAR_RETIRADO = "MILITAR_RETIRADO"
    TIPO_CIVIL = "CIVIL"
    TIPO_OTRO = "OTRO"

    TIPO_CHOICES = [
        (TIPO_MILITAR_ACTIVO, "Militar activo"),
        (TIPO_MILITAR_RETIRADO, "Militar retirado"),
        (TIPO_CIVIL, "Civil"),
        (TIPO_OTRO, "Otro"),
    ]

    clave = models.CharField(
        max_length=CLAVE_MAX_LENGTH,
        validators=[clave_format_validator],
        unique=True,
        verbose_name="Clave",
    )
    abreviatura = models.CharField(max_length=80, verbose_name="Abreviatura")
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        ordering = ["tipo", "abreviatura", "nombre"]
        verbose_name = "Grado/empleo"
        verbose_name_plural = "Grados/empleos"

    def __str__(self) -> str:
        return self.abreviatura


class Usuario(AbstractUser):
    ESTADO_ACTIVO = "activo"
    ESTADO_INACTIVO = "inactivo"
    ESTADO_BLOQUEADO = "bloqueado"

    ESTADO_CUENTA_CHOICES = [
        (ESTADO_ACTIVO, "Activo"),
        (ESTADO_INACTIVO, "Inactivo"),
        (ESTADO_BLOQUEADO, "Bloqueado"),
    ]

    last_login = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Último ingreso",
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name="Fecha de creación",
    )
    estado_cuenta = models.CharField(
        max_length=20,
        choices=ESTADO_CUENTA_CHOICES,
        default=ESTADO_ACTIVO,
    )
    nombre_completo = models.CharField(max_length=255, blank=True)
    grado_empleo = models.ForeignKey(
        GradoEmpleo,
        on_delete=models.SET_NULL,
        related_name="usuarios",
        null=True,
        blank=True,
        verbose_name="Grado/empleo",
    )
    correo = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    ultimo_acceso = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Último acceso",
    )

    @property
    def roles(self):
        return list(self.groups.values_list("name", flat=True))

    def tiene_rol(self, nombre_rol: str) -> bool:
        return self.groups.filter(name=nombre_rol).exists()

    @property
    def nombre_visible(self) -> str:
        return self.nombre_completo or self.username

    @property
    def nombre_institucional(self) -> str:
        if self.grado_empleo_id and self.grado_empleo.abreviatura:
            return f"{self.grado_empleo.abreviatura} {self.nombre_visible}".strip()
        return self.nombre_visible

    def save(self, *args, **kwargs):
        if self.correo and not self.email:
            self.email = self.correo
        elif self.email and not self.correo:
            self.correo = self.email
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username


class UnidadOrganizacional(models.Model):
    CLAVE_SECCION_PEDAGOGICA = "SEC_PEDAGOGICA"
    CLAVE_SECCION_ACADEMICA = "SEC_ACADEMICA"

    TIPO_SECCION = "SECCION"
    TIPO_SUBSECCION = "SUBSECCION"

    TIPO_UNIDAD_CHOICES = [
        (TIPO_SECCION, "Sección"),
        (TIPO_SUBSECCION, "Subsección"),
    ]

    clave = models.CharField(
        max_length=CLAVE_MAX_LENGTH,
        validators=[clave_format_validator],
        unique=True,
        verbose_name="Clave",
    )
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    tipo_unidad = models.CharField(
        max_length=20,
        choices=TIPO_UNIDAD_CHOICES,
        verbose_name="Tipo de unidad",
    )
    padre = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="subunidades",
        null=True,
        blank=True,
        verbose_name="Unidad padre",
    )
    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.PROTECT,
        related_name="unidades_organizacionales",
        null=True,
        blank=True,
        verbose_name="Carrera",
        help_text="Solo se captura cuando la unidad pertenece a una carrera.",
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")
    orden = models.PositiveSmallIntegerField(default=0, verbose_name="Orden")

    class Meta:
        ordering = ["orden", "tipo_unidad", "nombre"]
        verbose_name = "Unidad organizacional"
        verbose_name_plural = "Unidades organizacionales"

    def clean(self):
        errors = {}

        if self.pk and self.padre_id == self.pk:
            errors["padre"] = "Una unidad no puede ser padre de sí misma."

        if self.tipo_unidad == self.TIPO_SECCION:
            if self.padre_id:
                errors["padre"] = "Una sección no debe depender de otra unidad."
            if self.carrera_id:
                errors["carrera"] = "Una sección no debe tener carrera asignada."

        if self.tipo_unidad == self.TIPO_SUBSECCION:
            if not self.padre_id:
                errors["padre"] = "Una subsección debe tener una sección padre."
            elif self.padre.tipo_unidad != self.TIPO_SECCION:
                errors["padre"] = "La unidad padre de una subsección debe ser una sección."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.carrera_id:
            return f"{self.nombre} - {self.carrera.clave}"
        return self.nombre


class AsignacionCargo(models.Model):
    ROL_DISCENTE = "DISCENTE"
    ROL_DOCENTE = "DOCENTE"
    ROL_JEFE_PEDAGOGICA = "JEFE_PEDAGOGICA"
    ROL_JEFE_ACADEMICO = "JEFE_ACADEMICO"
    ROL_JEFATURA_ACADEMICA = "JEFATURA_ACADEMICA"
    ROL_JEFE_CARRERA = "JEFE_CARRERA"
    ROL_JEFATURA_CARRERA = "JEFATURA_CARRERA"
    ROL_JEFE_SUB_PLAN_EVAL = "JEFE_SUB_PLAN_EVAL"
    ROL_JEFE_SUB_EJEC_CTR = "JEFE_SUB_EJEC_CTR"

    CARGO_JEFE_CARRERA = "JEFE_CARRERA"
    CARGO_JEFE_ACADEMICO = "JEFE_ACADEMICO"
    CARGO_JEFE_PEDAGOGICA = "JEFE_PEDAGOGICA"
    CARGO_JEFE_SUBSECCION_PEDAGOGICA = "JEFE_SUBSECCION_PEDAGOGICA"
    CARGO_JEFE_SUB_PLAN_EVAL = "JEFE_SUB_PLAN_EVAL"
    CARGO_JEFE_SUB_EJEC_CTR = "JEFE_SUB_EJEC_CTR"
    CARGO_DOCENTE = "DOCENTE"

    CARGO_CHOICES = [
        (CARGO_JEFE_CARRERA, "Jefe de carrera"),
        (CARGO_JEFE_ACADEMICO, "Jefe académico"),
        (CARGO_JEFE_PEDAGOGICA, "Jefe de Pedagógica"),
        (CARGO_JEFE_SUBSECCION_PEDAGOGICA, "Jefe de subsección de Planeación y Evaluación"),
        (CARGO_JEFE_SUB_PLAN_EVAL, "Jefe de subsección de Planeación y Evaluación"),
        (CARGO_JEFE_SUB_EJEC_CTR, "Jefe de subsección de Ejecución y Control"),
        (CARGO_DOCENTE, "Docente"),
    ]

    CARGOS_POR_CARRERA = {
        CARGO_JEFE_CARRERA,
        CARGO_JEFE_SUBSECCION_PEDAGOGICA,
        CARGO_JEFE_SUB_PLAN_EVAL,
        CARGO_JEFE_SUB_EJEC_CTR,
    }
    CARGOS_CON_UNIDAD = {
        CARGO_JEFE_PEDAGOGICA,
        CARGO_JEFE_ACADEMICO,
        CARGO_JEFE_CARRERA,
        CARGO_JEFE_SUBSECCION_PEDAGOGICA,
        CARGO_JEFE_SUB_PLAN_EVAL,
        CARGO_JEFE_SUB_EJEC_CTR,
    }
    CARGOS_SECCION_CLAVE = {
        CARGO_JEFE_PEDAGOGICA: UnidadOrganizacional.CLAVE_SECCION_PEDAGOGICA,
        CARGO_JEFE_ACADEMICO: UnidadOrganizacional.CLAVE_SECCION_ACADEMICA,
    }
    CARGOS_SUBSECCION_PADRE_CLAVE = {
        CARGO_JEFE_CARRERA: UnidadOrganizacional.CLAVE_SECCION_ACADEMICA,
        CARGO_JEFE_SUBSECCION_PEDAGOGICA: UnidadOrganizacional.CLAVE_SECCION_PEDAGOGICA,
        CARGO_JEFE_SUB_PLAN_EVAL: UnidadOrganizacional.CLAVE_SECCION_PEDAGOGICA,
        CARGO_JEFE_SUB_EJEC_CTR: UnidadOrganizacional.CLAVE_SECCION_ACADEMICA,
    }
    GRUPOS_COMPATIBLES_POR_CARGO = {
        CARGO_DOCENTE: {ROL_DOCENTE},
        CARGO_JEFE_PEDAGOGICA: {ROL_JEFE_PEDAGOGICA},
        CARGO_JEFE_ACADEMICO: {ROL_JEFE_ACADEMICO, ROL_JEFATURA_ACADEMICA},
        CARGO_JEFE_CARRERA: {ROL_JEFE_CARRERA, ROL_JEFATURA_CARRERA},
        CARGO_JEFE_SUBSECCION_PEDAGOGICA: {ROL_JEFE_PEDAGOGICA},
        CARGO_JEFE_SUB_PLAN_EVAL: {ROL_JEFE_SUB_PLAN_EVAL},
        CARGO_JEFE_SUB_EJEC_CTR: {ROL_JEFE_SUB_EJEC_CTR},
    }

    DESIGNACION_TITULAR = "titular"
    DESIGNACION_ACCIDENTAL = "accidental"

    TIPO_DESIGNACION_CHOICES = [
        (DESIGNACION_TITULAR, "Titular"),
        (DESIGNACION_ACCIDENTAL, "Accidental"),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="asignaciones_cargo",
    )
    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.PROTECT,
        related_name="asignaciones_cargo",
        null=True,
        blank=True,
        verbose_name="Carrera",
        help_text=(
            "Se conserva por compatibilidad. Si también se captura unidad organizacional "
            "con carrera, ambas deben coincidir."
        ),
    )
    unidad_organizacional = models.ForeignKey(
        UnidadOrganizacional,
        on_delete=models.PROTECT,
        related_name="asignaciones_cargo",
        null=True,
        blank=True,
        verbose_name="Unidad organizacional",
    )
    cargo_codigo = models.CharField(
        max_length=50,
        choices=CARGO_CHOICES,
        verbose_name="Cargo",
    )
    tipo_designacion = models.CharField(
        max_length=20,
        choices=TIPO_DESIGNACION_CHOICES,
    )
    vigente_desde = models.DateField(
        null=True,
        blank=True,
        default=timezone.localdate,
    )
    vigente_hasta = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    def _ensure_vigencia_defaults(self):
        if not self.vigente_desde:
            self.vigente_desde = timezone.localdate()

    class Meta:
        ordering = ["-activo", "-vigente_desde", "cargo_codigo"]

    def requiere_carrera(self):
        return self.cargo_codigo in self.CARGOS_POR_CARRERA

    def requiere_unidad_organizacional(self):
        return self.cargo_codigo in self.CARGOS_CON_UNIDAD

    def cargo_descripcion(self):
        descripcion = self.get_cargo_codigo_display()
        if self.carrera_id:
            return f"{descripcion} de {self.carrera}"
        return descripcion

    def _add_error(self, errors, field, message):
        errors.setdefault(field, []).append(message)

    def _validar_compatibilidad_unidad(self, errors):
        unidad = self.unidad_organizacional
        if not unidad:
            return

        if self.cargo_codigo in self.CARGOS_SECCION_CLAVE:
            clave_esperada = self.CARGOS_SECCION_CLAVE[self.cargo_codigo]
            if unidad.tipo_unidad != UnidadOrganizacional.TIPO_SECCION:
                self._add_error(
                    errors,
                    "unidad_organizacional",
                    "Este cargo debe asignarse a una unidad tipo sección.",
                )
            elif unidad.clave != clave_esperada:
                self._add_error(
                    errors,
                    "unidad_organizacional",
                    f"Este cargo debe asignarse a la unidad {clave_esperada}.",
                )
            if self.carrera_id:
                self._add_error(
                    errors,
                    "carrera",
                    "Este cargo es de sección y no debe tener carrera asignada.",
                )
            return

        if self.cargo_codigo in self.CARGOS_SUBSECCION_PADRE_CLAVE:
            clave_padre_esperada = self.CARGOS_SUBSECCION_PADRE_CLAVE[self.cargo_codigo]
            if unidad.tipo_unidad != UnidadOrganizacional.TIPO_SUBSECCION:
                self._add_error(
                    errors,
                    "unidad_organizacional",
                    "Este cargo debe asignarse a una unidad tipo subsección.",
                )
            elif not unidad.padre_id or unidad.padre.clave != clave_padre_esperada:
                self._add_error(
                    errors,
                    "unidad_organizacional",
                    f"Este cargo debe depender de la unidad {clave_padre_esperada}.",
                )

            if not unidad.carrera_id:
                self._add_error(
                    errors,
                    "unidad_organizacional",
                    "La unidad organizacional debe tener carrera asociada para este cargo.",
                )
            elif self.carrera_id and self.carrera_id != unidad.carrera_id:
                self._add_error(
                    errors,
                    "carrera",
                    "La carrera debe coincidir con la carrera de la unidad organizacional.",
                )

    def _validar_traslape_designacion(self, errors):
        if not self.activo or not self.requiere_unidad_organizacional():
            return
        if not self.unidad_organizacional_id or not self.vigente_desde:
            return

        traslapadas = AsignacionCargo.objects.filter(
            activo=True,
            cargo_codigo=self.cargo_codigo,
            tipo_designacion=self.tipo_designacion,
            unidad_organizacional_id=self.unidad_organizacional_id,
        )
        if self.pk:
            traslapadas = traslapadas.exclude(pk=self.pk)

        traslapadas = traslapadas.filter(
            models.Q(vigente_hasta__isnull=True)
            | models.Q(vigente_hasta__gte=self.vigente_desde)
        )
        if self.vigente_hasta:
            traslapadas = traslapadas.filter(
                models.Q(vigente_desde__isnull=True)
                | models.Q(vigente_desde__lte=self.vigente_hasta)
            )

        if not traslapadas.exists():
            return

        if self.tipo_designacion == self.DESIGNACION_TITULAR:
            self._add_error(
                errors,
                "tipo_designacion",
                "Ya existe una jefatura titular activa para este cargo y unidad en el periodo indicado.",
            )
        elif self.tipo_designacion == self.DESIGNACION_ACCIDENTAL:
            self._add_error(
                errors,
                "tipo_designacion",
                "Ya existe una designación accidental activa traslapada para este cargo y unidad.",
            )

    def _validar_compatibilidad_rol_usuario(self, errors):
        if not self.usuario_id:
            return

        grupos_usuario = set(self.usuario.groups.values_list("name", flat=True))
        if self.ROL_DISCENTE in grupos_usuario:
            self._add_error(
                errors,
                "usuario",
                "Un usuario con rol DISCENTE no puede recibir cargos institucionales.",
            )
            return

        grupos_requeridos = self.GRUPOS_COMPATIBLES_POR_CARGO.get(self.cargo_codigo, set())
        if grupos_requeridos and grupos_usuario.isdisjoint(grupos_requeridos):
            grupos = ", ".join(sorted(grupos_requeridos))
            self._add_error(
                errors,
                "usuario",
                f"El usuario debe pertenecer a un grupo compatible con este cargo: {grupos}.",
            )

    def clean(self):
        self._ensure_vigencia_defaults()
        errors = {}

        self._validar_compatibilidad_rol_usuario(errors)

        if self.requiere_unidad_organizacional() and not self.unidad_organizacional_id:
            self._add_error(
                errors,
                "unidad_organizacional",
                "Debe seleccionar la unidad organizacional para este cargo.",
            )
        elif self.unidad_organizacional_id:
            self._validar_compatibilidad_unidad(errors)

        if self.carrera_id and not self.requiere_carrera():
            self._add_error(
                errors,
                "carrera",
                "La carrera solo aplica para cargos por carrera o subsección por carrera.",
            )

        if self.vigente_hasta and self.vigente_hasta < self.vigente_desde:
            self._add_error(errors, "vigente_hasta", "No puede ser anterior a 'vigente_desde'.")

        if self.tipo_designacion == self.DESIGNACION_ACCIDENTAL and not self.vigente_hasta:
            self._add_error(
                errors,
                "vigente_hasta",
                "Las designaciones accidentales deben tener fecha de término.",
            )

        self._validar_traslape_designacion(errors)

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self._ensure_vigencia_defaults()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.usuario.username} - {self.cargo_descripcion()}"
