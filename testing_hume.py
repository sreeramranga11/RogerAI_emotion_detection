import asyncio
import base64
import sounddevice as sd
import websockets

async def main():
    # Update the API endpoint URL and your API key
    endpoint_url = 'wss://api.hume.ai/v0/stream/models'
    api_key = 'jQQ9gJQPXS31GWAk2H1AJlBuYPfpEnd4EnapBO8JNdwxppuZ'

    async with websockets.connect(endpoint_url, extra_headers={'X-Hume-Api-Key': api_key}) as websocket:
        # Configure sounddevice to record audio
        duration = 5  # Recording duration in seconds
        sample_rate = 44100  # Sample rate for the audio
        channels = 1  # Number of audio channels (mono)

        print("Recording started. Speak into the microphone...")
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels)
        sd.wait()  # Wait until recording is complete

        print("Recording finished.")

        # Encode the recorded audio data
        encoded_data = encode_data(audio_data)

        # Construct the JSON message
        message = {
            "models": {
                "language": {}
            },
            "raw_audio": True,
            "data": encoded_data
        }

        # Send the JSON message to the socket
        await websocket.send(message)

        # Receive and process the response
        response = await websocket.recv()
        print(response)

def encode_data(audio_data):
    # Convert audio data to bytes
    audio_bytes = audio_data.tobytes()

    # Encode audio bytes as base64
    encoded_data = base64.b64encode(audio_bytes).decode("utf-8")
    return encoded_data

asyncio.run(main())
