import json
import base64
import os

async def read_json_transcript(file_name):
    print("📄 Leyendo JSON desde:", file_name)
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = f.read()
        return json.loads(data)
    except FileNotFoundError:
        print(f"❌ Error: El archivo '{file_name}' no fue encontrado.")
    except PermissionError:
        print(f"❌ Error: No se tienen permisos para leer el archivo '{file_name}'.")
    except json.JSONDecodeError as e:
        print(f"❌ Error: El archivo '{file_name}' no contiene un JSON válido.")
        print(f"📍 Detalle: {e}")
    except Exception as e:
        print(f"❌ Error inesperado al leer JSON desde '{file_name}': {e}")


async def audio_file_to_base64(file_name):
    print("🔊 Codificando audio a base64 desde:", file_name)
    try:
        with open(file_name, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode('utf-8')
    except FileNotFoundError:
        print(f"❌ Error: El archivo de audio '{file_name}' no fue encontrado.")
    except PermissionError:
        print(f"❌ Error: No se tienen permisos para acceder al archivo '{file_name}'.")
    except Exception as e:
        print(f"❌ Error inesperado al codificar el archivo de audio '{file_name}': {e}")
