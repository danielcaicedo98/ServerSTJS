from locust import HttpUser, task, between
import json

class ApiUser(HttpUser):
    wait_time = between(1, 3)
    host = "https://api.smarttutorjs.shop"  # tu servidor desplegado

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJ5VncwdndCeGY2Y0VNYUZvZzFCQ0xIeEJrRnExIiwiZW1haWwiOiJkYW5pZWxjYWljZWRvODk5MUBnbWFpbC5jb20iLCJleHAiOjE3NjA5Mzg4OTUuNTE3MjExfQ.1FEaFBi1msn3fHXUinn5XeBLgjdi1M6ZFc6ir_Z6iko"

    @task
    def evaluar_codigo(self):
        payload = {
            "descripcion": "Escribe una función que sume dos números y retorne el resultado",
            "codigo": "function suma(a, b) { return a + b; }",
            "nombre": "Juan"
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        # Ruta relativa al host (no pongas el dominio aquí)
        self.client.post("/evaluar_codigo/", data=json.dumps(payload), headers=headers)
