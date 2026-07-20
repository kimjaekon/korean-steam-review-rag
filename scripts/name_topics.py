import sys

from steam_rag.etl.analysis.topic import BERTopicAnalyzer
from steam_rag.etl.analysis.topic_namer import LLMTopicNamer
from steam_rag.storage.postgres.repository import PostgresReviewRepository
from steam_rag.storage.postgres.topic_repository import PostgresTopicRepository


def main() -> None:
    appid = int(sys.argv[1]) if len(sys.argv) > 1 else 578080
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 300

    # 1) 리뷰 조회
    reviews = PostgresReviewRepository().get_by_appid(appid=appid, limit=limit)
    print(f"조회: {len(reviews)}개")

    # 2) 토픽 분석
    result = BERTopicAnalyzer().analyze(reviews)
    print(f"토픽: {len(result.topics)}개, 배정된 리뷰: {len(result.assignments)}개")

    # 3) 토픽 키워드만 추려 LLM에 넘길 형태로 변환 ((topic_id, [키워드...]) 리스트)
    #    Topic.keywords 는 (단어, 가중치) 튜플 리스트라 단어만 뽑고 상위 10개로 제한
    topics_for_naming = [(t.topic_id, [w for w, _ in t.keywords[:10]]) for t in result.topics]

    # 4) LLM 이름 생성 (F3.6)
    names = LLMTopicNamer().name_topics(appid, topics_for_naming)
    for n in names:
        print(f"  토픽 {n.topic_id}: {n.name}  ← {n.keywords[:60]}")

    # 5) 저장
    repo = PostgresTopicRepository()
    saved_names = repo.save_many(names)
    saved_assign = repo.save_assignments(result.assignments)
    print(f"저장 - 이름: {saved_names}개, 배정: {saved_assign}개")


if __name__ == "__main__":
    main()
