import firebase_admin
from firebase_admin import credentials, firestore, auth
from .utils import generate_verification_code, send_verification_email
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import jwt
from jwt.exceptions import InvalidTokenError
from firebase_admin import auth as firebase_auth
import hashlib

# Inicializar Firebase si no está inicializado
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("./config/firestorekey.json")
        firebase_admin.initialize_app(cred)
        
    return firestore.client()

db = initialize_firebase()

# Estructura de progreso por defecto
DEFAULT_PROGRESS = {
    "sintaxis_basica": {
        "variables": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        },
        "tipos_datos": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        },
        "operadores_aritmeticos": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        }
    },
    "estructuras_control": {
        "condicionales": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        },
        "bucles": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        },
        "control_flujo": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        }
    },
    "funciones": {
        "definicion_declaracion": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        },
        "funciones_anonimas_flecha": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        },
        "parametros_retorno": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        },
        "alcance_variables": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        },
        "recursion": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        },
        "closures": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        }
    },
    "objetos_arreglos": {
        "introduccion_objetos": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        },
        "metodos_propiedades_objetos": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        },
        "creacion_manipulacion_arreglos": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        },
        "metodos_arreglos": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        },
        "desestructuracion_objetos": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        },
        "desestructuracion_arreglos": {
            "primer_ejercicio": False,
            "segundo_ejercicio": False,
            "tercer_ejercicio": False,
            "cuarto_ejercicio": False
        }
    }
}

def create_progress_document(user_id):
    """Crea el documento de progreso si no existe"""
    progress_ref = db.collection("users").document(user_id).collection("progreso").document("progreso")
    if not progress_ref.get().exists:
        progress_ref.set(DEFAULT_PROGRESS)

from .utils import generate_verification_code, send_verification_email
from django.utils import timezone
from datetime import timedelta

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get("email")
            token_password = data.get("password")
            name = data.get("name", "")
           
            if not email or not token_password:
                return JsonResponse({"error": "Email y contraseña son requeridos"}, status=400)
            
            try:
                # password =  hashlib.sha256(token_password.encode()).hexdigest()       
                password =  token_password    
                print(password)       
            except InvalidTokenError:
                return JsonResponse({"error": "Token de contraseña inválido"}, status=400)

            user = auth.create_user(email=email, password=password, display_name=name)

            # Generar y enviar código
            code = generate_verification_code()
            send_verification_email(email, code)

            # Guardar usuario y código en Firestore (marcar como no verificado)
            user_ref = db.collection("users").document(user.uid)
            user_ref.set({
                "email": email,
                "name": name,
                "verified": False,
                "verification_code": code,
                "code_expires_at": (timezone.now() + timedelta(minutes=10)).isoformat()
            })

            create_progress_document(user.uid)

            return JsonResponse({"message": "Usuario registrado. Verifica tu email", "uid": user.uid})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
def verify_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            uid = data.get("uid")
            code = data.get("code")

            user_ref = db.collection("users").document(uid)
            user_data = user_ref.get().to_dict()

            if not user_data:
                return JsonResponse({"error": "Usuario no encontrado"}, status=404)

            if user_data.get("verified"):
                return JsonResponse({"message": "Ya verificado"}, status=200)

            if user_data["verification_code"] != code:
                return JsonResponse({"error": "Código incorrecto"}, status=400)

            # Validar expiración
            expires_at = timezone.datetime.fromisoformat(user_data["code_expires_at"])
            if timezone.now() > expires_at:
                return JsonResponse({"error": "El código ha expirado"}, status=400)

            user_ref.update({"verified": True, "verification_code": None})
            return JsonResponse({"message": "Verificación exitosa"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def login_with_google(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id_token = data.get("id_token")

            if not id_token:
                return JsonResponse({"error": "Token de Google requerido"}, status=400)

            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token["uid"]
            email = decoded_token.get("email")
            name = decoded_token.get("name", "")

            user_ref = db.collection("users").document(uid)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                user_ref.set({
                    "email": email,
                    "name": name
                })

            # Crear documento de progreso si no existe
            create_progress_document(uid)

            return JsonResponse({"message": "Inicio de sesión exitoso", "uid": uid, "email": email, "name": name})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
def update_progress(request):
    """Actualiza una parte del progreso de un usuario"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            uid = data.get("uid")
            category = data.get("category")
            subcategory = data.get("subcategory")
            status = data.get("status")

            if not uid or not category or not subcategory or status is None:
                return JsonResponse({"error": "Todos los campos son requeridos"}, status=400)

            progress_ref = db.collection("users").document(uid).collection("progreso").document("progreso")
            progress_ref.update({f"{category}.{subcategory}": status})

            return JsonResponse({"message": f"Progreso actualizado en {category} -> {subcategory}: {status}"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
def get_progress(request):
    """Obtiene el progreso de un usuario"""
    if request.method == 'GET':
        try:
            uid = request.GET.get("uid")

            if not uid:
                return JsonResponse({"error": "UID es requerido"}, status=400)

            progress_ref = db.collection("users").document(uid).collection("progreso").document("progreso")
            progress_doc = progress_ref.get()

            if not progress_doc.exists:
                return JsonResponse({"error": "Progreso no encontrado"}, status=404)

            return JsonResponse({"progress": progress_doc.to_dict()})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id_token = data.get("id_token")
            # print(id_token)

            if not id_token:
                return JsonResponse({"error": "El id_token es requerido"}, status=400)

            # Verifica el token de Firebase
            decoded_token = firebase_auth.verify_id_token(id_token)
            uid = decoded_token["uid"]
            
            
            user = firebase_auth.get_user(uid)

            user_ref = db.collection("users").document(uid)
            user_doc = user_ref.get()            
            
            user_data = user_doc.to_dict()
            verified = user_data.get("verified", False)
            print(verified)

            if not user_doc.exists:
                return JsonResponse({"error": "Usuario no registrado en la base de datos"}, status=404)
            print(user)
            return JsonResponse({
                "uid": uid,
                "email": user.email,
                "name": user.display_name,
                "verified": verified
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)



# @csrf_exempt
# def login_user(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             email = data.get("email")
#             password = data.get("password")

#             if not email or not password:
#                 return JsonResponse({"error": "Email y contraseña son requeridos"}, status=400)

#             # Autenticar usuario con Firebase
#             try:
#                 user = auth.get_user_by_email(email)
#             except firebase_admin.auth.UserNotFoundError:
#                 return JsonResponse({"error": "Usuario no encontrado"}, status=404)

#             # Simular autenticación (Firebase Admin SDK no tiene sign-in directo)
#             user_ref = db.collection("users").document(user.uid)
#             user_doc = user_ref.get()

#             if not user_doc.exists:
#                 return JsonResponse({"error": "Usuario no registrado en la base de datos"}, status=404)

#             return JsonResponse({
#                 "message": "Inicio de sesión exitoso",
#                 "uid": user.uid,
#                 "email": user.email,
#                 "name": user.display_name                
#                 })
        
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)
    
#     return JsonResponse({"error": "Método no permitido"}, status=405)
