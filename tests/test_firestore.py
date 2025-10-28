import json
import jwt
from unittest.mock import patch, MagicMock
from django.test import Client, TestCase
from django.utils import timezone
from decouple import config
from serverstjs import firestore as fs


# ==============================
# CONFIGURACIÓN GLOBAL
# ==============================

SECRET_KEY = config("SECRET_KEY", default="testsecret")


def get_headers():
    """Genera encabezado Bearer con JWT válido para endpoints protegidos."""
    token = jwt.encode(
        {"uid": "test123", "email": "test@example.com"},
        SECRET_KEY,
        algorithm="HS256",
    )
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


# ==============================
# 🔹 TESTS UNITARIOS DE FIRESTORE CORE
# ==============================

class TestFirestoreCore(TestCase):
    """Pruebas unitarias para funciones base en firestore.py"""

    def setUp(self):
        self.client = Client()
        self.token = jwt.encode(
            {"email": "test@example.com"},
            SECRET_KEY,
            algorithm="HS256"
        )
        self.headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        self.url_update_user = "/actualizar_usuario/"

    # ---- generate_jwt ----
    def test_generate_jwt_crea_token_valido(self):
        token = fs.generate_jwt("uid123", "test@example.com")
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        self.assertEqual(decoded["uid"], "uid123")
        self.assertEqual(decoded["email"], "test@example.com")
        self.assertIn("exp", decoded)

    # ---- initialize_firebase ----
    @patch("serverstjs.firestore.firebase_admin")
    @patch("serverstjs.firestore.firestore")
    def test_initialize_firebase_si_no_inicializado(self, mock_firestore, mock_firebase_admin):
        mock_firebase_admin._apps = []
        fs.initialize_firebase()
        mock_firebase_admin.initialize_app.assert_called_once()
        mock_firestore.client.assert_called_once()

    @patch("serverstjs.firestore.firebase_admin")
    @patch("serverstjs.firestore.firestore")
    def test_initialize_firebase_ya_inicializado(self, mock_firestore, mock_firebase_admin):
        mock_firebase_admin._apps = ["app"]
        fs.initialize_firebase()
        mock_firebase_admin.initialize_app.assert_not_called()
        mock_firestore.client.assert_called_once()

    # ---- create_progress_document ----
    @patch("serverstjs.firestore.db")
    def test_create_progress_document_crea_documentos_si_no_existen(self, mock_db):
        mock_progress_doc = MagicMock()
        mock_progress_doc.get.return_value.exists = False
        mock_navigation_doc = MagicMock()
        mock_navigation_doc.get.return_value.exists = False
        mock_user_doc = MagicMock()
        mock_user_doc.collection.side_effect = lambda name: {
            "progreso": MagicMock(document=lambda _: mock_progress_doc),
            "navigation": MagicMock(document=lambda _: mock_navigation_doc),
        }[name]
        mock_db.collection.return_value.document.return_value = mock_user_doc
        fs.create_progress_document("uid123")
        mock_progress_doc.set.assert_called_once_with(fs.DEFAULT_PROGRESS)
        mock_navigation_doc.set.assert_called_once_with(fs.DEFAULT_NAVIGATION)

    # ---- update_user ----
    @patch("serverstjs.firestore.db")
    def test_update_user_exitoso(self, mock_db):
        mock_user_ref = MagicMock()
        mock_user_ref.get.return_value.exists = True
        mock_db.collection.return_value.document.return_value = mock_user_ref
        data = {"uid": "uid123", "updates": {"nombre": "Daniel"}}
        response = self.client.post(
            self.url_update_user,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Usuario actualizado", response.json()["message"])

    @patch("serverstjs.firestore.db")
    def test_update_user_sin_uid(self, mock_db):
        data = {"updates": {"nombre": "Daniel"}}
        response = self.client.post(
            self.url_update_user,
            json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 400)

    @patch("serverstjs.firestore.db")
    def test_update_user_usuario_no_encontrado(self, mock_db):
        mock_user_ref = MagicMock()
        mock_user_ref.get.return_value.exists = False
        mock_db.collection.return_value.document.return_value = mock_user_ref
        data = {"uid": "uid123", "updates": {"nombre": "Daniel"}}
        response = self.client.post(
            self.url_update_user,
            json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 404)

    @patch("serverstjs.firestore.db")
    def test_update_user_metodo_no_permitido(self, mock_db):
        response = self.client.get(self.url_update_user, **self.headers)
        self.assertEqual(response.status_code, 405)


# ==============================
# 🔹 TESTS DE ENDPOINTS PÚBLICOS (registro, login, verificación)
# ==============================

class TestAuthEndpoints(TestCase):

    @patch("serverstjs.firestore.auth.create_user")
    @patch("serverstjs.firestore.send_verification_email")
    @patch("serverstjs.firestore.db")
    def test_register_user_exitoso(self, mock_db, mock_send, mock_create_user):
        mock_create_user.return_value = MagicMock(uid="user123")
        mock_user_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_user_ref
        client = Client()
        response = client.post(
            "/registro/",
            json.dumps({"email": "test@example.com", "password": "123456", "name": "Tester"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Usuario registrado", response.json()["message"])
    

# ==============================
# 🔹 TESTS DE PROGRESO Y LENGUAJE
# ==============================

class TestProgressLanguage(TestCase):

    @patch("serverstjs.firestore.db")
    def test_update_progress_exitoso(self, mock_db):
        mock_progress_ref = MagicMock()
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_progress_ref
        client = Client()
        response = client.post(
            "/update_progress/",
            json.dumps({
                "uid": "user123",
                "category": "sintaxis_basica",
                "subcategory": "variables.primer_ejercicio",
                "status": True,
            }),
            content_type="application/json",
            **get_headers()
        )
        self.assertEqual(response.status_code, 200)

    @patch("serverstjs.firestore.db")
    def test_check_language_tiene(self, mock_db):
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {"lenguaje_programacion": "JavaScript"}
        mock_user_ref = MagicMock(get=MagicMock(return_value=mock_user_doc))
        mock_db.collection.return_value.document.return_value = mock_user_ref
        client = Client()
        response = client.get("/verificar_lenguaje/?uid=user123", **get_headers())
        self.assertEqual(response.status_code, 200)


# ==============================
# 🔹 TESTS DE NAVEGACIÓN
# ==============================

class TestNavigation(TestCase):

    @patch("serverstjs.firestore.db")
    def test_update_navigation_exitoso(self, mock_db):
        mock_nav_ref = MagicMock()
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_nav_ref
        client = Client()
        response = client.post(
            "/update_navigation/",
            json.dumps({"uid": "user123", "category": "funciones", "subcategory": "parametros", "index": 1}),
            content_type="application/json",
            **get_headers()
        )
        self.assertEqual(response.status_code, 200)

    @patch("serverstjs.firestore.db")
    def test_get_user_navigation_exitoso(self, mock_db):
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"category": "funciones", "subcategory": "parametros", "index": 2}
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = mock_doc
        client = Client()
        response = client.get("/get_user_navigation/?uid=user123", **get_headers())
        self.assertEqual(response.status_code, 200)


# ==============================
# 🔹 TESTS DE EJERCICIOS
# ==============================

class TestExercises(TestCase):

    @patch("serverstjs.firestore.db")
    def test_capture_user_exercises_exitoso(self, mock_db):
        mock_user_ref = MagicMock()
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_ref.get.return_value = mock_user_doc
        mock_db.collection.return_value.document.return_value = mock_user_ref
        client = Client()
        response = client.post(
            "/capture_user_exercises/",
            json.dumps({"uid": "user123", "datos_ejercicios": {"var1": {"intentos": 3}}}),
            content_type="application/json",
            **get_headers()
        )
        self.assertEqual(response.status_code, 200)

    @patch("serverstjs.firestore.db")
    def test_get_user_exercises_exitoso(self, mock_db):
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"datos_ejercicios": {"var1": {"intentos": 3}}}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        client = Client()
        response = client.get("/get_user_exercises/?uid=user123", **get_headers())
        self.assertEqual(response.status_code, 200)


# ==============================
# 🔹 TESTS DE PERFIL DE ESTUDIANTE
# ==============================

class TestStudentProfile(TestCase):

    @patch("serverstjs.firestore.db")
    def test_update_student_profile_exitoso(self, mock_db):
        mock_user_ref = MagicMock()
        mock_user_ref.get.return_value.exists = True
        mock_db.collection.return_value.document.return_value = mock_user_ref
        client = Client()
        response = client.post(
            "/update_student_profile/",
            json.dumps({"uid": "user123", "perfil_texto": "Aprendo JS"}),
            content_type="application/json",
            **get_headers()
        )
        self.assertEqual(response.status_code, 200)

    @patch("serverstjs.firestore.db")
    def test_get_student_profile_exitoso(self, mock_db):
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"perfil_texto": "Soy estudiante de JS"}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        client = Client()
        response = client.get("/get_student_profile/?uid=user123", **get_headers())
        self.assertEqual(response.status_code, 200)
