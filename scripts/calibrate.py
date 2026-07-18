"""임계값 보정 실행 리뷰 조회 → 감성 예측 → train/test 분할 → 최적 임계값 탐색 → test 검증"""

import sys

from steam_rag.etl.analysis.metrics import (
    ThresholdMetrics,
    best_by_balanced_accuracy,
    evaluate_at_threshold,
    sweep_thresholds,
)
from steam_rag.etl.analysis.sentiment import TransformerSentimentAnalyzer
from steam_rag.etl.analysis.split import stratified_split
from steam_rag.storage.postgres.repository import PostgresReviewRepository


def _print_row(m: ThresholdMetrics, marker: str = "") -> None:
    print(f"   {m.threshold:.2f}    {m.balanced_accuracy:.3f}{m.f1:.3f}[tn={m.true_negative} fp={m.false_positive}fn={m.false_negative} tp]{m.true_positive}]{marker}")


def main() -> None:
    appid = int(sys.argv[1]) if len(sys.argv) > 1 else 570
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 200

    # 1) 저장된 리뷰 조회
    repo = PostgresReviewRepository()
    reviews = repo.get_by_appid(appid=appid, limit=limit)
    print(f"조회: appid={appid} 리뷰 {len(reviews)}개")

    # 2) train/test 게층 분할 (votes_up 비율 유지)
    train, test = stratified_split(reviews, test_size=0.3, random_state=42)
    print(f"분할: train {len(train)}개  /  test {len(test)}개")

    # 3) 감성 예측 - train/test 각각 점수화
    analyzer = TransformerSentimentAnalyzer()
    train_results = analyzer.analyze(train)
    test_results = analyzer.analyze(test)

    train_scores = [r.sentiment_score for r in train_results]
    train_voted = [rv.voted_up for rv in train]

    test_scores = [r.sentiment_score for r in test_results]
    test_voted = [rv.voted_up for rv in test]

    # 4) train 에서만 최적 임게값 탐색 (0.30 ~ 0.70, 0.05 간격)
    candidates = [0.30 + 0.05 * i for i in range(9)]
    train_sweep = sweep_thresholds(train_scores, train_voted, candidates)
    best = best_by_balanced_accuracy(train_sweep)

    print("\n[train] 임계값 스윕")
    print("  thr        bal_acc       f1")
    for m in train_sweep:
        marker = "   <- best" if m.threshold == best.threshold else ("   (기존 0.5)" if m.threshold == 0.50 else "")
        _print_row(m, marker)

    # 한번도 안본 test에서 그 임계값이 통하는지 최종 검증
    test_at_best = evaluate_at_threshold(test_scores, test_voted, best.threshold)
    test_at_half = evaluate_at_threshold(test_scores, test_voted, 0.50)

    print("\n[test] 최종 검증 (train에서 고른 임계값을 처음 보는 데이터에 적용)")
    print("  thr        bal_acc       f1")
    _print_row(test_at_half, "   (기존 0.5)")
    _print_row(test_at_best, "   ← 선택된 임계값")

    print(f"\n결론:   최적 임계값 {best.threshold:.2f} (train bal_acc {best.balanced_accuracy:.3f}) → test bal_acc {test_at_best.balanced_accuracy:.3f}")


if __name__ == "__main__":
    main()
