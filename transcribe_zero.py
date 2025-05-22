import argparse
import os
import wave
import sys
import pyaudio
from google.cloud import speech

def process_text(text):
    print("heard:", str(text))

   
def transcribe_streaming(fs=16000, channels=1, frames_per_buffer=1024, language_code='en-US'):
    """
    Continuously record audio from microphone and stream to Google Cloud Speech-to-Text.
    Press Ctrl+C to stop streaming.
    """
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=fs,
        language_code=language_code,
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )
    pa = pyaudio.PyAudio()
    try:
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=fs,
            input=True,
            frames_per_buffer=frames_per_buffer,
        )
    except Exception as e:
        print(f'Could not open microphone stream: {e}')
        pa.terminate()
        return

    print('Streaming... Press Ctrl+C to stop.')

    def request_generator():
        while True:
            try:
                data = stream.read(frames_per_buffer, exception_on_overflow=False)
            except KeyboardInterrupt:
                return
            yield speech.StreamingRecognizeRequest(audio_content=data)

    requests = request_generator()
    try:
        # streaming_recognize expects positional args: (streaming_config, requests)
        responses = client.streaming_recognize(streaming_config, requests)
        for response in responses:
            for result in response.results:
                transcript = result.alternatives[0].transcript
                if result.is_final:
                    process_text(transcript)
                else:
                    pass
                    # print(f'Partial: {transcript}', end='\r')
    except KeyboardInterrupt:
        print('\nStreaming stopped.')
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

def main():
    parser = argparse.ArgumentParser(
        description='Record audio from microphone and transcribe using Google Cloud Speech-to-Text'
    )

    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print('Error: The GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/jon/jonefleming-n8n-31f098b2ea64.json'
    
    transcribe_streaming()

if __name__ == '__main__':
    main()
