"""저장 수동 검증"""

import sys

from steam_rag.config.settings import settings
from steam_rag.etl.transform import clean_reviews
from steam_rag.ingestion.collectors.steam import SteamReviewCollector
from steam_rag.storage.postgres.repository import PostgresReviewRepository


def main() -> None:
    appid = int(sys.argv[1]) if len(sys.argv) > 1 else 570
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    collector = SteamReviewCollector(language=settings.steam_language)

    try:
        raw = list(collector.collect(appid=appid, limit=limit))
    finally:
        collector.close()

    cleaned = clean_reviews(raw)

    repo = PostgresReviewRepository()
    inserted = repo.save_many(cleaned)

    fetched = repo.get_by_appid(appid=appid, limit=5)

    print(f"수집: {len(raw)}개 → 정제: {len(cleaned)}개")
    print(f"저장: {inserted}개 신규 INSERT (중복은 건너뜀)")
    print(f"조회: appid={appid} 최근 {len(fetched)}개")
    for i, review in enumerate(fetched, start=1):
        preview = review.content.replace("\n", " ")[:50]
        flag = "추천" if review.voted_up else "비추천"
        print(f"[{i}] {flag} {preview}")


if __name__ == "__main__":
    main()
