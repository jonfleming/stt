import argparse
import os
import wave
import sys
import pyaudio
from spinner import Spinner
from google.cloud import speech

# PyAutoGUI will be imported only if needed
pyautogui = None

if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
    print('Error: The GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/jon/jonefleming-n8n-31f098b2ea64.json'

def process_text(text):
    print("heard:", str(text))

def process_text_gui(text):
    global pyautogui
    if pyautogui is None:
        try:
            import pyautogui
        except ImportError:
            print("Warning: pyautogui not installed. GUI automation disabled.")
            return process_text(text)

    print("heard:", str(text))

    if "enter" in text or "new line" in text:
        print("Pressing Enter...")
        pyautogui.hotkey("enter")
    elif "tab" in text or "next" in text:
        print("Pressing Tab...")
        pyautogui.hotkey("tab")
    elif "period" in text or "next" in text:
        print("Pressing period...")
        pyautogui.typewrite(". ")
    elif "delete" in text or "backspace" in text:
        print("Deleting...")
#        pyautogui.hotkey("numlock") # Ensure numlock is off
        pyautogui.hotkey('home')
        pyautogui.hotkey('shift', 'down')
        pyautogui.hotkey("backspace")
#        pyautogui.hotkey("numlock") # Turn numlock back on
    elif "space" in text:
        print("Pressing Space...")
        pyautogui.hotkey("space")
    else:
        pyautogui.typewrite(str(text))

    pa = pyaudio.PyAudio()
def record(duration, filename, sr=16000, channels=1, frames_per_buffer=1024):
    try:
        stream = pa.open(format=pyaudio.paInt16,
                        channels=channels,
                        rate=sr,
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
    wf.setframerate(sr)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_file(speech_file, sr=16000, language_code='en-US'):
    client = speech.SpeechClient()

    with open(speech_file, 'rb') as f:
        content = f.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sr,
        language_code=language_code,
    )

    print('Transcribing...')
    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        transcript = result.alternatives[0].transcript
        print(f'Transcript: {transcript}')
    
def transcribe_streaming(sr=16000, channels=1, frames_per_buffer=1024, language_code='en-US', callback=process_text_gui):
    """
    Continuously record audio from microphone and stream to Google Cloud Speech-to-Text.
    Press Ctrl+C to stop streaming.
    """
    spinner = Spinner("")
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sr,
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
            rate=sr,
            input=True,
            frames_per_buffer=frames_per_buffer,
        )
    except Exception as e:
        print(f'Could not open microphone stream: {e}')
        pa.terminate()
        return

    print('Streaming... Press Ctrl+C to stop.')
    spinner.start()

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
                    callback(transcript)
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
    parser.add_argument('--duration', '-d', type=float, default=5.0,
                        help='Recording duration in seconds')
    parser.add_argument('--file', '-f', type=str, default='output.wav',
                        help='Output WAV file name')
    parser.add_argument('--language', '-l', type=str, default='en-US',
                        help='Language code (e.g., en-US)')
    parser.add_argument('--stream', '-s', action='store_true',
                        help='Enable continuous streaming recognition')
    parser.add_argument('--sample', '-sr', type=str, default="44100",
                        help='Recording sample rate in Hz')
    parser.add_argument('--gui', '-g', action='store_true',
                        help='Enable keyboard automation with PyAutoGUI')
    args = parser.parse_args()

    callback_fn = process_text_gui if args.gui else process_text

    if args.stream:
        transcribe_streaming(sr=int(args.sample), language_code=args.language, callback=callback_fn)
    else:
        record(sr=int(args.sample), duration=args.duration, filename=args.file)
        transcribe_file(sr=int(args.sample), speech_file=args.file, language_code=args.language)

if __name__ == '__main__':
    main()