# from fastapi import FastAPI, Request
# from pydantic import BaseModel
# from datetime import datetime
# from fastapi.middleware.cors import CORSMiddleware
# from mindmap import generate_mind_map
# from faq import generate_faq
# from studyguide import generate_studyguide
# from llm_response import get_response

# app = FastAPI()

# # Allow frontend (adjust origin for production)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Update with your frontend URL in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# class QuestionRequest(BaseModel):
#     question: str
#     timestamp: str


# class BotResponse(BaseModel):
#     reply: str
#     received_at: str


# @app.post("/ask", response_model=BotResponse)
# async def ask_question(payload: QuestionRequest):
#     print(f"Received question: {payload.question}")
#     print(f"Timestamp: {payload.timestamp}")
#     llmreply = get_response(
#         question=payload.question
#     )  # Assuming this function is defined elsewhere
#     return BotResponse(
#         # reply=f"Thanks for your question: '{payload.question}'. I'm processing it!",
#         reply=llmreply,
#         received_at=datetime.utcnow().isoformat(),
#     )


# class DocumentRequest(BaseModel):
#     document_path: str


# @app.post("/study-guide")
# async def generate_study_guide(payload: DocumentRequest):
#     print(f"Generating study guide for: {payload.document_path}")
#     response = generate_studyguide(doc_path=payload.document_path)
#     return {"result": response}


# @app.post("/faq")
# async def generatefaq(payload: DocumentRequest):
#     print(f"Generating FAQ for: {payload.document_path}")
#     response = generate_faq(doc_path=payload.document_path)
#     return {"result": response}


# @app.post("/mind-map")
# async def generate_briefing_doc(payload: DocumentRequest):
#     print(f"Generating mindmap for: {payload.document_path}")
#     response = generate_mind_map(doc_path=payload.document_path)
#     return {"result": response}

# @app.post("/briefing-doc")
# async def generate_briefing_doc(payload: DocumentRequest):
#     print(f"Generating Briefing Document for: {payload.document_path}")
#     response = generate_mind_map(doc_path=payload.document_path)
#     return {"result": response}

import tempfile
from fastapi import FastAPI, File, UploadFile
import openai
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from translate import translate_with_whisper
from llm_response import get_response
from studyguide import (
    StudyGuide,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

study_tool = StudyGuide()


class QuestionRequest(BaseModel):
    question: str
    timestamp: str


class BotResponse(BaseModel):
    reply: str
    received_at: str


class DocumentRequest(BaseModel):
    document_path: str


@app.post("/ask", response_model=BotResponse)
async def ask_question(payload: QuestionRequest):
    print(f"Received question: {payload.question}")
    llmreply = get_response(question=payload.question)
    return BotResponse(
        reply=llmreply,
        received_at=datetime.utcnow().isoformat(),
    )


@app.post("/study-guide")
async def generate_study_guide(payload: DocumentRequest):
    print(f"Generating Study Guide for: {payload.document_path}")
    response = study_tool.generate_studyguide(payload.document_path)
    return {"result": response}


@app.post("/faq")
async def generate_faq_endpoint(payload: DocumentRequest):
    print(f"Generating FAQ for: {payload.document_path}")
    response = study_tool.generate_faq(payload.document_path)
    return {"result": response}


@app.post("/mind-map")
async def generate_mindmap(payload: DocumentRequest):
    print(f"Generating Mindmap for: {payload.document_path}")
    response = study_tool.generate_mind_map(payload.document_path)
    return {"result": response}


@app.post("/briefing-doc")
async def generate_briefing_doc(payload: DocumentRequest):
    print(f"Generating Briefing Document for: {payload.document_path}")
    response = study_tool.generate_briefing_document(payload.document_path)
    return {"result": response}


openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your key


@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    print(f"Received audio file: {audio.filename}")
    print(f"Translating the audio file using whisper...")
    transcription = translate_with_whisper(audio)
    return {"transcription": transcription}
