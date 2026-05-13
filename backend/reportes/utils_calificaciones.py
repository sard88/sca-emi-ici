from decimal import Decimal, ROUND_HALF_UP


NUMEROS_LETRA = {
    0: "CERO",
    1: "UNO",
    2: "DOS",
    3: "TRES",
    4: "CUATRO",
    5: "CINCO",
    6: "SEIS",
    7: "SIETE",
    8: "OCHO",
    9: "NUEVE",
    10: "DIEZ",
}


def redondear_un_decimal(valor):
    if valor is None:
        return None
    return Decimal(valor).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def calificacion_numerica_con_letra(valor):
    redondeada = redondear_un_decimal(valor)
    if redondeada is None:
        return ""
    entero = int(redondeada)
    decimal = int((redondeada - Decimal(entero)) * Decimal("10"))
    letra = f"{NUMEROS_LETRA.get(entero, str(entero))} PUNTO {NUMEROS_LETRA.get(decimal, str(decimal))}"
    return f"{redondeada:.1f} ({letra})"
