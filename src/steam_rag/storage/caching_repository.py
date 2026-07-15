"""캐싱 저장소 데코레이터 - ReviewRepository를 감쌈"""

import json
from collections.abc import Iterable, Sequence
from dataclasses import asdict
from datetime import datetime
from typing import cast

from steam_rag.domain.interfaces import ReviewRepository
from steam_rag.domain.models import Review
from steam_rag.storage.cache import RedisCache


class CachingReviewRepository:
    """RedisRepository를 감싸고 get_by_appid 결과를 Redis 에 캐싱"""

    def __init__(self, inner: ReviewRepository, cache: RedisCache) -> None:
        # inner: 진짜 저장소(PostgresReviewRepository). 프로토콜 타입이라 무엇이 오든 상관없음
        self._inner = inner
        self._cache = cache

    def save_many(self, reviews: Iterable[Review]) -> int:
        # 쓰기는 캐싱하지 않고 그대로 위임
        return self._inner.save_many(reviews)

    def get_by_appid(self, appid: int, limit: int) -> Sequence[Review]:
        key = f"reviews:{appid}:{limit}"

        cached = self._cache.get(key)
        if cached is not None:
            # 캐시히트: JSON -> dict -> Review 객체
            rows = cast("list[dict[str, object]]", json.loads(cached))
            return [self._from_json(row) for row in rows]

        # 캐시 미스: DB 조회
        reviews = self._inner.get_by_appid(appid=appid, limit=limit)

        # 결과를 JSON 으로 직렬화 후 캐시에 적재
        payload = json.dumps([self._to_json(r) for r in reviews])
        self._cache.set(key, payload)
        return reviews

    @staticmethod
    def _to_json(review: Review) -> dict[str, object]:
        # asdict: dataclass -> dict
        data = asdict(review)
        data["created_at"] = review.created_at.isoformat()
        data["collected_at"] = review.collected_at.isoformat()  # isoformat() → datetime → 문자열
        return data

    @staticmethod
    def _from_json(data: dict[str, object]) -> Review:
        # isoformat 문자열 → datetime 복원 후 Review 재구성
        return Review(
            recommendation_id=int(cast(int, data["recommendation_id"])),
            appid=int(cast(int, data["appid"])),
            author_steamid=str(data["author_steamid"]),
            content=str(data["content"]),
            voted_up=bool(data["voted_up"]),
            playtime_at_review_min=int(cast(int, data["playtime_at_review_min"])),
            votes_helpful=int(cast(int, data["votes_helpful"])),
            created_at=datetime.fromisoformat(str(data["created_at"])),
            collected_at=datetime.fromisoformat(str(data["collected_at"])),  # fromisoformat() → 문자열 → datetime
        )
