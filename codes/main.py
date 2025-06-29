import os
import tempfile
from typing import List, Optional, Dict
from fastapi import FastAPI, File, UploadFile, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv
import openai
from retrieve_chunks import get_chunk
from translate import translate_with_whisper
from response_url import Chatbot
from studyguide import StudyGuide
from all_lang_podcast import Podcast

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

study_tool = StudyGuide()
podcast = Podcast()
chatbot = Chatbot()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==== MODELS ====


class QAItem(BaseModel):
    question: str
    answer: Optional[str]


class QuestionRequest(BaseModel):
    question: str
    timestamp: str
    conversation: List[QAItem] = []


class BotResponse(BaseModel):
    reply: str
    received_at: str


class SelectedDocument(BaseModel):
    id: int
    name: str
    path: str


class DocumentRequest(BaseModel):
    selectedDocs: List[SelectedDocument]


class PodcastRequest(BaseModel):
    language: str
    selectedDocs: List[SelectedDocument]


class TitleRequest(BaseModel):
    type: str
    selectedDocs: List[SelectedDocument]


class ChunkRequest(BaseModel):
    source: str
    chunkid: str


# ==== ENDPOINTS ====


@app.post("/ask", response_model=BotResponse)
async def ask_question(payload: QuestionRequest):
    print(f"Received question: {payload.question}")
    print("Conversation history:")
    for item in payload.conversation:
        print(f"Q: {item.question}\nA: {item.answer}")

    llmreply = await run_in_threadpool(
        chatbot.get_response, payload.question, payload.conversation
    )
    return BotResponse(reply=llmreply, received_at=datetime.utcnow().isoformat())


@app.post("/getchunk")
async def get_relevant_chunk(payload: ChunkRequest):
    print(f"Received source: {payload.source}")
    print(f"Received chunk: {payload.chunkid}")
    chunk = await run_in_threadpool(get_chunk, payload.source, payload.chunkid)
    return chunk


@app.post("/get-note-title")
async def get_note_title(payload: TitleRequest):
    names = [doc.name for doc in payload.selectedDocs]
    print("Generating a title for the received documents:", names)
    title = await run_in_threadpool(study_tool.generate_title, names, payload.type)
    return title


@app.post("/study-guide")
async def generate_study_guide(payload: DocumentRequest):
    doc_paths = [doc.path for doc in payload.selectedDocs]
    print("Generating Study Guide for:", doc_paths)
    response = await run_in_threadpool(study_tool.generate_studyguide, doc_paths)
    return response


@app.post("/faq")
async def generate_faq_endpoint(payload: DocumentRequest):
    doc_paths = [doc.path for doc in payload.selectedDocs]
    print("Generating FAQ for:", doc_paths)
    response = await run_in_threadpool(study_tool.generate_faq, doc_paths)
    return response


@app.post("/generate-mindmap")
async def generate_mindmap_api(payload: DocumentRequest):
    doc_paths = [doc.path for doc in payload.selectedDocs]
    print("Generating mindmap for:", doc_paths)
    mindmap_markdown = await run_in_threadpool(study_tool.generate_mindmap, doc_paths)
    return {"markdown": mindmap_markdown}


@app.post("/briefing-doc")
async def generate_briefing_doc(payload: DocumentRequest):
    doc_paths = [doc.path for doc in payload.selectedDocs]
    print("Generating Briefing Document for:", doc_paths)
    response = await run_in_threadpool(study_tool.generate_briefing_document, doc_paths)
    return response


@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    print(f"Received audio file: {audio.filename}")
    transcription = await run_in_threadpool(translate_with_whisper, audio)
    return {"transcription": transcription}


@app.post("/podcast")
async def set_language(payload: PodcastRequest):
    language = payload.language
    doc_paths = [doc.path for doc in payload.selectedDocs]
    print(f"Generating podcast in {language} for:", doc_paths)
    audiopath = await run_in_threadpool(podcast.generate_podcast, language, doc_paths)
    return {"audio_url": f"http://127.0.0.1:8000{audiopath}"}


@app.post("/generate-audio/")
async def generate_audio(payload: dict):
    text = payload.get("text", "")
    response = await run_in_threadpool(
        client.audio.speech.create,
        model="gpt-4o-mini-tts",
        voice="nova",
        input=text,
        response_format="mp3",
    )
    audio_content = response.content
    return Response(content=audio_content, media_type="audio/mpeg")


@app.get("/card-data")
def get_card_data() -> Dict:
    return {
        "title": "Sources",
        "modules": [
            {
                "name": "Module 1",
                "documents": [
                    {
                        "id": 1,
                        "name": "Ongoing Issues in Test Fairness",
                        "path": "C:\\Users\\Maham Jafri\\Documents\\Office Tasks\\Durbeen\\ResearchArticles\\research_mds\\Ongoing issues in test fairness.md",
                        "viewpath": "/docs/Ongoing issues in test fairness.md",
                    },
                    {
                        "id": 2,
                        "name": "Portfolio Purposes",
                        "path": "C:\\Users\\Maham Jafri\\Documents\\Office Tasks\\Durbeen\\ResearchArticles\\research_mds\\Portfolio Purposes.md",
                        "viewpath": "/docs/Portfolio Purposes.md",
                    },
                    {
                        "id": 3,
                        "name": "Can a picture ruin a thousand words",
                        "path": "C:\\Users\\Maham Jafri\\Documents\\Office Tasks\\Durbeen\\ResearchArticles\\research_mds\\Can a picture ruin a thousand words  The effects of visual resources in exam questions.md",
                        "viewpath": "/docs/Can a picture ruin a thousand words  The effects of visual resources in exam questions.md",
                    },
                    {
                        "id": 4,
                        "name": "Does washback exists?",
                        "path": "C:\\Users\\Maham Jafri\\Documents\\Office Tasks\\Durbeen\\ResearchArticles\\research_mds\\Does Washback Exists.md",
                        "viewpath": "/docs/Does Washback Exists.md",
                    },
                ],
            },
            {"name": "Module 2", "documents": []},
            {"name": "Module 3", "documents": []},
            {"name": "Module 4", "documents": []},
        ],
        "audioOverview": True,
        "notesAndHighlights": True,
    }
