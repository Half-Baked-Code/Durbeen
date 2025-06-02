import tempfile
import os
from fastapi import UploadFile
from dotenv import load_dotenv
from openai import OpenAI  # New import style

# ✅ Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Instantiate client with key


def translate_with_whisper(audio: UploadFile) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
        temp_audio.write(audio.file.read())
        temp_audio.flush()
        temp_path = temp_audio.name

    try:
        with open(temp_path, "rb") as f:
            result = client.audio.transcriptions.create(
                file=f, model="whisper-1", language="en"  # Set language to Urdu
            )
        return result.text
    except Exception as e:
        raise RuntimeError(f"Translation failed: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
