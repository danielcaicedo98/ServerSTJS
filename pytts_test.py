import pyttsx3

# Inicializa el motor
engine = pyttsx3.init()

# Texto a convertir
texto = "Hola, esto es una prueba de conversión de texto a voz con pyttsx3. Hola, esto es una prueba de conversión de texto a voz con pyttsx3Hola, esto es una prueba de conversión de texto a voz con pyttsx3Hola, esto es una prueba de conversión de texto a voz con pyttsx3Hola, esto es una prueba de conversión de texto a voz con pyttsx3Hola, esto es una prueba de conversión de texto a voz con pyttsx3Hola, esto es una prueba de conversión de texto a voz con pyttsx3Hola, esto es una prueba de conversión de texto a voz con pyttsx3Hola, esto es una prueba de conversión de texto a voz con pyttsx3"

# Opciones (velocidad, volumen, voz)
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
voces = engine.getProperty('voices')
engine.setProperty('voice', voces[0].id)

# Guardar a archivo (formato WAV)
engine.save_to_file(texto, 'salida.wav')

# Ejecutar el guardado
engine.runAndWait()

print("✅ Audio guardado como 'salida.wav'")
