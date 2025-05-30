from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from llm_response import get_response

app = FastAPI()

# Allow frontend (adjust origin for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str
    timestamp: str


class BotResponse(BaseModel):
    reply: str
    received_at: str


@app.post("/ask", response_model=BotResponse)
async def ask_question(payload: QuestionRequest):
    print(f"Received question: {payload.question}")
    print(f"Timestamp: {payload.timestamp}")
    llmreply = get_response(
        question=payload.question
    )  # Assuming this function is defined elsewhere
    return BotResponse(
        # reply=f"Thanks for your question: '{payload.question}'. I'm processing it!",
        reply=llmreply,
        received_at=datetime.utcnow().isoformat(),
    )


class DocumentRequest(BaseModel):
    document_path: str


@app.post("/study-guide")
async def generate_study_guide(payload: DocumentRequest):
    print(f"Generating study guide for: {payload.document_path}")
    response = get_response(document_path=payload.document_path, task="study_guide")
    return {"result": response}


@app.post("/faq")
async def generate_faq(payload: DocumentRequest):
    print(f"Generating FAQ for: {payload.document_path}")
    response = get_response(document_path=payload.document_path, task="faq")
    return {"result": response}


@app.post("/briefing-doc")
async def generate_briefing_doc(payload: DocumentRequest):
    print(f"Generating briefing doc for: {payload.document_path}")
    response = get_response(document_path=payload.document_path, task="briefing_doc")
    return {"result": response}
