import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re
from .auth import require_token, require_token_async
from decouple import config

api_gemini = config('GEMINI_KEY')  
genai.configure(api_key=api_gemini)

# Definimos el modelo a utilizar
version = 'models/gemini-2.0-flash'
model = genai.GenerativeModel(version)

def limpiar_texto(texto):
                # Eliminar comillas dobles, comillas simples y backticks
                texto_limpio = re.sub(r"[\"'`]", "", texto)
                return texto_limpio

@csrf_exempt
@require_token
def evaluar_codigo(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            descripcion_ejercicio = data.get("descripcion", "")
            codigo_estudiante = data.get("codigo", "")
            nombre_estudiante = data.get("nombre", "")
            # print(codigo_estudiante)
            
            if not codigo_estudiante or not descripcion_ejercicio:
                return JsonResponse({"error": "No se proporcionó código para evaluar."}, status=400)
            
            prompt = f"""Eres un asistente experto en JavaScript.
Tu tarea es evaluar el código de un estudiante, identificar errores y proporcionar retroalimentación amigable, directa y útil para guiarlo hacia la solución correcta.
Debes seguir estas reglas:

1. Analiza el código proporcionado y determina si cumple con los requisitos del ejercicio.
2. Presta especial atención a que la salida en consola coincida exactamente con lo que se espera según la descripción del ejercicio.
3. Si el código está incompleto, vacío o sólo contiene comentarios, considera esto un error y proporciona instrucciones claras sobre qué debe hacer para completarlo.
4. Identifica errores sintácticos, semánticos o lógicos y explica brevemente por qué ocurren.
5. Sugiere correcciones o pistas en unas pocas líneas que permitan avanzar hacia la solución correcta.
6. Habla directamente al estudiante usando “tú” o “debes…”, evitando referirte al estudiante en tercera persona.
7. Evita explicaciones adicionales, saludos o comentarios fuera de la lista de errores.
8. Usa un tono amigable y motivador.
9. Retorna una lista resumida pero sustancial

---
### Descripción del ejercicio e información del estudiante:
{descripcion_ejercicio}
---
### Código escrito por el estudiante:
{codigo_estudiante}
"""                
            print(prompt)
            response = model.generate_content(prompt)
            palabras = response.text.split()
            sumary_text = response.text
            sumary_prompt = f"""
            [Rol/Identidad]
            Eres un asistente especializado en generar textos breves y naturales para ser hablados por un sintetizador de voz (TTS) de Google.

            [Objetivo/Tarea]
            Resume el siguiente texto en una versión más corta (máximo 2 o 3 frases), pensada para ser escuchada por un estudiante. 
            El resumen debe estar escrito en segunda persona, en tono amable y claro.

            [Instrucciones específicas]
            - Solo usa texto plano (sin emojis, sin signos especiales, sin formato).
            - El resultado debe sonar natural al ser leído por voz.
            - Mantén el contenido educativo y positivo.

            [Texto original]
            {response.text}

            [Salida esperada]
            Texto corto en segunda persona, amable y natural, listo para ser reproducido por el sintetizador de voz.
            """
            if len(palabras) > 60:
                response_model = model.generate_content(sumary_prompt)
                sumary_text = response_model.text
            
            response = {
                "texto": response.text,
                "resumen": sumary_text
            }
            
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
@require_token
def free_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mensaje = data.get("mensaje", "")

            if not mensaje:
                return JsonResponse({"error": "No se proporcionó ningún mensaje."}, status=400)

            response = model.generate_content(mensaje)
            # respuesta_limpia = limpiar_texto(response.text)

            return JsonResponse({"response": response.text})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
@require_token_async
async def talking_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mensaje = data.get("message", "")
            historial = data.get("historial", [])    
            contexto = data.get("contexto","")
            talking_prompt = f"""
            [Rol/Identidad]
            Eres un tutor virtual experto en JavaScript, con una personalidad amable y didáctica. 
            Te comunicas de manera clara, concisa y cercana. Tu propósito es ayudar al estudiante a aprender programación en JavaScript.

            [Objetivo/Tarea]
            Responde a la siguiente pregunta del estudiante en un texto muy breve (máximo 2 o 3 frases). 
            Si la pregunta no tiene relación con JavaScript o programación, responde amablemente que solo puedes hablar sobre JavaScript.

            [Contexto del estudiante]
            Historial de conversación: {historial if historial else "Sin historial previo."}
            Contexto adicional: {contexto}

            [Entrada del estudiante]
            Pregunta: "{mensaje}"

            [Formato y tono deseado]
            - Usa un tono amable, cercano y motivador.
            - Redacta una respuesta natural, pensada para ser hablada por un avatar 3D.
            - No incluyas emojis ni símbolos, solo texto plano.

            [Salida esperada]
            Respuesta breve y clara sobre JavaScript o una frase cordial indicando que solo puedes hablar de JavaScript.
            """

            if not mensaje:
                return JsonResponse({"error": "No se proporcionó ningún mensaje."}, status=400)

            chat = model.start_chat(history=historial)
            response = chat.send_message(talking_prompt)            
            palabras = response.text.split()
            sumary_text = response.text
            sumary_prompt = f"""
            [Rol/Identidad]
            Eres un asistente especializado en generar textos breves y naturales para ser hablados por un sintetizador de voz (TTS) de Google.

            [Objetivo/Tarea]
            Resume el siguiente texto en una versión más corta (máximo 2 o 3 frases), pensada para ser escuchada por un estudiante. 
            El resumen debe estar escrito en segunda persona, en tono amable y claro.

            [Instrucciones específicas]
            - Solo usa texto plano (sin emojis, sin signos especiales, sin formato).
            - El resultado debe sonar natural al ser leído por voz.
            - Mantén el contenido educativo y positivo.

            [Texto original]
            {response.text}

            [Salida esperada]
            Texto corto en segunda persona, amable y natural, listo para ser reproducido por el sintetizador de voz.
            """

            if len(palabras) > 60:
                response_model = model.generate_content(sumary_prompt)
                sumary_text = response_model.text   
            
            messages = [
                {
                    "text": response.text,
                    "summary": sumary_text,                    
                    "facialExpression": "default",
                    "animation": "TalkingOne",
                }
            ]

            return JsonResponse({"messages":messages})
        except Exception as error:
            if hasattr(error, 'response') and getattr(error.response, 'status', None) == 429:
                pass
            else:            
                return JsonResponse({"error": str(error)}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)