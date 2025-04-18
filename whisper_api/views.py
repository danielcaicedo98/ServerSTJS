from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
import whisper
import tempfile

class TranscribeAudio(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        audio_file = request.FILES['audio']
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            for chunk in audio_file.chunks():
                temp_audio.write(chunk)
            temp_audio_path = temp_audio.name

        model = whisper.load_model("base")
        result = model.transcribe(temp_audio_path)
        return Response({'text': result['text']})
