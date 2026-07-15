"""
수집 파이프라인 오케스트레이션 : 수집 -> 정제 -> 한국어정제 -> 적재
"""

from dataclasses import dataclass

from steam_rag.domain.interfaces import ReviewCollector, ReviewRepository
from steam_rag.etl.language import filter_korean
from steam_rag.etl.transform import clean_reviews


@dataclass(frozen=True, slots=True)
class IngestResult:
    collected: int
    cleaned: int
    korean: int
    saved: int


def ingest_reviews(collector: ReviewCollector, repository: ReviewRepository, appid: int, limit: int) -> IngestResult:
    raw = list(collector.collect(appid=appid, limit=limit))
    cleaned = clean_reviews(raw)
    korean = filter_korean(cleaned)
    saved = repository.save_many(korean)

    return IngestResult(collected=len(raw), cleaned=len(cleaned), korean=len(korean), saved=saved)
