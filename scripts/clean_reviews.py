"""정제 수동 검증"""

import sys

from steam_rag.config.settings import settings
from steam_rag.etl.transform import clean_reviews
from steam_rag.ingestion.collectors.steam import SteamReviewCollector

# ingestion: 데이터 수집 및 적재


def main() -> None:
    appid = int(sys.argv[1]) if len(sys.argv) > 1 else 570
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    collector = SteamReviewCollector(language=settings.steam_language)
    try:
        raw = list(collector.collect(appid=appid, limit=limit))
    finally:
        collector.close()

    cleaned = clean_reviews(raw)

    print(f"수집: {len(raw)}개")
    print(f"정제: {len(cleaned)}개 (제거: {len(raw) - len(cleaned)}개)")
    for i, review in enumerate(cleaned[:5], start=1):  # enumerate() 반복하면서 번호를 같이 붙여주는 함수
        preview = review.content.replace("\n", " ")[:50]
        print(f"[{i}] {preview}")


if __name__ == "__main__":
    main()
