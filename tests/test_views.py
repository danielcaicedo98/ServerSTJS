import jwt
import json
from django.test import AsyncClient, Client, TestCase
from decouple import config
from unittest.mock import patch, MagicMock

SECRET_KEY = config("SECRET_KEY")


class EndpointTests(TestCase):
    """Pruebas para los endpoints evaluar_codigo, free_chat y talking_chat"""

    def setUp(self):
        # Cliente síncrono
        self.client = Client()
        # Cliente asíncrono (para talking_chat)
        self.async_client = AsyncClient()

        # Token JWT válido
        self.token = jwt.encode({"email": "test@example.com"}, SECRET_KEY, algorithm="HS256")
        self.headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        # Rutas (ajústalas según tu urls.py)
        self.url_evaluar = "/evaluar_codigo/"
        self.url_freechat = "/free_chat/"
        self.url_talkingchat = "/talking_chat/"

    # ---------- TESTS EVALUAR_CODIGO ----------
    @patch("google.generativeai.GenerativeModel.generate_content")
    def test_evaluar_codigo_ok(self, mock_gemini):
        mock_gemini.return_value.text = "1. El código cumple correctamente."
        data = {
            "descripcion": "Crear una función que sume dos números.",
            "codigo": "function sumar(a,b){return a+b;}",
            "nombre": "Juan"
        }
        response = self.client.post(
            self.url_evaluar,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("texto", response.json())

    def test_evaluar_codigo_sin_token(self):
        data = {"descripcion": "Ejercicio", "codigo": "print('hola')"}
        response = self.client.post(
            self.url_evaluar,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    @patch("google.generativeai.GenerativeModel.generate_content")
    def test_evaluar_codigo_faltan_datos(self, mock_gemini):
        data = {"codigo": ""}
        response = self.client.post(
            self.url_evaluar,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_evaluar_codigo_metodo_get(self):
        response = self.client.get(self.url_evaluar, **self.headers)
        self.assertEqual(response.status_code, 405)

    # ---------- TESTS FREE_CHAT ----------
    @patch("google.generativeai.GenerativeModel.generate_content")
    def test_free_chat_ok(self, mock_gemini):
        mock_gemini.return_value.text = "Hola, ¿cómo puedo ayudarte?"
        data = {"mensaje": "Hola"}
        response = self.client.post(
            self.url_freechat,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())

    def test_free_chat_sin_token(self):
        data = {"mensaje": "Hola"}
        response = self.client.post(
            self.url_freechat,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    @patch("google.generativeai.GenerativeModel.generate_content")
    def test_free_chat_sin_mensaje(self, mock_gemini):
        data = {"mensaje": ""}
        response = self.client.post(
            self.url_freechat,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 400)

    def test_free_chat_metodo_get(self):
        response = self.client.get(self.url_freechat, **self.headers)
        self.assertEqual(response.status_code, 405)

    # ---------- TESTS TALKING_CHAT (asíncrono) ----------
    # ---------- TESTS TALKING_CHAT (asíncrono) ----------
    @patch("google.generativeai.GenerativeModel.start_chat")
    async def test_talking_chat_ok(self, mock_start_chat):
        mock_chat_instance = MagicMock()
        mock_chat_instance.send_message.return_value.text = (
            "Claro, en JavaScript puedes usar let para declarar variables."
        )
        mock_start_chat.return_value = mock_chat_instance

        data = {
            "message": "¿Qué es let en JavaScript?",
            "historial": [],
            "contexto": "Variables"
        }

        response = await self.async_client.post(
            self.url_talkingchat,
            data=json.dumps(data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.token}"},  # ✅ CAMBIO
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("messages", response.json())

    async def test_talking_chat_sin_token(self):
        data = {"message": "Hola"}
        response = await self.async_client.post(
            self.url_talkingchat,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    @patch("google.generativeai.GenerativeModel.start_chat")
    async def test_talking_chat_sin_mensaje(self, mock_start_chat):
        data = {"message": ""}
        response = await self.async_client.post(
            self.url_talkingchat,
            data=json.dumps(data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.token}"},  # ✅ CAMBIO
        )
        self.assertEqual(response.status_code, 400)

    async def test_talking_chat_metodo_get(self):
        response = await self.async_client.get(
            self.url_talkingchat,
            headers={"Authorization": f"Bearer {self.token}"}  # ✅ CAMBIO
        )
        self.assertEqual(response.status_code, 405)

