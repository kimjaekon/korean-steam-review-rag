"""FastAPI 진입점"""

from fastapi import FastAPI

from steam_rag.config.settings import settings
from steam_rag.serving.schemas import ReviewOut
from steam_rag.storage.postgres.repository import PostgresReviewRepository

app = FastAPI(title="Korean Steam Review RAG", version="0.1.0")


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "llm_provider": settings.llm.provider, "agent_mode": settings.agent_mode}


@app.get("/reviews/{appid}")
def get_reviews(appid: int, limit: int = 20) -> list[ReviewOut]:
    repo = PostgresReviewRepository()
    reviews = repo.get_by_appid(appid=appid, limit=limit)
    return [ReviewOut.model_validate(review) for review in reviews]
