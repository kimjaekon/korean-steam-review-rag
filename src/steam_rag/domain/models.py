"""도메인 엔티티: 프로젝트 전체에서 공통으로 사용하는 데이터 형식"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Review:
    """스팀 리뷰 한개"""

    recommendation_id: int
    appid: int
    author_steamid: str
    content: str
    voted_up: bool
    playtime_at_review_min: int
    votes_helpful: int
    created_at: datetime
    collected_at: datetime
