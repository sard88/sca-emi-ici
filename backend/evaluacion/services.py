from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError

from .models import CapturaCalificacionPreliminar, ComponenteEvaluacion, EsquemaEvaluacion


CALIFICACION_APROBATORIA = Decimal("6.0")
UMBRAL_EXENCION_INSTITUCIONAL = Decimal("9.0")


def redondear_visualizacion_un_decimal(valor):
    if valor is None:
        return None
    return Decimal(valor).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


class ServicioCalculoAcademico:
    def __init__(self, inscripcion_materia):
        self.inscripcion_materia = inscripcion_materia
        self.esquema = self.obtener_esquema_activo(inscripcion_materia.programa_asignatura)
        self.componentes = list(
            self.esquema.componentes.all().order_by("corte_codigo", "orden", "pk")
        )
        self.capturas = {
            captura.componente_id: captura
            for captura in CapturaCalificacionPreliminar.objects.filter(
                inscripcion_materia=inscripcion_materia,
                componente__esquema=self.esquema,
            )
        }

    @staticmethod
    def obtener_esquema_activo(programa_asignatura):
        esquema = (
            EsquemaEvaluacion.objects.filter(
                programa_asignatura=programa_asignatura,
                activo=True,
            )
            .prefetch_related("componentes")
            .order_by("-id")
            .first()
        )
        if not esquema:
            raise ValidationError(
                "No existe un esquema de evaluación activo para este programa de asignatura."
            )
        return esquema

    def _componentes_corte(self, corte_codigo):
        return [
            componente
            for componente in self.componentes
            if componente.corte_codigo == corte_codigo
        ]

    def _valor_componente(self, componente, promedio_parciales=None, sustituir_examen=False):
        if (
            sustituir_examen
            and componente.corte_codigo == ComponenteEvaluacion.CORTE_FINAL
            and componente.es_examen
        ):
            return promedio_parciales

        captura = self.capturas.get(componente.id)
        if not captura:
            return None
        return captura.valor

    def calcular_resultado_corte(
        self,
        corte_codigo,
        promedio_parciales=None,
        sustituir_examen=False,
    ):
        componentes = self._componentes_corte(corte_codigo)
        detalle = []
        total = Decimal("0.00")
        completo = bool(componentes)

        for componente in componentes:
            valor = self._valor_componente(
                componente,
                promedio_parciales=promedio_parciales,
                sustituir_examen=sustituir_examen,
            )
            if valor is None:
                completo = False
                ponderado = None
            else:
                ponderado = Decimal(valor) * componente.porcentaje / Decimal("100")
                total += ponderado

            detalle.append(
                {
                    "componente": componente,
                    "valor": valor,
                    "porcentaje": componente.porcentaje,
                    "ponderado": ponderado,
                    "sustituido_por_exencion": (
                        sustituir_examen
                        and componente.corte_codigo == ComponenteEvaluacion.CORTE_FINAL
                        and componente.es_examen
                    ),
                }
            )

        return {
            "corte": corte_codigo,
            "componentes": detalle,
            "completo": completo,
            "resultado": total if completo else None,
            "resultado_visual": redondear_visualizacion_un_decimal(total) if completo else None,
        }

    def _cortes_parciales(self):
        cortes = [ComponenteEvaluacion.CORTE_P1]
        if self.esquema.num_parciales >= EsquemaEvaluacion.PARCIALES_2:
            cortes.append(ComponenteEvaluacion.CORTE_P2)
        if self.esquema.num_parciales >= EsquemaEvaluacion.PARCIALES_3:
            cortes.append(ComponenteEvaluacion.CORTE_P3)
        return cortes

    def _calcular_promedio_parciales(self, resultados_corte):
        resultados = []
        for corte in self._cortes_parciales():
            resultado = resultados_corte[corte]["resultado"]
            if resultado is None:
                return None
            resultados.append(resultado)
        return sum(resultados) / Decimal(len(resultados))

    def _exencion_aplica(self, promedio_parciales):
        if promedio_parciales is None:
            return False
        tiene_examen_final = any(
            componente.corte_codigo == ComponenteEvaluacion.CORTE_FINAL and componente.es_examen
            for componente in self.componentes
        )
        return (
            self.esquema.permite_exencion
            and self.esquema.num_parciales in (
                EsquemaEvaluacion.PARCIALES_2,
                EsquemaEvaluacion.PARCIALES_3,
            )
            and promedio_parciales
            >= (self.esquema.umbral_exencion or UMBRAL_EXENCION_INSTITUCIONAL)
            and tiene_examen_final
        )

    def calcular(self):
        resultados_corte = {}
        for corte in self._cortes_parciales():
            resultados_corte[corte] = self.calcular_resultado_corte(corte)

        promedio_parciales = self._calcular_promedio_parciales(resultados_corte)
        exencion_aplica = self._exencion_aplica(promedio_parciales)
        resultado_final = self.calcular_resultado_corte(
            ComponenteEvaluacion.CORTE_FINAL,
            promedio_parciales=promedio_parciales,
            sustituir_examen=exencion_aplica,
        )
        resultados_corte[ComponenteEvaluacion.CORTE_FINAL] = resultado_final

        calificacion_final_preliminar = None
        calificacion_final_preliminar_visual = None
        resultado_preliminar = "INCOMPLETO"
        if promedio_parciales is not None and resultado_final["resultado"] is not None:
            calificacion_final_preliminar = (
                promedio_parciales * self.esquema.peso_parciales
                + resultado_final["resultado"] * self.esquema.peso_final
            ) / Decimal("100")
            calificacion_final_preliminar_visual = redondear_visualizacion_un_decimal(
                calificacion_final_preliminar
            )
            resultado_preliminar = (
                "APROBATORIO"
                if calificacion_final_preliminar >= CALIFICACION_APROBATORIA
                else "REPROBATORIO"
            )

        return {
            "inscripcion": self.inscripcion_materia,
            "esquema": self.esquema,
            "cortes": resultados_corte,
            "promedio_parciales": promedio_parciales,
            "promedio_parciales_visual": redondear_visualizacion_un_decimal(promedio_parciales),
            "exencion_aplica": exencion_aplica,
            "resultado_final": resultado_final["resultado"],
            "resultado_final_visual": resultado_final["resultado_visual"],
            "calificacion_final_preliminar": calificacion_final_preliminar,
            "calificacion_final_preliminar_visual": calificacion_final_preliminar_visual,
            "resultado_preliminar": resultado_preliminar,
        }
