import pyttsx3
from pathlib import Path

async def convert_text_to_speech(text, file_name):
    file_path = Path(file_name).resolve()
    print("FILENAME DE CONVERTTEXT:", file_path)
    """ RATE"""
       # setting up new voice rate

    engine = pyttsx3.init()
    rate = engine.getProperty('rate')   # getting details of current speaking rate
    print (rate)                        #printing current voice rate
    engine.setProperty('rate', 150)  
    voices = engine.getProperty('voices')
    print(voices)
    engine.setProperty('voice', voices[0].id)
    # Guardar el archivo (formato .mp3 no soportado, solo .wav)
    engine.save_to_file(text, str(file_path.with_suffix(".wav")))
    engine.runAndWait()

    print(f"Texto convertido a voz y guardado en: {file_path.with_suffix('.wav')}")
