"""감정(sentiment) 분석 파이프라인"""

from collections.abc import Iterable

from transformers import pipeline

from steam_rag.config.settings import settings
from steam_rag.domain.models import Review, SentimentResult

# 모델이 돌려주는 5개 라벨 -> 점수(0.0 ~ 1.0)
# 가장 부정 = 0, 가장 긍정 = 1
_LABEL_TO_SCORE = {"Very Negative": 0.0, "Negative": 0.25, "Neutral": 0.5, "Positive": 0.75, "Very Positive": 1.0}

# 점수 >= 0.5 를 "추천 예측"
_POSITIVE_THRESHOLD = 0.5


class TransformerSentimentAnalyzer:
    """SentimentAnalyzer 프로토콜 구현"""

    def __init__(self, model_name: str | None = None) -> None:
        # pipeline(task, model): Hugging Face pipeline()이 내부적으로 전처리·추론·후처리를 한번에 처리해줌
        # 모델은 최초 호출 시 Hugging Face Hub에서 자동 다운로드 후 캐시.
        self._pipe = pipeline(
            task="text-classification",
            model=model_name or settings.sentiment_model,
            truncation=True,  # # 모델 최대 토큰 초과 리뷰를 잘라 넣음(긴 리뷰 방어)
        )

    def analyze(self, reviews: Iterable[Review]) -> list[SentimentResult]:
        review_list = list(reviews)
        if not review_list:
            return []

        texts = [r.content for r in review_list]

        # 파이프라인에 리스트를 넘기면 배치로 처리. 결과는 리뷰당 dict 하나: {"label": "Positive", "score": 0.98}  ← score는 그 라벨의 확신도
        outputs = self._pipe(texts)

        results: list[SentimentResult] = []
        """
        enumerate()	인덱스(번호)를 붙여준다.	몇 번째인지 필요할 때
        zip()	    여러 리스트를 묶어준다.	    여러 데이터를 동시에 순회할 때
        """
        for review, output in zip(review_list, outputs, strict=True):  # Strict 엄격하게
            label = output["label"]
            score = _LABEL_TO_SCORE[label]
            predicted_up = score >= _POSITIVE_THRESHOLD

            results.append(SentimentResult(review_recommendation_id=review.recommendation_id, sentiment_score=score, sentiment_label=label, matches_voted_up=(predicted_up == review.voted_up)))
        return results
