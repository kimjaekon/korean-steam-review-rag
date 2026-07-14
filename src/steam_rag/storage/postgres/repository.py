"""psycopg raw SQL 저장소 (F1.4 초판 — Slice 2에서 SQLAlchemy로 정식화)"""

from collections.abc import Iterable, Sequence
from typing import cast

from sqlalchemy import CursorResult, select  # CursorResult: SQLAlchemy가 SQL을 실행한 뒤 DB 커서(cursor)를 감싼 결과 객체
from sqlalchemy.dialects.postgresql import insert as pg_insert

from steam_rag.domain.models import Review
from steam_rag.storage.postgres.models import ReviewORM
from steam_rag.storage.postgres.session import SessionLocal


class PostgresReviewRepository:
    """ReviewRepository 프로토콜 구현"""

    def save_many(self, reviews: Iterable[Review]) -> int:
        rows = [self._to_mapping(r) for r in reviews]
        if not rows:
            return 0

        # ON CONFLICT DO NOTHING: recommendation_id 중복은 조용히 건너뜀(멱등) # do_update 는 덮어씌움
        stmt = pg_insert(ReviewORM).values(rows).on_conflict_do_nothing(index_elements=["recommendation_id"])

        with SessionLocal.begin() as session:  # begin(): 정상 종료 시 commit, 예외 시 rollback
            result = cast("CursorResult[object]", session.execute(stmt))
            return result.rowcount

    def get_by_appid(self, appid: int, limit: int) -> Sequence[Review]:
        stmt = select(ReviewORM).where(ReviewORM.appid == appid).order_by(ReviewORM.created_at.desc()).limit(limit)

        with SessionLocal() as session:
            orm_rows = session.scalars(stmt).all()
            return [self._to_domain(row) for row in orm_rows]
        """
        session.scalars(stmt).all() -> 반환 타입 list[Object]
        session.scalars(stmt) -> 반환 타입 ScalarResult
        session.scalar(stmt) -> 반환 타입 객체 하나
        """

    @staticmethod
    def _to_mapping(review: Review) -> dict[str, object]:
        return {
            "recommendation_id": int(review.recommendation_id),
            "appid": int(review.appid),
            "author_steamid": review.author_steamid,
            "content": review.content,
            "voted_up": bool(review.voted_up),
            "playtime_at_review_min": int(review.playtime_at_review_min),
            "votes_helpful": int(review.votes_helpful),
            "created_at": review.created_at,
            "collected_at": review.collected_at,
        }

    @staticmethod
    def _to_domain(orm: ReviewORM) -> Review:
        return Review(
            recommendation_id=orm.recommendation_id,
            appid=orm.appid,
            author_steamid=orm.author_steamid,
            content=orm.content,
            voted_up=orm.voted_up,
            playtime_at_review_min=orm.playtime_at_review_min,
            votes_helpful=orm.votes_helpful,
            created_at=orm.created_at,
            collected_at=orm.collected_at,
        )
