import requests
import os

class STSService:
    """Handles interaction with the Speech-to-Speech service."""
    
    def __init__(self, token):
        self.token = token
        self.url = 'http://10.21.3.9:5001/v1/speech-to-speech'

    def synthesize_speech(self, filename, src_language, tgt_language, gender):
        """Synthesizes speech from text and plays it or saves to a file."""
        headers = {'Authorization': f'Bearer {self.token}'}
        files = {'file': open(filename, 'rb')}
        data = {
            'src_language': src_language,
            'tgt_language': tgt_language,
            'gender': gender,
        }

        response = requests.post(self.url, headers=headers, files=files, data=data)
        if response.status_code == 200:
            output_filename = filename.replace('audio', 'generated_output_audio').replace('.wav', '_tts.wav')
            os.makedirs(os.path.dirname(output_filename), exist_ok=True)
            with open(output_filename, 'wb') as f:
                f.write(response.content)

            # Play the synthesized audio via the output stream
            # output_stream.write(response.content)
            print(f"TTS output saved and played: {output_filename}")
            return response.content
        else:
            raise Exception(f"Error in TTS service: {response.status_code}, {response.text}")
