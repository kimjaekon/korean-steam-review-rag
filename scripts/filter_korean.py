"""언어 필터 수동 검증"""

import sys

from steam_rag.config.settings import settings
from steam_rag.etl.language import filter_korean
from steam_rag.etl.transform import clean_reviews
from steam_rag.ingestion.collectors.steam import SteamReviewCollector


def main() -> None:
    appid = int(sys.argv[1]) if len(sys.argv) > 1 else 570
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    collector = SteamReviewCollector(language=settings.steam_language)
    try:
        raw = list(collector.collect(appid, limit))
    finally:
        collector.close()

    cleaned = clean_reviews(raw)
    korean = filter_korean(cleaned)

    print(f"수집:   {len(raw)}개")
    print(f"정제:   {len(cleaned)}개 (제거: {len(raw) - len(cleaned)}개)")
    print(f"한국어: {len(korean)}개 (제외: {len(cleaned) - len(korean)}개)")

    dropped = [r for r in cleaned if r not in korean]

    for i, review in enumerate(dropped[:5], start=1):
        preview = review.content.replace("\n", " ")[:50]
        print(f"[제외 {i}] {preview}")


if __name__ == "__main__":
    main()
