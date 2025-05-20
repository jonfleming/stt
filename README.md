 # Speech-to-Text Microphone Transcription
 
 Records audio from a microphone on a Raspberry Pi using PyAudio and transcribes it using the Google Cloud Speech-to-Text API.
 
 ## Prerequisites
 
 - Python 3
 - Microphone and audio input configured on your Raspberry Pi
 - A Google Cloud project with the Speech-to-Text API enabled
 - A service account key JSON file. Set the environment variable:
 
 ```bash
 export GOOGLE_APPLICATION_CREDENTIALS='/path/to/your-service-account-key.json'
 ```
 
 ### Install system dependencies
 
 ```bash
 sudo apt-get update
 sudo apt-get install python3-pyaudio
 ```
 
 ### Install Python dependencies
 
 ```bash
 python3 -m venv venv
 source venv/bin/activate
 pip install -r requirements.txt
 ```
 
 ## Usage
 
 ```bash
 python3 transcribe_mic.py --duration 5 --file output.wav --language en-US
 ```