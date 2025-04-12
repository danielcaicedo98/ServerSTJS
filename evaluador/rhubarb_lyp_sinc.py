import subprocess
from pathlib import Path
import time

async def exec_command(command):
    """Función auxiliar que imita execCommand"""
    try:
        print(f"Ejecutando: {command}")
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando el comando: {e}")
        raise

async def get_phonemes(message):
    print("FILENAME DE GETPHONEMES:", message)
    
    try:
        start_time = time.time()
        print(f"Starting conversion for message {message}")

        # Convertir MP3 a WAV
        # await exec_command(f"ffmpeg -y -i ../audios/{message}.mp3 ../audios/{message}.wav")

        # Ejecutar Rhubarb para generar el archivo .json
        ruta_rhubarb = Path("./rhubarb_linux/rhubarb").resolve()
        await exec_command(
            f'"{ruta_rhubarb}" -f json -o ./audios/{message}.json ./audios/{message}.wav -r phonetic'
        )

        elapsed = time.time() - start_time
        print(f"Lip sync done in {int(elapsed * 1000)}ms")

    except Exception as error:
        print(f"Error while getting phonemes for message {message}:", error)
