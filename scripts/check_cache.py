"""캐시 검증"""

import sys
import time

from steam_rag.storage.cache import RedisCache
from steam_rag.storage.caching_repository import CachingReviewRepository
from steam_rag.storage.postgres.repository import PostgresReviewRepository


def main() -> None:
    appid = int(sys.argv[1]) if len(sys.argv) > 1 else 570
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    repo = CachingReviewRepository(PostgresReviewRepository(), RedisCache())

    # 1회차: 캐시 미스 -> DB 조회 후 적재
    t0 = time.perf_counter()
    first = repo.get_by_appid(appid=appid, limit=limit)
    t1 = time.perf_counter()

    # 2회차: 캐시 히트-> redis에서 반환
    second = repo.get_by_appid(appid=appid, limit=limit)
    t2 = time.perf_counter()

    print(f"1회차(miss→DB): {len(first)}건, {(t1 - t0) * 1000:.1f}ms")
    print(f"2회차(hit→Redis): {len(second)}건, {(t2 - t1) * 1000:.1f}ms")
    print(f"동일 데이터: {[r.recommendation_id for r in first] == [r.recommendation_id for r in second]}")


if __name__ == "__main__":
    main()
