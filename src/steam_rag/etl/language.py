"""수집된 리뷰 중 한국어 2차 필터링"""

from collections.abc import Iterable

from langdetect import DetectorFactory, detect
from langdetect.lang_detect_exception import LangDetectException

from steam_rag.domain.models import Review

# langdetect는 확률 기반: SEED 고정
DetectorFactory.seed = 0

_KOREAN = "ko"


def is_korean(text: str) -> bool:
    """한국어인가?"""
    try:
        data: bool = detect(text) == _KOREAN
        return data
    except LangDetectException:
        return False


def filter_korean(reviews: Iterable[Review]) -> list[Review]:
    """한국어 리뷰만 남김"""
    return [review for review in reviews if is_korean(review.content)]
