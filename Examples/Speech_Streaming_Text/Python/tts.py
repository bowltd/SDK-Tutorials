import os
import io
import time
import requests
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv
import urllib3

# Suppress only the single InsecureRequestWarning from urllib3 needed for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from the .env file
load_dotenv()

# Configure API keys and server URLs
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key must be set in the .env file")

WILLOW_SERVER_URL = os.getenv('WILLOW_SERVER_URL')
if not WILLOW_SERVER_URL:
    raise ValueError("Willow server URL must be set in the .env file")


class TTS:
    last_tts_time = 0

    def __init__(self, service: str, rate_limit_ms: int = 800, **kwargs):
        """
        Initialize the TTS service.

        :param service: The TTS service to use ('willow' or 'openai').
        :param kwargs: Additional parameters for the TTS service.
        """
        self.service = service
        self.rate_limit_ms = rate_limit_ms
        if service == 'willow':
            self.server_url = kwargs.get('server_url', WILLOW_SERVER_URL)
            self.format = kwargs.get('format', 'WAV')
            self.speaker = kwargs.get('speaker', 'default')
        elif service == 'openai':
            self.api_key = kwargs.get('api_key', OPENAI_API_KEY)
            self.model = kwargs.get('model', 'tts-1')
            self.voice = kwargs.get('voice', 'alloy')
        else:
            raise ValueError("Unsupported service. Choose 'willow' or 'openai'.")

    def stream_text_to_speech(self, text: str, playback: bool = False) -> AudioSegment:
        """
        Stream TTS audio from the specified service.

        :param text: The text to convert to speech.
        :param playback: Whether to play the audio after streaming.
        :return: AudioSegment.
        """
        current_time_ms = int(time.time() * 1000)
        if current_time_ms - TTS.last_tts_time < self.rate_limit_ms:
            print("TTS rate limited. Try again later.")
            return None

        TTS.last_tts_time = current_time_ms

        if self.service == 'willow':
            url = self.server_url
            params = {
                'text': text,
                'format': self.format,
                'speaker': self.speaker
            }
            headers = None
        elif self.service == 'openai':
            url = "https://api.openai.com/v1/audio/speech"
            params = {
                "model": self.model,
                "voice": self.voice,
                "input": text
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

        if playback:
            return self._stream_and_play(url, params, headers)
        else:
            return self._stream_only(url, params, headers)

    def _stream_and_play(self, url: str, params: dict, headers: dict = None) -> AudioSegment:
        """
        Stream audio data from the TTS server and play it.

        :param url: The URL of the TTS service.
        :param params: The parameters for the TTS service.
        :param headers: The headers for the TTS service.
        :return: AudioSegment.
        """
        try:
            if headers:
                response = requests.post(url, json=params, headers=headers, stream=True)
            else:
                response = requests.get(url, params=params, stream=True, verify=False)

            response.raise_for_status()  # Raise HTTPError for bad responses

            audio_stream = io.BytesIO()
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    audio_stream.write(chunk)

            audio_stream.seek(0)
            audio_format = params.get('format', 'mp3').lower()
            audio_segment = AudioSegment.from_file(audio_stream, format=audio_format)
            play(audio_segment)
            return audio_segment

        except requests.RequestException as e:
            print(f"Error occurred: {e}")
            return None

    def _stream_only(self, url: str, params: dict, headers: dict = None) -> AudioSegment:
        """
        Stream audio data from the TTS server without playing it.

        :param url: The URL of the TTS service.
        :param params: The parameters for the TTS service.
        :param headers: The headers for the TTS service.
        :return: AudioSegment.
        """
        try:
            if headers:
                response = requests.post(url, json=params, headers=headers, stream=True)
            else:
                response = requests.get(url, params=params, stream=True, verify=False)

            response.raise_for_status()  # Raise HTTPError for bad responses

            audio_stream = io.BytesIO()
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    audio_stream.write(chunk)

            audio_stream.seek(0)
            audio_format = params.get('format', 'mp3').lower()
            audio_segment = AudioSegment.from_file(audio_stream, format=audio_format)
            return audio_segment

        except requests.RequestException as e:
            print(f"Error occurred: {e}")
            return None


if __name__ == "__main__":
    text = "Hello, this is a test of the text to speech system. I'm Willow!"
    text2 = "Hello, this is a test of the text to speech system. I'm OpenAI!"

    # Example usage with Willow with playback
    willow_tts = TTS(service='willow', format='wav', speaker='CLB')
    willow_tts.stream_text_to_speech(text, playback=True)

    # Example usage with OpenAI without playback
    openai_tts = TTS(service='openai', model='tts-1', voice='alloy')
    audio_segment = openai_tts.stream_text_to_speech(text2, playback=False)
    if audio_segment:
        print("Audio segment retrieved successfully")
