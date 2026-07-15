from collections.abc import Iterable, Sequence

# Iterable : 반복가능객체
# Sequence : 순서가 있으면서 반복가능 객체
from typing import Protocol, runtime_checkable

# Protocol: 메서드들을 구현하면 된다는 약속
# 구현체는 Protocol을 import하거나 상속하지 않아도 되고, 메서드의 이름과 매개변수, 반환형(시그니처)만 맞으면 됨
from steam_rag.domain.models import Review, SentimentResult


@runtime_checkable  # 파이썬 실행 중(isinstance, issubclass)에도 검사할 수 있게 해주는 옵션
class ReviewCollector(Protocol):
    """리뷰 수집"""

    def collect(self, appid: int, limit: int) -> Iterable[Review]: ...


@runtime_checkable
class ReviewRepository(Protocol):
    """리뷰 저장소"""

    def save_many(self, reviews: Iterable[Review]) -> int: ...

    def get_by_appid(self, appid: int, limit: int) -> Sequence[Review]: ...


@runtime_checkable
class SentimentAnalyzer(Protocol):
    """감성 분석기"""

    def analyze(self, review: Iterable[Review]) -> list[SentimentResult]: ...


@runtime_checkable
class AnalysisRepository(Protocol):
    """분석 결과 저장소"""

    def save_many(self, results: Iterable[SentimentResult]) -> int: ...
