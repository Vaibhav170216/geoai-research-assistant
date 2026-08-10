"""FastAPI server for the GeoAI Research Assistant."""

from functools import lru_cache
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from assistant import load_assistant
from db_save import save_conversation


TOPICS = [
    "geoai",
    "earth observation",
    "remote sensing",
    "sentinel-2",
    "land use land cover classification",
    "vision transformer",
    "foundation models",
    "change detection",
    "satellite imagery",
    "self-supervised learning",
]


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10_000)
    topic: str | None = None


class ChatResponse(BaseModel):
    answer: str
    response_time: float
    conversation_id: int | None = None


@lru_cache(maxsize=1)
def get_assistant():
    """Load the search and embedding models once per server process."""
    return load_assistant()


app = FastAPI(title="GeoAI Research Assistant API", version="1.0.0")
assistant_lock = Lock()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/topics")
def list_topics():
    return {"topics": TOPICS}


@app.get("/api/knowledge-base")
def knowledge_base():
    assistant = get_assistant()
    return {"papers": assistant.index.count()}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    topic = request.topic.strip().lower() if request.topic else None
    if topic and topic not in TOPICS:
        raise HTTPException(status_code=422, detail="Unknown research topic.")

    # The RAG object stores the selected topic and the latest call metrics, so
    # keep each request's retrieval and logging data isolated from other users.
    with assistant_lock:
        assistant = get_assistant()
        assistant.topic = topic
        answer = assistant.rag(request.question.strip())
        record = assistant.last_call

    # Monitoring must not make the chat unavailable when PostgreSQL is offline.
    conversation_id = None
    try:
        conversation_id = save_conversation(record, request.question.strip(), "geoai-research-assistant")
    except Exception as exc:  # pragma: no cover - depends on deployment services
        print(f"Could not save conversation: {exc}")

    return ChatResponse(
        answer=answer,
        response_time=record.response_time,
        conversation_id=conversation_id,
    )


frontend_dist = Path(__file__).parent / "frontend" / "dist"
if frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    @app.get("/", include_in_schema=False)
    async def root():
        return {"message": "GeoAI Research Assistant API. Visit /docs for API documentation."}
