import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re

# Configurar la API de Google Generative AI
genai.configure(api_key='AIzaSyBHjc9tKEPxVUIlqmH2LJsK-MjJRFcQIzI')

# Definir el modelo a utilizar
version = 'models/gemini-1.5-flash'
model = genai.GenerativeModel(version)

def limpiar_texto(texto):
                # Eliminar comillas dobles, comillas simples y backticks
                texto_limpio = re.sub(r"[\"'`]", "", texto)
                return texto_limpio

@csrf_exempt
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
                4. **Explicar claramente en unas pocas líneas cuál es el error del estudiante**  
                5. **La salida debe ser solamente una lista donde un elemento de la lista corresponda a un error, si hay 2 errores, entonces dos elementos, si hay tres errores entonces tres elementos de la lista**  
                6. **La salida debe hablarle directamente al estudiante, el cual se llama {nombre_estudiante}**  
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
