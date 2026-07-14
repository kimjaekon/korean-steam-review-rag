"""서빙 계층 응답 스키마"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

"""
BaseModel : 타입 검사, JSON 변환, API 응답 직렬화 자동
DTO → dict	model_dump()
DTO → JSON	model_dump_json()

dict → DTO	model_validate()
JSON → DTO	model_validate_json()

dict → JSON	json.dumps()
JSON → dict	json.loads()
"""


class ReviewOut(BaseModel):
    """/reviews/{appid} 한건"""

    model_config = ConfigDict(from_attributes=True)  # 객체의 속성(attribute)을 읽어서 Pydantic 모델을 생성

    recommendation_id: int
    appid: int
    author_steamid: str
    content: str
    voted_up: bool
    playtime_at_review_min: int
    votes_helpful: int
    created_at: datetime
    collected_at: datetime
