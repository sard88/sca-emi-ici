from django.conf import settings
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers


class ExplicitCorsMiddleware:
    """CORS mínimo y explícito para el portal Next.js en desarrollo/intranet."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin")
        if request.method == "OPTIONS" and self._origin_allowed(origin):
            response = HttpResponse(status=204)
        else:
            response = self.get_response(request)

        if self._origin_allowed(origin):
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = (
                "Content-Type, X-CSRFToken, X-Requested-With"
            )
            response["Access-Control-Expose-Headers"] = (
                "Content-Disposition, X-Registro-Exportacion-Id"
            )
            patch_vary_headers(response, ("Origin",))

        return response

    @staticmethod
    def _origin_allowed(origin):
        return bool(origin and origin in getattr(settings, "CORS_ALLOWED_ORIGINS", ()))
