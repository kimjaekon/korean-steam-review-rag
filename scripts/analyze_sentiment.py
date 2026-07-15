"""감성 분석 실행: 저장된 리뷰 조회 -> 예측 -> 분석 결과 저장"""

import sys

from steam_rag.etl.analysis.sentiment import TransformerSentimentAnalyzer
from steam_rag.storage.postgres.analysis_repository import PostgreAnalysisRepository
from steam_rag.storage.postgres.repository import PostgresReviewRepository


def main() -> None:
    appid = int(sys.argv[1]) if len(sys.argv) > 1 else 570
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    review_repo = PostgresReviewRepository()
    reviews = review_repo.get_by_appid(appid=appid, limit=limit)

    analyzer = TransformerSentimentAnalyzer()
    results = analyzer.analyze(reviews)

    analysis_repo = PostgreAnalysisRepository()
    saved = analysis_repo.save_many(results)

    matched = sum(1 for r in results if r.matches_voted_up)
    print(f"조회:   appid={appid} 리뷰 {len(reviews)}개")
    print(f"분석:   {len(results)}개 예측 완료")
    print(f"저장:   {saved}개 UPSERT (review_analysis)")
    if results:
        rate = matched / len(results) * 100
        print(f"일치율: {matched}/{len(results)} ({rate:.1f}%) — 예측 vs 실제 voted_up")
    for r in results[:5]:
        flag = "일치" if r.matches_voted_up else "불일치"
        print(f"  rec={r.review_recommendation_id} {r.sentiment_label:>13} ({r.sentiment_score:.2f}) [{flag}]")


if __name__ == "__main__":
    main()
