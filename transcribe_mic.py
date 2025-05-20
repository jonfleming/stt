import argparse
import os
import wave
import sys

import pyaudio
from google.cloud import speech

def record(duration, filename, fs=16000, channels=1, frames_per_buffer=1024):
    pa = pyaudio.PyAudio()
    try:
        stream = pa.open(format=pyaudio.paInt16,
                        channels=channels,
                        rate=fs,
                        input=True,
                        frames_per_buffer=frames_per_buffer)
    except Exception as e:
        print(f'Could not open microphone stream: {e}')
        pa.terminate()
        sys.exit(1)

    print(f'Recording {duration} seconds...')
    frames = []

    for _ in range(int(fs / frames_per_buffer * duration)):
        data = stream.read(frames_per_buffer)
        frames.append(data)

    print('Recording complete.')

    stream.stop_stream()
    stream.close()
    pa.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_file(speech_file, fs=16000, language_code='en-US'):
    client = speech.SpeechClient()

    with open(speech_file, 'rb') as f:
        content = f.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=fs,
        language_code=language_code,
    )

    print('Transcribing...')
    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        transcript = result.alternatives[0].transcript
        print(f'Transcript: {transcript}')

def main():
    parser = argparse.ArgumentParser(
        description='Record audio from microphone and transcribe using Google Cloud Speech-to-Text'
    )
    parser.add_argument('--duration', '-d', type=float, default=5.0,
                        help='Recording duration in seconds')
    parser.add_argument('--file', '-f', type=str, default='output.wav',
                        help='Output WAV file name')
    parser.add_argument('--language', '-l', type=str, default='en-US',
                        help='Language code (e.g., en-US)')
    args = parser.parse_args()

    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print('Error: The GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.')
        sys.exit(1)

    record(args.duration, args.file)
    transcribe_file(args.file, language_code=args.language)

if __name__ == '__main__':
    main()