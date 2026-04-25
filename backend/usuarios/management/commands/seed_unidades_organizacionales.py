import hashlib

from django.core.management.base import BaseCommand

from catalogos.models import ESTADO_ACTIVO, Carrera
from catalogos.validators import CLAVE_MAX_LENGTH
from usuarios.models import UnidadOrganizacional


class Command(BaseCommand):
    help = "Crea las unidades organizacionales base de forma idempotente."

    SECCIONES_BASE = (
        (
            UnidadOrganizacional.CLAVE_SECCION_PEDAGOGICA,
            "Sección Pedagógica",
        ),
        (
            UnidadOrganizacional.CLAVE_SECCION_ACADEMICA,
            "Sección Académica",
        ),
    )
    SUBSECCIONES_BASE = (
        (
            "SUB_PLAN_EVAL",
            "SUB_PE",
            "Subsección de Planeación y Evaluación",
            UnidadOrganizacional.CLAVE_SECCION_PEDAGOGICA,
        ),
        (
            "SUB_EJEC_CTRL",
            "SUB_EC",
            "Subsección de Ejecución y Control",
            UnidadOrganizacional.CLAVE_SECCION_ACADEMICA,
        ),
    )

    def handle(self, *args, **options):
        created_count = 0
        existing_count = 0
        warning_count = 0

        secciones = {}
        for clave, nombre in self.SECCIONES_BASE:
            unidad, created = UnidadOrganizacional.objects.get_or_create(
                clave=clave,
                defaults={
                    "nombre": nombre,
                    "tipo_unidad": UnidadOrganizacional.TIPO_SECCION,
                },
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Creada sección {clave}"))
            else:
                existing_count += 1
                warning_count += self._warn_if_incompatible(
                    unidad,
                    tipo_unidad=UnidadOrganizacional.TIPO_SECCION,
                    padre=None,
                    carrera=None,
                )
            secciones[clave] = unidad

        carreras = Carrera.objects.filter(estado=ESTADO_ACTIVO).order_by("clave")
        for carrera in carreras:
            for prefijo, prefijo_corto, nombre_base, clave_padre in self.SUBSECCIONES_BASE:
                clave = self._build_subseccion_clave(prefijo, prefijo_corto, carrera.clave)
                unidad, created = UnidadOrganizacional.objects.get_or_create(
                    clave=clave,
                    defaults={
                        "nombre": f"{nombre_base} {carrera.clave}",
                        "tipo_unidad": UnidadOrganizacional.TIPO_SUBSECCION,
                        "padre": secciones[clave_padre],
                        "carrera": carrera,
                    },
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Creada subsección {clave}"))
                else:
                    existing_count += 1
                    warning_count += self._warn_if_incompatible(
                        unidad,
                        tipo_unidad=UnidadOrganizacional.TIPO_SUBSECCION,
                        padre=secciones[clave_padre],
                        carrera=carrera,
                    )

        self.stdout.write(
            self.style.SUCCESS(
                "Unidades organizacionales base procesadas: "
                f"{created_count} creadas, {existing_count} existentes, "
                f"{warning_count} advertencias."
            )
        )

    def _build_subseccion_clave(self, prefijo, prefijo_corto, clave_carrera):
        clave = f"{prefijo}_{clave_carrera}"
        if len(clave) <= CLAVE_MAX_LENGTH:
            return clave

        digest = hashlib.blake2s(clave_carrera.encode("utf-8"), digest_size=2).hexdigest().upper()
        espacio_carrera = CLAVE_MAX_LENGTH - len(prefijo_corto) - len(digest) - 2
        carrera_recortada = clave_carrera[:espacio_carrera]
        return f"{prefijo_corto}_{carrera_recortada}_{digest}"

    def _warn_if_incompatible(self, unidad, tipo_unidad, padre, carrera):
        errores = []
        if unidad.tipo_unidad != tipo_unidad:
            errores.append(f"tipo={unidad.tipo_unidad}, esperado={tipo_unidad}")
        if unidad.padre_id != (padre.id if padre else None):
            errores.append("padre distinto al esperado")
        if unidad.carrera_id != (carrera.id if carrera else None):
            errores.append("carrera distinta a la esperada")

        if not errores:
            return 0

        self.stdout.write(
            self.style.WARNING(
                f"Advertencia: {unidad.clave} ya existe con datos diferentes: "
                + "; ".join(errores)
            )
        )
        return 1
