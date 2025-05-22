from pidog import Pidog
import argparse
import os
import wave
import sys
import pyaudio
from google.cloud import speech
from preset_actions import scratch, hand_shake, high_five, pant, body_twisting, bark_action, shake_head_smooth, bark, push_up, howling, attack_posture, lick_hand, feet_shake, sit_2_stand, nod, think, recall, alert, surprise,  stretch

# Import Pidog class
from pidog import Pidog

# instantiate a Pidog with custom initialized servo angles
my_dog = Pidog(leg_init_angles = [25, 25, -25, -25, 70, -45, -70, 45],
                head_init_angles = [0, 0, -25],
                tail_init_angle= [0]
            )

def process_text(text):
    print("heard:", str(text))
    execute(text)
    
def execute(text):
    if ("sit" in text):
        my_dog.do_action('sit', speed=80)
    if ("scratch" in text):
        scratch(my_dog)
    if ("shake" in text):
        hand_shake(my_dog)
    if ("five" in text):
        high_five(my_dog)
    if ("pant" in text):
        pant(my_dog)
    if ("twist" in text):
        body_twisting(my_dog)
    if ("speak" in text):
        bark_action(my_dog)
        bark(my_dog)
    if ("bark" in text):
        bark_action(my_dog)
        bark(my_dog)
    if ("no" in text):
        shake_head_smooth(my_dog)
    if ("up" in text):
        push_up(my_dog)
    if ("howl" in text):
        howling(my_dog)
    if ("attack" in text):
        attack_posture(my_dog)
    if ("lick" in text):
        lick_hand(my_dog)
    if ("stand" in text):
        sit_2_stand(my_dog)
    if ("yes" in text):
        nod(my_dog)
    if ("think" in text):
        think(my_dog)
    if ("recall" in text):
        recall(my_dog)
    if ("alert" in text):
        alert(my_dog)
    if ("surprise" in text):
        surprise(my_dog)
    if ("stretch" in text):
        stretch(my_dog)        
    
def transcribe_streaming(fs=44100, channels=1, frames_per_buffer=1024, language_code='en-US'):
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
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print('Error: The GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/jon/jonefleming-n8n-31f098b2ea64.json'

    transcribe_streaming()


if __name__ == '__main__':
    main()