# auth.py (puede estar en la misma carpeta que views.py)
import jwt
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from functools import wraps
from decouple import config

SECRET_KEY = config('SECRET_KEY')  

def require_token(view_func):
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Token de autorización no proporcionado o inválido."}, status=401)

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_info = payload  # Puedes acceder luego a request.user_info["email"], por ejemplo
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "El token ha expirado."}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Token inválido."}, status=401)

        return view_func(request, *args, **kwargs)
    return _wrapped_view


def require_token_async(view_func):
    @wraps(view_func)
    async def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Token no proporcionado"}, status=401)
        
        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_info = payload  # puedes acceder a esto dentro de la vista
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token expirado"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Token inválido"}, status=401)

        # 👇 aquí hacemos await correctamente
        return await view_func(request, *args, **kwargs)

    return _wrapped_view