"""토픽이름 + 리뷰별 토픽 저장소"""

from collections.abc import Iterable

from sqlalchemy.dialects.postgresql import insert as pg_insert

from steam_rag.domain.models import TopicName
from steam_rag.storage.postgres.models import ReviewTopicORM, TopicNameORM
from steam_rag.storage.postgres.session import SessionLocal


class PostgresTopicRepository:
    """TopicRepository 프로토콜 구현 — topic_names·review_topic 두 테이블 UPSERT"""

    def save_many(self, names: Iterable[TopicName]) -> int:
        rows = [self._name_to_mapping(n) for n in names]
        if not rows:
            return 0

        stmt = pg_insert(TopicNameORM).values(rows)

        upsert = stmt.on_conflict_do_update(index_elements=["appid", "topic_id"], set_={"name": stmt.excluded.name, "keywords": stmt.excluded.keywords}).returning(TopicNameORM.topic_id)

        with SessionLocal.begin() as session:
            result = session.execute(upsert)
            return len(result.fetchall())

    def save_assignments(self, assignments: dict[int, int]) -> int:

        rows = [{"review_recommendation_id": int(rec_id), "topic_id": int(tid), "keywords": "", "weight": 1.0} for rec_id, tid in assignments.items() if tid != -1]
        if not rows:
            return 0

        stmt = pg_insert(ReviewTopicORM).values(rows)

        upsert = stmt.on_conflict_do_update(index_elements=["review_recommendation_id", "topic_id"], set_={"keywords": stmt.excluded.keywords, "weight": stmt.excluded.weight}).returning(
            ReviewTopicORM.topic_id
        )

        with SessionLocal.begin() as session:
            result = session.execute(upsert)
            return len(result.fetchall())

    @staticmethod
    def _name_to_mapping(name: TopicName) -> dict[str, object]:
        return {"appid": int(name.appid), "topic_id": int(name.topic_id), "name": name.name, "keywords": name.keywords}
