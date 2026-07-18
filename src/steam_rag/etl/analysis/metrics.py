"""퍙가지표 계산 + 임계값 스윕(훑다): 감성점수를 voted_up으로 검증하고 최적 임계값 찾음"""

from collections.abc import Sequence
from dataclasses import dataclass

from sklearn.metrics import balanced_accuracy_score, confusion_matrix, precision_recall_fscore_support

"""
balanced_accuracy_score             : 클래스 불균형을 고려한 정확도 계산    : float
confusion_matrix                    : 실제값과 예측값을 표 형태로 비교	    : ndarray
precision_recall_fscore_support	    : Precision, Recall, F1-score 계산	: (precision, recall, f1, support)
"""


@dataclass(frozen=True, slots=True)
class ThresholdMetrics:
    """한 임계값에서의 평과 결과"""

    threshold: float
    balanced_accuracy: float
    f1: float
    # confusion matrix 4칸
    true_negative: int  # 실제 비추천 -> 비추천 예측 (정답)
    false_positive: int  # 실제 비추천 -> 추천 예측 (오답)
    false_negative: int  # 실제 추천 -> 비추천 예측 (오답)
    true_positive: int  # 실제 추천 -> 추천 예측 (정답)


def evaluate_at_threshold(scores: Sequence[float], voted_up: Sequence[bool], threshold: float) -> ThresholdMetrics:
    """점수를 임계값으로 이진화 한뒤 지표 계산"""
    y_pred = [s >= threshold for s in scores]  # 점수를 True False 로 변환
    y_true = list(voted_up)  # 실제 정답

    bal = balanced_accuracy_score(y_true, y_pred)  # 추천 맞춘 비율, 비추천 맞춘 비율로 계산해서 평균냄
    # average='binary' : True(추천) 를 양성(Positive)으로 보고 F1을 계산
    # zero_division=0.0 : 예측이 전부 False 처럼 Precision을 계산할 수 없는 경우 에러 대신 0.0 반환
    _, _, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0.0)  # f1 점수계산 (Precision, Recall, F1, Support )

    # confusion_matrix(labels=[False, True]): 2x2 순서를 고정 (라벨이 한쪽뿐일 때도 형태 보장)
    cm = confusion_matrix(y_true, y_pred, labels=[False, True])  #
    (tn, fp), (fn, tp) = cm

    return ThresholdMetrics(threshold=threshold, balanced_accuracy=float(bal), f1=float(f1), true_negative=int(tn), false_positive=int(fp), false_negative=int(fn), true_positive=int(tp))


def sweep_thresholds(scores: Sequence[float], voted_up: Sequence[bool], candidates: Sequence[float]) -> list[ThresholdMetrics]:
    """여러 임계갑 후보를 훑어 각각의 지표를 계산"""
    return [evaluate_at_threshold(scores, voted_up, t) for t in candidates]


def best_by_balanced_accuracy(results: Sequence[ThresholdMetrics]) -> ThresholdMetrics:
    """balanced accuracy가 가장 높은 임계값 결과를 고른다."""
    return max(results, key=lambda m: m.balanced_accuracy)
