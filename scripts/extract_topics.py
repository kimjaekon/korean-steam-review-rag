"""토픽 분석 실행: 저장된 리뷰 조회 -> BERTopic 군집화 -> 토픽·키워드 출력"""

import sys

from steam_rag.etl.analysis.topic import BERTopicAnalyzer
from steam_rag.storage.postgres.repository import PostgresReviewRepository


def main() -> None:
    appid = int(sys.argv[1]) if len(sys.argv) > 1 else 578080
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 300  # 토픽은 감성보다 표본이 더 필요

    review_repo = PostgresReviewRepository()
    reviews = review_repo.get_by_appid(appid=appid, limit=limit)

    analyzer = BERTopicAnalyzer(min_topic_size=5)  # 군집 최소 크기 — 이 knob 을 줄이면 토픽이 더 잘게 쪼개짐
    result = analyzer.analyze(reviews)

    # 토픽 번호 오름차순 정렬, -1(이상치)은 맨 뒤로
    topics = sorted(result.topics, key=lambda t: (t.topic_id == -1, t.topic_id))
    real = sum(1 for t in topics if t.topic_id != -1)

    print(f"조회:   appid={appid} 리뷰 {len(reviews)}개")
    print(f"토픽:   {real}개 (이상치 -1 제외)")
    for t in topics:
        head = ", ".join(w for w, _ in t.keywords[:6])  # 대표 키워드 6개
        tag = "이상치" if t.topic_id == -1 else f"토픽 {t.topic_id}"
        print(f"  [{tag}] 리뷰 {t.count}개 | {head}")


if __name__ == "__main__":
    main()
