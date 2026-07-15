"""Redis 캐시"""

from functools import cached_property

import redis

from steam_rag.config.settings import settings


class RedisCache:
    """Redis get/set 래퍼. 값은 항상 str"""

    @cached_property
    def client(self) -> redis.Redis:
        return redis.Redis.from_url(settings.redis.url, decode_responses=True)  # decode_responses=True : 바이트가 아니라 str로 받음

    def get(self, key: str) -> str | None:
        value = self.client.get(key)
        return value if value is None else str(value)

    def set(self, key: str, value: str) -> None:  # 시간 만료시 초기화
        self.client.set(key, value, ex=settings.redis.ttl_seconds)
