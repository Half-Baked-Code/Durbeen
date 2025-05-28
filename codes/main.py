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
    llmreply = get_response()  # Assuming this function is defined elsewhere
    return BotResponse(
        # reply=f"Thanks for your question: '{payload.question}'. I'm processing it!",
        reply=llmreply,
        received_at=datetime.utcnow().isoformat(),
    )
