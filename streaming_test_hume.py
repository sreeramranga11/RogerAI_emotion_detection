import asyncio
import base64
import ssl
import websockets
import json
import pandas as pd
import wave
import audioop
import speech_recognition as sr
from hume import HumeStreamClient
from hume.models.config import BurstConfig
from dotenv import load_dotenv
import os

async def main():
    # Endpoint URL and API Key in .env file
    load_dotenv('.env')
    endpoint_url = os.getenv('ENDPOINT_URL')
    api_key = os.getenv('API_KEY')

    ssl_context = ssl.SSLContext()
    ssl_context.verify_mode = ssl.CERT_NONE  # Disable certificate verification

    headers = {'X-Hume-Api-Key': api_key}
    async with websockets.connect(endpoint_url, extra_headers=headers, ssl=ssl_context) as websocket:
        client = HumeStreamClient(api_key)
        config = BurstConfig()

        client.connect([config])

        # Initialize speech recognition
        recognizer = sr.Recognizer()

        print("Speak now...")

        # Configure audio recording
        duration = 5  # Recording duration in seconds
        sample_rate = 44100  # Sample rate for recording
        channels = 1  # Number of audio channels
        sample_width = 2  # Sample width in bytes (16-bit audio)

        # Open a wave file for recording
        audio_filename = "recorded_audio.wav"
        audio_file = wave.open(audio_filename, 'wb')
        audio_file.setnchannels(channels)
        audio_file.setsampwidth(sample_width)
        audio_file.setframerate(sample_rate)

        # Record audio
        audio_data = []
        buffer_size = int(sample_rate / 10)  # Buffer size for audio samples

        try:
            for _ in range(int(duration * sample_rate / buffer_size)):
                audio_sample = client.receive_audio()
                if audio_sample is not None:
                    audio_data.append(audio_sample)
                    audio_file.writeframes(audio_sample)
        finally:
            audio_file.close()

        print("Recording finished.")

        with sr.AudioFile(audio_filename) as source:
            # Read the audio file
            audio = recognizer.record(source)

        # Encode the recorded audio data
        encoded_data = encode_data(audio)

        # Construct the JSON message
        message = {
            "data": encoded_data,
            "models": {
                "burst": {},
                "prosody": {}
            }
        }

        # Send the JSON message to the socket
        await websocket.send(json.dumps(message))

        # Receive and process the response
        response = await websocket.recv()
        data = process_response(response)

        # Convert the data to a DataFrame
        df = pd.DataFrame(data)

        # Save the DataFrame to an Excel file
        output_filename = "output.xlsx"
        df.to_excel(output_filename, index=False)
        print("Results saved to", output_filename)

def encode_data(audio):
    audio_bytes = audio.get_wav_data()
    encoded_data = base64.b64encode(audio_bytes).decode("utf-8")
    return encoded_data

def process_response(response):
    response_json = json.loads(response)
    prosody_predictions = response_json['prosody']['predictions'][0]['emotions']
    data = [{'Emotion': prediction['name'], 'Score': prediction['score']} for prediction in prosody_predictions]
    return data

asyncio.run(main())
