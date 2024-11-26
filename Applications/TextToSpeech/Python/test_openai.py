import os
import io
import requests
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configure OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OpenAI API key must be set in the .env file")


def stream_and_play_tts(text: str, model: str = "tts-1", voice: str = "alloy") -> None:
    """
    Stream and play TTS audio using OpenAI's API.

    :param text: The text to convert to speech
    :param model: The TTS model to use
    :param voice: The voice to use for TTS
    :return: None
    """
    url = "https://api.openai.com/v1/audio/speech"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "voice": voice,
        "input": text
    }

    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()

        audio_stream = io.BytesIO()
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                audio_stream.write(chunk)

        audio_stream.seek(0)
        audio_segment = AudioSegment.from_file(audio_stream, format='mp3')
        play(audio_segment)

    except requests.RequestException as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    text = "Hello world! This is a streaming test."
    stream_and_play_tts(text)
