"""psycopg raw SQL 저장소 (F1.4 초판 — Slice 2에서 SQLAlchemy로 정식화)"""

from collections.abc import Iterable, Sequence
from datetime import datetime

import psycopg
from psycopg.rows import class_row

from steam_rag.domain.models import Review

# ── 테이블 보장 DDL (Alembic 도입 전 임시) ──
# recommendation_id 를 UNIQUE 로 잡아야 ON CONFLICT 가 걸린다.
_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS reviews (
    id                     BIGSERIAL PRIMARY KEY,
    recommendation_id      BIGINT      NOT NULL UNIQUE,
    appid                  BIGINT      NOT NULL,
    author_steamid         VARCHAR(32) NOT NULL,
    content                TEXT        NOT NULL,
    voted_up               BOOLEAN     NOT NULL,
    playtime_at_review_min INTEGER     NOT NULL,
    votes_helpful          INTEGER     NOT NULL,
    created_at             TIMESTAMPTZ NOT NULL,
    collected_at           TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_reviews_appid ON reviews (appid);
"""

# %(name)s = 이름 있는 자리표시자. 딕셔너리 키와 매칭된다.
# 중복 recommendation_id 는 조용히 건너뛴다(멱등).
_INSERT = """
INSERT INTO reviews (
    recommendation_id, appid, author_steamid, content, voted_up,
    playtime_at_review_min, votes_helpful, created_at, collected_at
) VALUES (
    %(recommendation_id)s, %(appid)s, %(author_steamid)s, %(content)s, %(voted_up)s,
    %(playtime_at_review_min)s, %(votes_helpful)s, %(created_at)s, %(collected_at)s
)
ON CONFLICT (recommendation_id) DO NOTHING
"""

_SELECT_BY_APPID = """
SELECT recommendation_id, appid, author_steamid, content, voted_up,
       playtime_at_review_min, votes_helpful, created_at, collected_at
FROM reviews
WHERE appid = %s
ORDER BY created_at DESC
LIMIT %s
"""


class PostgreReviewRepository:
    """ReviewRepository 프로토콜 구현"""

    def __init__(self, dsn: str) -> None:  # dsn : Data Source Name
        self._dsn = dsn.replace("postgresql+psycopg://", "postgresql://")
        self._ensure_schema()

    def _ensure_schema(self) -> None:  # ensure : 보장한다
        with psycopg.connect(self._dsn) as conn:  # with 블록 정상 종료시 psycopg 가 자동 commit
            conn.execute(_CREATE_TABLE)

    def save_many(self, reviews: Iterable[Review]) -> int:
        rows = [self._to_row(r) for r in reviews]
        if not rows:
            return 0

        with psycopg.connect(self._dsn) as conn, conn.cursor() as cur:
            cur.executemany(_INSERT, rows)
            return cur.rowcount

    def get_by_appid(self, appid: int, limit: int) -> Sequence[Review]:
        # row_factory=class_row(Review): DB에서 가져온 한 행(row)을 Review 객체로 자동 변환해주는 설정
        with psycopg.connect(self._dsn) as conn, conn.cursor(row_factory=class_row(Review)) as cur:
            cur.execute(_SELECT_BY_APPID, (appid, limit))
            return cur.fetchall()

    @staticmethod  # 클래스 안에 있지만 클래스나 객체와는 관계없이 동작하는 일반 함수
    def _to_row(review: Review) -> dict[str, object]:
        return {
            "recommendation_id": int(review.recommendation_id),
            "appid": int(review.appid),
            "author_steamid": review.author_steamid,
            "content": review.content,
            "voted_up": bool(review.voted_up),
            "playtime_at_review_min": int(review.playtime_at_review_min),
            "votes_helpful": int(review.votes_helpful),
            "created_at": _as_datetime(review.created_at),
            "collected_at": _as_datetime(review.collected_at),
        }


def _as_datetime(value: datetime) -> datetime:
    # pandas.Timestamp 는 datetime 의 서브클래스라 to_pydatetime() 로 표준화.
    to_py = getattr(value, "to_pydatetime", None)
    if to_py is not None:
        result: datetime = to_py()
        return result
    return value
