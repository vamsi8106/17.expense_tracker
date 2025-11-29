#src/api/main.py
from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from time import perf_counter

from src.agent.chat_agent import run_agent
from src.utils.memory import clear_user, get_user, count_sessions
from src.utils.metrics import LLM_LATENCY, ACTIVE_USERS


app = FastAPI(title="Expense Assistant")


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.post("/chat")
async def chat(req: ChatRequest):
    """
    All LLM call counting & cache logic is inside chat_agent.py
    """
    start = perf_counter()

    # Update active user gauge
    ACTIVE_USERS.set(count_sessions())

    # Run agent
    reply = await run_agent(req.session_id, req.message)

    # Record latency
    latency = perf_counter() - start
    LLM_LATENCY.observe(latency)

    return {"response": reply}


@app.get("/reset/{session_id}")
def reset_session(session_id: str):
    clear_user(session_id)
    ACTIVE_USERS.set(count_sessions())
    return {"status": "session cleared"}


@app.get("/metrics")
async def metrics():
    """
    Prometheus endpoint
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
