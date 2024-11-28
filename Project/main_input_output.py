from audio_processor import AudioRecorder, OutputAudioProcessor
from sts_service import STSService
from asr_service import ASRService

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
            output_filename = sts_service.synthesize_speech(saved_audio_filename, 'english', 'tamil', 'female')
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
            output_filename = sts_service.synthesize_speech(saved_audio_filename, 'english', 'tamil', 'female')
            audio_recorder.play_audio(output_filename)
            counter += 1

    except KeyboardInterrupt:
        print("\nRecording stopped.")

    finally:
        # Cleanup: Close the streams and terminate PyAudio
        audio_recorder.close()
