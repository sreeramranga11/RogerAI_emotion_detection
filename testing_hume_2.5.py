import pandas as pd
import asyncio
import base64
import ssl
import websockets
import json
from hume import HumeStreamClient
from hume.models.config import BurstConfig

async def main():
    # Update the API endpoint URL and your API key
    endpoint_url = 'wss://api.hume.ai/v0/stream/models'
    api_key = 'jQQ9gJQPXS31GWAk2H1AJlBuYPfpEnd4EnapBO8JNdwxppuZ'

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

        # Filter and calculate average scores for the 10 most important emotions
        top_10_emotions = [
            'Calmness', 'Contentment', 'Determination', 'Relief', 'Satisfaction',
            'Joy', 'Love', 'Empathic Pain', 'Sympathy', 'Sadness'
        ]
        filtered_data = [d for d in data if d['Emotion'] in top_10_emotions]
        averaged_data = []
        for emotion in top_10_emotions:
            related_emotions = [d['Score'] for d in filtered_data if d['Emotion'] == emotion or d['Emotion'].startswith(emotion.split()[0])]
            average_score = sum(related_emotions) / len(related_emotions)
            averaged_data.append({'Emotion': emotion, 'Average Score': average_score})

        # Convert the data to a DataFrame
        df = pd.DataFrame(averaged_data)

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
