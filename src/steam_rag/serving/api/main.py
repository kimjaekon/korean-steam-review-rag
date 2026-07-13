"""FastAPI 진입점"""

from fastapi import FastAPI

from steam_rag.config.settings import settings

app = FastAPI(title="Korean Steam Review RAG", version="0.1.0")


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "llm_provider": settings.llm.provider, "agent_mode": settings.agent_mode}
