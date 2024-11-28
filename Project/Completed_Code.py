import os
import subprocess
import requests
import zipfile
import pyaudio
import wave
import time
import numpy as np
import threading



def obtain_auth_token():
    """Obtains an authentication token from the specified API."""
    global token  # Declare that we are using the global token variable
    api_url = "http://10.21.3.9:5001/v1/auth/Token/"
    api_key = '5678'
    headers = {'x-api-key': api_key}
    response = requests.get(api_url, headers=headers)
    print(response.json().get('token'))
    
    if response.status_code == 200:
        # Extract the token from the response JSON
        token = response.json().get('token')
        if token:
            return token
        else:
            raise Exception("Token not found in response")
    else:
        raise Exception(f"Failed to obtain token: {response.status_code}, {response.text}")


class VBCableInstaller:
    def __init__(self, driver_path="C:\Program Files\VB\CABLE", download_url="https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack45.zip", installer_zip="VBCABLE_Driver_Pack43.zip", extracted_path="VBCABLE_Installer"):
        self.driver_path = driver_path
        self.download_url = download_url
        self.installer_zip = installer_zip
        self.extracted_path = extracted_path

    def is_vb_cable_installed(self):
        """Check if the VB-Cable driver is installed by verifying the driver path."""
        return os.path.exists(self.driver_path)

    def download_vb_cable_installer(self):
        """Download the VB-Cable installer from the specified URL."""
        print("Starting download of VB-Cable installer...")
        response = requests.get(self.download_url, stream=True)
        if response.status_code == 200:
            with open(self.installer_zip, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):    
                    file.write(chunk)
            print(f"Downloaded VB-Cable installer to {self.installer_zip}")
            return self.installer_zip
        else:
            print(f"Failed to download VB-Cable installer. Status code: {response.status_code}")
            return None

    def install_vb_cable(self, installer_path):
        """Install VB-Cable by extracting and running the installer."""
        print(f"Extracting installer from {installer_path}...")
        with zipfile.ZipFile(installer_path, "r") as zip_ref:
            zip_ref.extractall(self.extracted_path)
        print(f"Extracted installer to {self.extracted_path}")
        
        installer_exec_path = os.path.join(self.extracted_path, "VBCABLE_Setup_x64.exe")  # Ensure this is the correct executable name
        try:
            subprocess.run(["start", "/wait", installer_exec_path], shell=True, check=True)
            print("VB-Cable installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Installation failed: {e}")

    def install(self):
        """Check if VB-Cable is installed, if not, download and install it."""
        if self.is_vb_cable_installed():
            print("VB-Cable is already installed. No need to download or install.")
        else:
            print("VB-Cable is not installed. Downloading and installing...")
            installer_path = self.download_vb_cable_installer()
            if installer_path:
                self.install_vb_cable(installer_path)






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
        #     else:
        #         raise Exception(f"Error in transcription: {response_json.get('reason')}")
        # else:
        #     raise Exception(f"Error in ASR service: {response.status_code}")


class STSService:
    """Handles interaction with the Text-to-Speech service."""

    def __init__(self, token):
        self.token = token
        self.url = 'http://10.21.3.9:5001/v1/speech-to-speech'
        

    def synthesize_speech(self, filename, src_language, tgt_language, gender, output_stream):
        """Synthesizes speech from text and saves it to a file."""
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

            # output_stream.write(response.content)

            print(f"TTS output saved to {output_filename}.")
            return response.content
        # else:
        #     raise Exception(f"Error in TTS service: {response.status_code}")





class AudioProcessor:
    """Handles capturing and processing audio input and output."""

    def __init__(self, input_device_name=None, output_device_name=None, format=pyaudio.paInt16, channels=1, rate=22050, chunk=1024, duration=5):
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.duration = duration

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()

        # Find the input and output devices by name
        self.input_device_index = self.get_device_index_by_name(input_device_name, is_input=True)
        self.output_device_index = self.get_device_index_by_name(output_device_name, is_input=False)

        print(f"Devices {self.input_device_index}  and  {self.output_device_index}")

        # Open input and output streams
        self.input_stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
            input_device_index=self.input_device_index
        )

        self.output_stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk,
            output_device_index=self.output_device_index
        )

        print(f"self {self.input_device_index}  and {self.output_stream} ")


    def get_device_index_by_name(self, device_name, is_input=True):
        """Returns the device index that matches the given name."""
        device_count = self.p.get_device_count()
        for i in range(device_count):
            device_info = self.p.get_device_info_by_index(i)
            if (is_input and device_info['maxInputChannels'] > 0) or (not is_input and device_info['maxOutputChannels'] > 0):
                if device_name and device_name.lower() in device_info['name'].lower():
                    return i
        return self.p.get_default_input_device_info()["index"] if is_input else self.p.get_default_output_device_info()["index"]


    def capture_chunk(self):
        """Records audio for the specified duration."""
        
        duration = self.duration

        frames = []
        start_time = time.time()

        while time.time() - start_time < duration:
            input_data = self.input_stream.read(self.chunk, exception_on_overflow=False)
            frames.append(input_data)

        # Combine all frames and append the beep sound at the end
        recorded_audio = b''.join(frames)
        return recorded_audio

    def play_audio(self, audio_data):
        """Plays audio on the output stream."""

        if audio_data is not None:
            self.output_stream.write(audio_data)

    def save_audio_to_wav(self, filename, audio_data):
        """Saves audio data to a .wav file."""
        # filename = os.path.join("saved_audio", filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(audio_data)

        print(f"Audio saved to {filename}.")
        return filename

    def close(self):
        """Closes the audio streams."""
        self.input_stream.stop_stream()
        self.input_stream.close()
        self.output_stream.stop_stream()
        self.output_stream.close()
        self.p.terminate()


class AudioRecorder(AudioProcessor):
    """Handles audio recording, processing, and saving."""

    def __init__(self, input_device_name=None, output_device_name=None, format=pyaudio.paInt16, channels=1, rate=22050, chunk=1024, duration=5):
        # Inherit from AudioProcessor
        super().__init__(input_device_name=input_device_name, output_device_name=output_device_name, format=format, channels=channels, rate=rate, chunk=chunk, duration=duration)

    def capture_chunk(self):
        """Records audio for the specified duration."""
        return super().capture_chunk()


class OutputAudioProcessor(AudioProcessor):
    """Handles capturing audio output and saving it to a file in chunks."""

    def __init__(self, input_device_name=None, output_device_name=None, format=pyaudio.paInt16, channels=1, rate=22050, chunk=1024, duration=5):
        # Inherit from AudioProcessor
        super().__init__(input_device_name=input_device_name, output_device_name=output_device_name, format=format, channels=channels, rate=rate, chunk=chunk, duration=duration)

    def capture_chunk(self):
        """Records audio for the specified duration."""
        return super().capture_chunk()




def main_input(token):

    input_device_name = "Microphone (High Definition Aud"
    output_device_name = "CABLE Output (VB-Audio Virtual C"

    # Create AudioRecorder instance
    audio_recorder = AudioRecorder(input_device_name=input_device_name, output_device_name=output_device_name)
    
    # Create services (assuming these classes are defined elsewhere in the code)
    asr_service = ASRService()  # For transcribing audio
    sts_service = STSService(token)  # For text-to-speech

    print("Recording audio... Press Ctrl+C to stop.")
    counter = 1
    try:
        while True:
            # Record audio for the set duration and capture the recorded data
            recorded_audio = audio_recorder.capture_chunk()

            # Define a filename for saving the recorded audio
            filename = f"sended_audio/audio_{counter}.wav"

            # Save the recorded audio to a .wav file
            saved_audio_filename = audio_recorder.save_audio_to_wav(filename, recorded_audio)

            # Transcribe the saved audio file using ASR service
            transcript = asr_service.transcribe_audio(saved_audio_filename)
            print(f"Transcript Input: {transcript}")

            # Synthesize speech from the transcript using TTS service
            output_filename = sts_service.synthesize_speech(saved_audio_filename, 'english', 'tamil', 'female', audio_recorder.output_stream)
            audio_recorder.play_audio(output_filename)
            counter += 1

    except KeyboardInterrupt:
        print("\nRecording stopped.")

    finally:
        # Cleanup: Close the streams and terminate PyAudio
        audio_recorder.close()



def main_output(token):

    input_device_name = "CABLE Output (VB-Audio Virtual"
    output_device_name = "Speakers (High Definition Audio"

    # Create AudioRecorder instance
    audio_recorder = OutputAudioProcessor(input_device_name=input_device_name, output_device_name=output_device_name)
    
    # Create services (assuming these classes are defined elsewhere in the code)
    asr_service = ASRService()  # For transcribing audio
    sts_service = STSService(token)  # For text-to-speech

    print("Recording audio... Press Ctrl+C to stop.")
    counter = 1
    try:
        while True:
            # Record audio for the set duration and capture the recorded data
            recorded_audio = audio_recorder.capture_chunk()

            # Define a filename for saving the recorded audio
            filename = f"received_audio/audio_{counter}.wav"

            # Save the recorded audio to a .wav file
            saved_audio_filename = audio_recorder.save_audio_to_wav(filename, recorded_audio)

            # Transcribe the saved audio file using ASR service
            transcript = asr_service.transcribe_audio(saved_audio_filename)
            print(f"Transcript Output: {transcript}")

            # Synthesize speech from the transcript using TTS service
            output_filename = sts_service.synthesize_speech(saved_audio_filename, 'english', 'tamil', 'female', audio_recorder.output_stream)
            audio_recorder.play_audio(output_filename)
            counter += 1

    except KeyboardInterrupt:
        print("\nRecording stopped.")

    finally:
        # Cleanup: Close the streams and terminate PyAudio
        audio_recorder.close()



from multiprocessing import Process

def main():
    installer = VBCableInstaller()
    installer.install()

    obtain_auth_token()

    if not token:
        raise Exception("Token was not obtained successfully. Exiting.")

    input_process = Process(target=main_input, args=(token,))
    output_process = Process(target=main_output, args=(token,))

    input_process.start()
    output_process.start()

    input_process.join()
    output_process.join()

if __name__ == "__main__":
    main()