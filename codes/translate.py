import tempfile
import os
from fastapi import UploadFile
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# this function is called when the user clicks on the mic icon and then this translates audio using OpenAI's Whisper model
def translate_with_whisper(audio: UploadFile) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
        temp_audio.write(audio.file.read())
        temp_audio.flush()
        temp_path = temp_audio.name

    try:
        with open(temp_path, "rb") as f:
            result = client.audio.transcriptions.create(
                file=f, model="whisper-1", language="en"
            )
        return result.text
    except Exception as e:
        raise RuntimeError(f"Translation failed: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
