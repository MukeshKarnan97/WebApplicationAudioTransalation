import pyaudio
import time
import wave
import os

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
