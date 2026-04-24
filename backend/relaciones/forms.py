from django import forms

from catalogos.models import ESTADO_ACTIVO, GrupoAcademico, PeriodoEscolar, ProgramaAsignatura
from usuarios.models import Usuario

from .models import (
    ROL_DISCENTE,
    ROL_DOCENTE,
    AdscripcionGrupo,
    Discente,
    AsignacionDocente,
    InscripcionMateria,
    MovimientoAcademico,
)


def usuarios_activos_queryset(rol=None):
    queryset = Usuario.objects.filter(
        is_active=True,
        estado_cuenta=Usuario.ESTADO_ACTIVO,
    )
    if rol:
        queryset = queryset.filter(groups__name=rol)
    return queryset.distinct().order_by("username")


def grupos_activos_queryset():
    return (
        GrupoAcademico.objects.filter(
            estado=ESTADO_ACTIVO,
            periodo__estado=ESTADO_ACTIVO,
            antiguedad__estado=ESTADO_ACTIVO,
        )
        .select_related("periodo", "antiguedad", "antiguedad__plan_estudios")
        .order_by("periodo__anio_escolar", "clave_grupo")
    )


def programas_activos_queryset():
    return (
        ProgramaAsignatura.objects.filter(
            plan_estudios__estado=ESTADO_ACTIVO,
            materia__estado=ESTADO_ACTIVO,
        )
        .select_related("plan_estudios", "materia")
        .order_by("plan_estudios__clave", "materia__clave")
    )


class DiscenteAdminForm(forms.ModelForm):
    class Meta:
        model = Discente
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["usuario"].queryset = usuarios_activos_queryset(ROL_DISCENTE)
        self.fields["plan_estudios"].queryset = self.fields["plan_estudios"].queryset.filter(
            estado=ESTADO_ACTIVO
        )
        self.fields["antiguedad"].queryset = self.fields["antiguedad"].queryset.filter(
            estado=ESTADO_ACTIVO,
            plan_estudios__estado=ESTADO_ACTIVO,
        )


class AdscripcionGrupoForm(forms.ModelForm):
    class Meta:
        model = AdscripcionGrupo
        fields = [
            "discente",
            "grupo_academico",
            "vigente_desde",
            "vigente_hasta",
            "activo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["discente"].queryset = Discente.objects.filter(
            activo=True,
            usuario__is_active=True,
            usuario__estado_cuenta=Usuario.ESTADO_ACTIVO,
            usuario__groups__name=ROL_DISCENTE,
        ).select_related("usuario", "plan_estudios", "antiguedad").distinct()
        self.fields["grupo_academico"].queryset = grupos_activos_queryset()


class AsignacionDocenteForm(forms.ModelForm):
    class Meta:
        model = AsignacionDocente
        fields = [
            "usuario_docente",
            "grupo_academico",
            "programa_asignatura",
            "vigente_desde",
            "vigente_hasta",
            "activo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["usuario_docente"].queryset = usuarios_activos_queryset(ROL_DOCENTE)
        self.fields["grupo_academico"].queryset = grupos_activos_queryset()
        self.fields["programa_asignatura"].queryset = programas_activos_queryset()


class InscripcionMateriaForm(forms.ModelForm):
    class Meta:
        model = InscripcionMateria
        fields = [
            "discente",
            "asignacion_docente",
            "estado_inscripcion",
            "intento_numero",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["discente"].queryset = Discente.objects.filter(
            activo=True,
            usuario__is_active=True,
            usuario__estado_cuenta=Usuario.ESTADO_ACTIVO,
            usuario__groups__name=ROL_DISCENTE,
        ).select_related("usuario", "plan_estudios", "antiguedad").distinct()
        self.fields["asignacion_docente"].queryset = (
            AsignacionDocente.objects.filter(
                activo=True,
                usuario_docente__is_active=True,
                usuario_docente__estado_cuenta=Usuario.ESTADO_ACTIVO,
                usuario_docente__groups__name=ROL_DOCENTE,
                grupo_academico__estado=ESTADO_ACTIVO,
                grupo_academico__periodo__estado=ESTADO_ACTIVO,
                programa_asignatura__plan_estudios__estado=ESTADO_ACTIVO,
                programa_asignatura__materia__estado=ESTADO_ACTIVO,
            )
            .select_related(
                "usuario_docente",
                "grupo_academico",
                "grupo_academico__periodo",
                "programa_asignatura",
                "programa_asignatura__materia",
            )
            .distinct()
            .order_by("grupo_academico__clave_grupo", "programa_asignatura__materia__clave")
        )


class MovimientoAcademicoForm(forms.ModelForm):
    class Meta:
        model = MovimientoAcademico
        fields = [
            "discente",
            "periodo",
            "tipo_movimiento",
            "grupo_origen",
            "grupo_destino",
            "fecha_movimiento",
            "observaciones",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["discente"].queryset = Discente.objects.filter(
            activo=True,
            usuario__is_active=True,
            usuario__estado_cuenta=Usuario.ESTADO_ACTIVO,
            usuario__groups__name=ROL_DISCENTE,
        ).select_related("usuario", "plan_estudios", "antiguedad").distinct()
        self.fields["periodo"].queryset = PeriodoEscolar.objects.filter(
            estado=ESTADO_ACTIVO
        ).order_by("-anio_escolar", "-periodo_academico")
        self.fields["grupo_origen"].queryset = grupos_activos_queryset()
        self.fields["grupo_destino"].queryset = grupos_activos_queryset()
