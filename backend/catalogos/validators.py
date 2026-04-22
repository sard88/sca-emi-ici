from django.core.validators import RegexValidator

CLAVE_MAX_LENGTH = 20
CLAVE_REGEX = r"^[A-Za-z0-9_-]+$"
CLAVE_FORMAT_MESSAGE = (
    "Solo se permiten letras, numeros, guion medio (-) y guion bajo (_)."
)

clave_format_validator = RegexValidator(
    regex=CLAVE_REGEX,
    message=CLAVE_FORMAT_MESSAGE,
    code="invalid_clave_format",
)
