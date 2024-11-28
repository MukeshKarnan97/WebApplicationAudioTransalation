import requests

class ASRService:
    """Handles interaction with the Automatic Speech Recognition service."""

    def __init__(self):
        self.url = 'https://asr.iitm.ac.in/internal/asr/decode'

    def transcribe_audio(self, filename):
        """Transcribes audio file using the ASR service."""

        print(filename)
        files = {
            'file': open(filename, 'rb'),
            'language': (None, 'english'),
            'vtt': (None, 'false'),
        }
        response = requests.post(self.url, files=files)
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get('status') == 'success':
                return response_json['transcript']