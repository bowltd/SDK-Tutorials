import requests
from dotenv import load_dotenv
import os
import io
from pydub import AudioSegment
from pydub.playback import play
import urllib3

# Suppress only the single InsecureRequestWarning from urllib3 needed for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from the .env file
load_dotenv()

# Configure the server endpoint
WILLOW_SERVER_URL = os.getenv('WILLOW_SERVER_URL')
if not WILLOW_SERVER_URL:
    raise ValueError("Willow server URL must be set in the .env file")

def stream_text_to_speech(text: str, format: str = 'WAV', speaker: str = 'default') -> None:
    """
    Stream audio data from the TTS server as it is generated.

    :param text: Text to convert to speech.
    :param format: Audio format (e.g., 'WAV').
    :param speaker: Speaker ID.
    :return: None.
    """
    params = {
        'text': text,
        'format': format,
        'speaker': speaker
    }

    try:
        response = requests.get(WILLOW_SERVER_URL, params=params, stream=True, verify=False)
        response.raise_for_status()  # Raise HTTPError for bad responses

        audio_stream = io.BytesIO()
        for chunk in response.iter_content(chunk_size=4096):
            audio_stream.write(chunk)

        audio_stream.seek(0)
        audio_segment = AudioSegment.from_file(audio_stream, format=format)
        play(audio_segment)

    except requests.RequestException as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    text = "Hello, this is a test of the text to speech system."
    format = 'wav'
    speaker = 'CLB'

    stream_text_to_speech(text, format, speaker)
