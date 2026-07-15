"""수집 파이프라인 실행"""

import sys

from steam_rag.config.settings import settings
from steam_rag.etl.pipeline import ingest_reviews
from steam_rag.ingestion.collectors.steam import SteamReviewCollector
from steam_rag.storage.postgres.repository import PostgresReviewRepository


def main() -> None:
    appid = int(sys.argv[1]) if len(sys.argv) > 1 else 570
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    collector = SteamReviewCollector(language=settings.steam_language)
    repository = PostgresReviewRepository()

    try:
        result = ingest_reviews(collector=collector, repository=repository, appid=appid, limit=limit)
    finally:
        collector.close()

    print(f"수집:   {result.collected}개")
    print(f"정제:   {result.cleaned}개 (제거: {result.collected - result.cleaned}개)")
    print(f"한국어: {result.korean}개 (제외: {result.cleaned - result.korean}개)")
    print(f"저장:   {result.saved}개 신규 INSERT (중복은 건너뜀)")


if __name__ == "__main__":
    main()
