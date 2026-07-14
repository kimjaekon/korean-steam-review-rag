"""수집기 수동 검증용 CLI"""

import sys

from steam_rag.config.settings import settings
from steam_rag.ingestion.collectors.steam import SteamReviewCollector


def main() -> None:
    appid = int(sys.argv[1]) if len(sys.argv) > 1 else 570
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    collector = SteamReviewCollector(language=settings.steam_language)
    try:
        for i, review in enumerate(collector.collect(appid, limit), start=1):
            label = "추천" if review.voted_up else "비추천"
            preview = review.content.replace("\n", " ")[:50]
            print(f"[{i}] {label} | {review.playtime_at_review_min}분 | {preview}")
    finally:
        collector.close()


if __name__ == "__main__":
    main()
