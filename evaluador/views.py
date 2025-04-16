import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re
import uuid
import asyncio
from .text_to_speech import convert_text_to_speech
from .rhubarb_lyp_sinc import get_phonemes
from .files import audio_file_to_base64, read_json_transcript
from .auth import require_token, require_token_async
from decouple import config

api_gemini = config('GEMINI_KEY')  
genai.configure(api_key=api_gemini)

# Definir el modelo a utilizar
version = 'models/gemini-1.5-flash'
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
            
            prompt = f"""Eres un asistente de programación experto en JavaScript.
                Tu tarea es evaluar el código de un estudiante, identificar errores y proporcionar retroalimentación detallada.  
                Debes seguir estas reglas:  
                1. **Analizar el código** proporcionado y determinar si cumple con los requisitos del ejercicio.  
                2. **Identificar errores sintácticos, semánticos o lógicos**, explicando por qué ocurren y cómo corregirlos.  
                3. **La corrección debe ser unas cuantas líneas**  
                4. **Explicarle al estudiante claramente en unas pocas líneas cuál es el error**  
                5. **La salida debe ser solamente una lista donde un elemento de la lista corresponda a un error, si hay 2 errores, entonces dos elementos, si hay tres errores entonces tres elementos de la lista**  
                6. **usa un tono amigable para el estudiante**  
                7. **Cada elemento de la lista debe iniciar con ** y terminar en un salto de línea**                 
                8. **Evita explicaciones adicionales**                
                ---  
                ### **Ejercicio a Evaluar**  
                **Descripción:**  
                {descripcion_ejercicio}  
                ---  
                ### **Código del Estudiante**  
                ```javascript  
                {codigo_estudiante}  
                ```"""
            response = model.generate_content(prompt)
            formated_text = limpiar_texto(response.text)
            
            # print(response.text)
            return JsonResponse({"respuesta": formated_text})
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
            respuesta_limpia = limpiar_texto(response.text)

            return JsonResponse({"respuesta": respuesta_limpia})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
@require_token
def free_conversation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mensaje = data.get("message", "")
            historial = data.get("historial", [])  # <- Lista de mensajes previos opcional           

            if not mensaje:
                return JsonResponse({"error": "No se proporcionó ningún mensaje."}, status=400)

            chat = model.start_chat(history=historial)
            response = chat.send_message("En un texto muy corto, en un tono amabla, de unas pocas líneas y que el texto pueda ser leído por un sistetizador respondeme lo siguiente: " + mensaje + ".")            

            return JsonResponse({
                "respuesta": response.text                
            })

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
            historial = data.get("historial", [])  # <- Lista de mensajes previos opcional    
            if not mensaje:
                return JsonResponse({"error": "No se proporcionó ningún mensaje."}, status=400)

            chat = model.start_chat(history=historial)
            response = chat.send_message("En un texto muy corto, en un tono amabla, de unas pocas líneas,ten muy en cuenta que el texto va a ser leído por un sistetizador respondeme lo siguiente: " + mensaje + ".")            
            respuesta_limpia = limpiar_texto(response.text)

            unique_id = str(uuid.uuid4())
            file_name = f"mensaje-{unique_id}"
            audio_file_name = f"./audios/{file_name}"  
            
            # await convert_text_to_speech(text=respuesta_limpia, file_name=audio_file_name)
            # await get_phonemes(file_name)
            audio = await audio_file_to_base64(f"audios/default_audio.wav")
            # lypsinc = await read_json_transcript(f"audios/{file_name}.json")
            lypsinc = await read_json_transcript('audios/default_visemas.json')
            
            
            messages = [
                {
                    "text": respuesta_limpia,
                    "audio": audio,
                    "lipsync": lypsinc,
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

@csrf_exempt
@require_token_async
async def talking_chat_complete(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mensaje = data.get("message", "")
            historial = data.get("historial", [])  # <- Lista de mensajes previos opcional    
            if not mensaje:
                return JsonResponse({"error": "No se proporcionó ningún mensaje."}, status=400)

            chat = model.start_chat(history=historial)
            # response = chat.send_message("En un texto muy corto, en un tono amabla, de unas pocas líneas,ten muy en cuenta que el texto va a ser leído por un sistetizador respondeme lo siguiente: " + mensaje + ".")            
            response = chat.send_message(mensaje)
            respuesta_limpia = limpiar_texto(response.text)

            unique_id = str(uuid.uuid4())
            file_name = f"mensaje-{unique_id}"
            audio_file_name = f"./audios/{file_name}"  
            
            await convert_text_to_speech(text=respuesta_limpia, file_name=audio_file_name)
            await get_phonemes(file_name)
            audio = await audio_file_to_base64(f"audios/{file_name}.wav")
            lypsinc = await read_json_transcript(f"audios/{file_name}.json")            
            
            messages = [
                {
                    "text": respuesta_limpia,
                    "audio": audio,
                    "lipsync": lypsinc,
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