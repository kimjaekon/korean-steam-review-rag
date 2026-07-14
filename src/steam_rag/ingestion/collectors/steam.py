"""Steam 공개 리뷰 API 수집기"""

import time
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import httpx

from steam_rag.domain.models import Review

_MAX_RETRIES = 3  # 5xx 시 최대 재시도 횟수
_RETRY_BACKOFF = 0.5  # 재시도 간 기본 대기(초) — 점증

_BASE_URL = "https://store.steampowered.com/appreviews/{appid}"
_MAX_PER_PAGE = 100


class SteamReviewCollector:
    """appid로 한국어 리뷰 수집"""

    def __init__(self, language: str, timeout: float = 10.0) -> None:
        self._language = language
        self._client = httpx.Client(timeout=timeout)

    def collect(self, appid: int, limit: int) -> Iterator[Review]:

        cursor = "*"
        seen = 0

        while seen < limit:
            payload = self._fetch_page(appid, cursor)

            if payload.get("success") != 1:
                break
            reviews = payload.get("reviews", [])
            if not reviews:
                break

            for raw in reviews:
                yield self._to_review(appid, raw)
                seen += 1
                if seen >= limit:
                    return

            next_cursor = payload.get("cursor")
            if not next_cursor or next_cursor == cursor:
                break

            cursor = next_cursor

    def _fetch_page(self, appid: int, cursor: str) -> dict[str, Any]:
        """한 페이지를 호출해 JSON을 dict로 반환."""
        # params로 넘기면 httpx가 커서의 =, + 같은 문자를 알아서 URL 인코딩한다.
        params = {
            "json": "1",
            "language": self._language,
            "num_per_page": str(_MAX_PER_PAGE),
            "purchase_type": "all",
            "cursor": cursor,
        }
        url = _BASE_URL.format(appid=appid)

        last_error: httpx.HTTPStatusError | None = None

        for attempt in range(_MAX_PER_PAGE):
            response = self._client.get(url, params=params)
            if response.status_code >= 500:
                last_error = httpx.HTTPStatusError(f"{response.status_code} from Steam", request=response.request, response=response)
                time.sleep(_RETRY_BACKOFF * (attempt + 1))
                continue
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            return data

        # 재시도 횟수 다 쓰고도 실패하면 마지막 에러
        assert last_error is not None
        raise last_error

    def _to_review(self, appid: int, raw: dict[str, Any]) -> Review:
        """Steam 원본 dict4 하나를 도메인 Review 로 반환"""
        author = raw.get("author", {})
        return Review(
            recommendation_id=int(raw["recommendationid"]),
            appid=appid,
            author_steamid=author.get("steamid", ""),
            content=raw.get("review", ""),
            voted_up=raw.get("voted_up", False),
            playtime_at_review_min=author.get("playtime_at_review", 0),
            votes_helpful=raw.get("votes_up", 0),
            created_at=datetime.fromtimestamp(raw["timestamp_created"], tz=UTC),
            collected_at=datetime.now(UTC),
        )

    def close(self) -> None:
        self._client.close()
