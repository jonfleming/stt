from pidog import Pidog
from time import sleep
from math import sin
from preset_actions import scratch, hand_shake, high_five, pant, body_twisting, bark_action, shake_head_smooth, bark, push_up, howling, attack_posture, lick_hand, feet_shake, sit_2_stand, nod, think, recall, alert, surprise,  stretch
import pocketsphinx
from pocketsphinx import LiveSpeech

def main():
    """
    Main function to initialize and run the speech recognition.
    """
    # For newer versions of PocketSphinx (>=5.0.0)
    # Configure LiveSpeech for microphone input
    speech = LiveSpeech(
        verbose=False,
        sampling_rate=16000,
        buffer_size=2048,
        no_search=False,
        full_utt=False
    )
    
    print("Listening... Speak into your microphone.")
    print("Press Ctrl+C to exit.")
    
    try:
        # Process speech continuously
        for phrase in speech:
            if not phrase or phrase.strip() == "":
                continue

            process_text(phrase)
            
    except KeyboardInterrupt:
        print("\nStopped listening.")

# Import Pidog class
from pidog import Pidog

# instantiate a Pidog with custom initialized servo angles
my_dog = Pidog(leg_init_angles = [25, 25, -25, -25, 70, -45, -70, 45],
                head_init_angles = [0, 0, -25],
                tail_init_angle= [0]
            )

def process_text(text):
    print(text)
    execute(text)

def execute(text):
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
    if ("bark" in text):
        bark_action(my_dog)
    if ("no" in text):
        shake_head_smooth(my_dog)
    if ("bark" in text):
        bark(my_dog)
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

if __name__ == '__main__':
    print("Wait until it says 'speak now'")
    recorder = AudioToTextRecorder()

    while True:
        recorder.text(process_text)