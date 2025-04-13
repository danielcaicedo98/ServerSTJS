from gtts import gTTS
from pydub import AudioSegment

async def convert_text_to_speech(text, file_name):
    # Convertir texto a audio usando gTTS
    tts = gTTS(text, lang='es',slow=False)
    
    # Guardar como archivo MP3 temporal
    tts.save("audio_temp.mp3")
    
    # Convertir de MP3 a WAV usando pydub
    audio = AudioSegment.from_mp3("audio_temp.mp3")
    audio.export(file_name + ".wav", format="wav")   




