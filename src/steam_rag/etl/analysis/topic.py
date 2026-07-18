"""토픽 분석 파이프라인 - 리뷰를 주제별로 군집화"""

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from bertopic import BERTopic  # 토픽 모델링 라이브러리 (임베딩→UMAP→HDBSCAN→c-TF-IDF를 한번에)
from sklearn.feature_extraction.text import CountVectorizer  # 토픽 '키워드' 뽑을 때 단어를 세는 벡터라이저
from umap import UMAP  # 차원 축소 도구

from steam_rag.config.settings import settings
from steam_rag.domain.models import Review


@dataclass(frozen=True, slots=True)
class Topic:
    """토픽 한개: 번호 + 리뷰 수 + 대표키워드(가중치 포함)"""

    topic_id: int  # -1 은 어느 토픽에도 못 묶인 '이상한 값'
    count: int  # 이 토픽에 속한 리뷰 수
    keywords: list[tuple[str, float]]  # (키워드, c-TF-IDF 가중치), 가중치 내림차순


@dataclass(frozen=True, slots=True)
class TopicResult:
    """분석 산출물: 토픽 목록 + 리뷰별 토픽 배정"""

    topics: list[Topic]
    assignments: dict[int, int]  # recommendation_id -> topic_id , assignments (할당)


class BERTopicAnalyzer:
    """토픽 분석기"""

    def __init__(self, min_topic_size: int = 10) -> None:
        umap_model = UMAP(
            n_neighbors=15,  # 이웃 몇 개를 보고 구조를 잡을지. 표본(리뷰) 수보다 작아야 함
            n_components=5,  # 줄일 목표 차원 수
            min_dist=0.0,  # 점들을 얼마나 촘촘히 모을지(0=최대한 조밀 -> 군집화에 유리)
            metric="cosine",  # 벡터 유사도 거리(임베딩엔 코사인이 표준)
            random_state=42,
        )

        # CountVectorizer(analyzer="char_wb"): 토픽 '키워드'를 뽑을 때 쓰는 벡터라이저.
        #   한국어는 띄어쓰기 기준 단어 분리가 부실해서(교착어), 형태소 분석기(konlpy) 없이
        #   글자 단위 n-gram 으로 하위 단어를 잡는다. char_wb = 단어 경계 안에서만 글자 n-gram 생성.
        vectorizer_model = CountVectorizer(
            analyzer="char_wb",  # 단어 경계 내 글자 n-gram (기본값 "word" 대신)
            ngram_range=(2, 4),  # 2~4글자 조합을 키워드 후보로
            min_df=1,  # 최소 2개 리뷰에 등장한 조합만(희귀 노이즈 제거)
        )

        # BERTopic: 위 부품들을 조립
        self._model = BERTopic(
            embedding_model=settings.embedding_model,  # ko-sroberta(한국어 문장 임베딩, 768-dim)
            umap_model=umap_model,
            vectorizer_model=vectorizer_model,
            min_topic_size=min_topic_size,  # 이 수보다 작은 군집은 토픽으로 인정 안 함
            calculate_probabilities=False,  # 리뷰별 소속 확률은 안 씀 → 계산 아껴 속도↑
            verbose=True,
        )

    def analyze(self, reviews: Sequence[Review]) -> TopicResult:
        # content 가 비었거나 문자열이 아닌 리뷰는 걸러냄 (BERTopic 은 문자열만 받음)
        pairs = [(r.recommendation_id, r.content) for r in reviews if isinstance(r.content, str) and r.content.strip()]
        docs = [content for _, content in pairs]

        topic_ids, _ = self._model.fit_transform(docs)

        counts = Counter(int(t) for t in topic_ids)

        topics: list[Topic] = []
        for tid, words in self._model.get_topics().items():
            keywords = [(str(w), float(s)) for w, s in (words or [])]
            topics.append(Topic(topic_id=int(tid), count=counts.get(int(tid), 0), keywords=keywords))

        assignments = {rec_id: int(tid) for (rec_id, _), tid in zip(pairs, topic_ids, strict=True)}
        return TopicResult(topics=topics, assignments=assignments)
