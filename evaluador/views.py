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
            
            prompt = f"""
            [ROL]
            Eres un **tutor experto en JavaScript** con amplia experiencia enseñando a principiantes y corrigiendo código de forma pedagógica y motivadora.

            [OBJETIVO]
            Tu tarea es **evaluar el código enviado por un estudiante**, detectar errores y ofrecer **retroalimentación clara, directa y útil** que le ayude a comprender y resolver sus fallos.  

            [CONTEXTO]
            {descripcion_ejercicio}

            ### 💻 Código del estudiante:
            {codigo_estudiante}

            [Instrucciones específicas]
            1. **Evalúa el código** y determina si cumple los requisitos descritos en el ejercicio.
            2. **Verifica la salida esperada en consola**: debe coincidir exactamente con lo que se indica en la consigna.
            3. Si el código está **vacío, incompleto o solo tiene comentarios**, considéralo un error. Indica al estudiante **qué partes debe implementar o completar**.
            4. **Identifica y clasifica los errores** (sintácticos, semánticos o lógicos) explicando **por qué ocurren** de manera breve.
            5. Ofrece **pistas o correcciones concretas** en pocas líneas que lo ayuden a mejorar.
            6. **Habla directamente al estudiante** (usa “tú” o “debes…”), sin referirte a él en tercera persona.
            7. **Evita introducciones, saludos o comentarios innecesarios.**
            8. Mantén un **tono amigable, motivador y pedagógico.**
            9. Devuelve una **lista estructurada y concisa** de observaciones, asegurando que sea útil.

            [Salida esperada]
            Responde en formato de **lista numerada** con las observaciones principales.  
            Cada ítem debe incluir:
            - Descripción del error o mejora.
            - Breve explicación del motivo.
            - Sugerencia o pista para corregirlo.            
            """
            print("--------------------------------------------EVALUAR CODIGO--------------------")
            print("PROMPT :\n")
            print(prompt)

            response = model.generate_content(prompt)
            
            print("\n\nSALIDA :\n")
            print(response.text)
            print("--------------------------------------------FIN EVALUAR CODIGO--------------------")
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

            print("-------------------------OPEN CHAT----------------------------------------")
            print("PROMPT :\n")
            print(mensaje)
            response = model.generate_content(mensaje)
            # respuesta_limpia = limpiar_texto(response.text)
            print("\n\nSALIDA :\n")
            print(response.text)
            print("-------------------------FIN OPEN CHAT----------------------------------------")
            
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
            prompt = f"""
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
            print("-------------------------------CHAT INTERACTIVO-----------------------------")
            print("PROMPT :\n")
            print(prompt)
            
            if not mensaje:
                return JsonResponse({"error": "No se proporcionó ningún mensaje."}, status=400)

            chat = model.start_chat(history=historial)
            response = chat.send_message(prompt)            
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
            print("\n\nSALIDA :\n")
            print(response.text)
            print("---------------------------FIN CHAT INTERACTIVO-----------------------------------")

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