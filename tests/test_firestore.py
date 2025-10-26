import json
import jwt
import pytest
from unittest.mock import patch, MagicMock
from django.test import Client, TestCase
from decouple import config
from django.utils import timezone
from datetime import timedelta

# Importamos los objetos del módulo
from serverstjs import firestore as fs

SECRET_KEY = config("SECRET_KEY")


class FirestoreTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.token = jwt.encode(
            {"email": "test@example.com"},
            SECRET_KEY,
            algorithm="HS256"
        )
        self.headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        self.url_update_user = "/update_user/"

    # ---------- TEST generate_jwt ----------
    def test_generate_jwt_crea_token_valido(self):
        token = fs.generate_jwt("uid123", "test@example.com")
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        self.assertEqual(decoded["uid"], "uid123")
        self.assertEqual(decoded["email"], "test@example.com")
        self.assertIn("exp", decoded)

    # ---------- TEST initialize_firebase ----------
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

    # ---------- TEST create_progress_document ----------
    @patch("serverstjs.firestore.db")
    def test_create_progress_document_crea_documentos_si_no_existen(self, mock_db):
        mock_progress_doc = MagicMock()
        mock_progress_doc.get.return_value.exists = False

        mock_navigation_doc = MagicMock()
        mock_navigation_doc.get.return_value.exists = False

        mock_user_doc = MagicMock()
        mock_user_doc.collection.side_effect = lambda name: {
            "progreso": MagicMock(document=lambda _: mock_progress_doc),
            "navigation": MagicMock(document=lambda _: mock_navigation_doc)
        }[name]

        mock_db.collection.return_value.document.return_value = mock_user_doc

        fs.create_progress_document("uid123")

        mock_progress_doc.set.assert_called_once_with(fs.DEFAULT_PROGRESS)
        mock_navigation_doc.set.assert_called_once_with(fs.DEFAULT_NAVIGATION)

    # ---------- TEST update_user ----------
    @patch("serverstjs.firestore.db")
    def test_update_user_exitoso(self, mock_db):
        mock_user_ref = MagicMock()
        mock_user_ref.get.return_value.exists = True
        mock_db.collection.return_value.document.return_value = mock_user_ref

        data = {
            "uid": "uid123",
            "updates": {"nombre": "Daniel"}
        }

        response = self.client.post(
            self.url_update_user,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Usuario actualizado correctamente", response.json()["message"])
        mock_user_ref.update.assert_called_once_with({"nombre": "Daniel"})

    @patch("serverstjs.firestore.db")
    def test_update_user_sin_uid(self, mock_db):
        data = {"updates": {"nombre": "Daniel"}}
        response = self.client.post(
            self.url_update_user,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("UID", response.json()["error"])

    @patch("serverstjs.firestore.db")
    def test_update_user_sin_updates(self, mock_db):
        data = {"uid": "uid123"}
        response = self.client.post(
            self.url_update_user,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("actualizar", response.json()["error"])

    @patch("serverstjs.firestore.db")
    def test_update_user_usuario_no_encontrado(self, mock_db):
        mock_user_ref = MagicMock()
        mock_user_ref.get.return_value.exists = False
        mock_db.collection.return_value.document.return_value = mock_user_ref

        data = {"uid": "uid123", "updates": {"nombre": "Daniel"}}
        response = self.client.post(
            self.url_update_user,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("Usuario no encontrado", response.json()["error"])

    @patch("serverstjs.firestore.db")
    def test_update_user_metodo_get(self, mock_db):
        response = self.client.get(self.url_update_user, **self.headers)
        self.assertEqual(response.status_code, 405)

    @patch("serverstjs.firestore.db")
    def test_update_user_excepcion(self, mock_db):
        mock_db.collection.side_effect = Exception("Error interno Firestore")

        data = {"uid": "uid123", "updates": {"nombre": "Daniel"}}
        response = self.client.post(
            self.url_update_user,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Error interno", response.json()["error"])
