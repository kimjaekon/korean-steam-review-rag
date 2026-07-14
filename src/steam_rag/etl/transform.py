"""수집된 리뷰 빈 리뷰, 중복제거"""

from collections.abc import Iterable
from dataclasses import asdict

import pandas as pd

from steam_rag.domain.models import Review


def clean_reviews(reviews: Iterable[Review]) -> list[Review]:
    # rows = [vars(r) for r in reviews]  # vars() : 객체의 속성을 딕셔너리로 반환하는 함수 , slots=True에서는 사용할 수 없음
    rows = [asdict(r) for r in reviews]  # asdict() : dataclass 객체를 딕셔너리(dict)로 변환하는 함수,
    if not rows:
        return []

    df = pd.DataFrame(rows)

    content_ok = df["content"].str.strip().str.len() > 0
    df = df[content_ok]

    df = df.drop_duplicates(subset="recommendation_id", keep="first")

    # orient="records" : DataFrame의 각 행을 하나의 딕셔너리로 만들어 리스트로 담기
    return [Review(**row) for row in df.to_dict(orient="records")]
