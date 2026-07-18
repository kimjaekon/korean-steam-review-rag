"""계층 분할: 추천/비추천 비율을 유지하며 train/test 나눔"""

from collections.abc import Sequence

from sklearn.model_selection import train_test_split

from steam_rag.domain.models import Review


def stratified_split(reviews: Sequence[Review], test_size: float = 0.3, random_state: int = 42) -> tuple[list[Review], list[Review]]:
    """리뷰를 train/test 계층 분할, voted_up 비율을 양쪽에 동일하게 유지"""
    labels = [r.voted_up for r in reviews]

    # stratify=labels: 이 라벨 비율을 train/test 양쪽에 똑같이 유지
    train, test = train_test_split(reviews, test_size=test_size, stratify=labels, random_state=random_state)
    return train, test
