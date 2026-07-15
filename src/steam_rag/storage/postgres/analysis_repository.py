"""감정/피처 저장소"""

from collections.abc import Iterable
from datetime import UTC, datetime
from typing import cast

from sqlalchemy import CursorResult  # CursorResult: SQL을 실행한 결과를 담는 클래스
from sqlalchemy.dialects.postgresql import insert as pg_insert

from steam_rag.domain.models import SentimentResult
from steam_rag.storage.postgres.models import ReviewAnalysisORM
from steam_rag.storage.postgres.session import SessionLocal


class PostgreAnalysisRepository:
    """AnalysisRepository 프로톹콜 구현"""

    def save_many(self, results: Iterable[SentimentResult]) -> int:
        analyzed_at = datetime.now(UTC)
        rows = [self._to_mapping(r, analyzed_at) for r in results]
        if not rows:
            return 0

        stmt = pg_insert(ReviewAnalysisORM).values(rows)

        # 이미 분석된 리뷰(PK 충돌)는 최신 예측으로 덮어씀.
        # set_ 에는 "새로 넣으려던 값"(stmt.excluded)을 지정 → 재분석 결과로 갱신.
        stmt = stmt.on_conflict_do_update(
            index_elements=["review_recommendation_id"],
            set_={
                "sentiment_score": stmt.excluded.sentiment_score,
                "sentiment_label": stmt.excluded.sentiment_label,
                "matches_voted_up": stmt.excluded.matches_voted_up,
                "analyzed_at": stmt.excluded.analyzed_at,
            },
        )

        with SessionLocal.begin() as session:
            result = cast("CursorResult[object]", session.execute(stmt))
            return result.rowcount

    @staticmethod
    def _to_mapping(result: SentimentResult, analyzed_at: datetime) -> dict[str, object]:
        return {
            "review_recommendation_id": int(result.review_recommendation_id),
            "sentiment_score": float(result.sentiment_score),
            "sentiment_label": result.sentiment_label,
            "matches_voted_up": bool(result.matches_voted_up),
            "analyzed_at": analyzed_at,
        }
