### best version ###
import asyncio
import base64
import ssl
import websockets
import json
import pandas as pd
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

        # Read the audio file
        input_filename = "happyaudio.wav"
        encoded_data = encode_data(input_filename)

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

def encode_data(input_filename):
    with open(input_filename, 'rb') as audio_file:
        audio_bytes = audio_file.read()
        encoded_data = base64.b64encode(audio_bytes).decode("utf-8")
        return encoded_data

def process_response(response):
    response_json = json.loads(response)
    prosody_predictions = response_json['prosody']['predictions'][0]['emotions']
    data = [{'Emotion': prediction['name'], 'Score': prediction['score']} for prediction in prosody_predictions]
    return data

asyncio.run(main())
