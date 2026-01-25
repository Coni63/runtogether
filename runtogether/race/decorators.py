from django.http import JsonResponse
from functools import wraps
from django.conf import settings


def api_key_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # On récupère la clé dans le header
        api_key = request.headers.get("X-API-KEY")

        # On compare avec une clé stockée en DB ou en ENV
        if api_key != settings.X_API_KEY:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view
