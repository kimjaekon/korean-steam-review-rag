"""토픽 이름 생성 - c-TF-IDF 키워드 조각을 LLM으로 문장화"""

from collections.abc import Sequence

from langchain_ollama import ChatOllama  # LangChain의 Ollama 챗 모델 래퍼 (로컬 LLM 호출)

from steam_rag.config.settings import settings
from steam_rag.domain.models import TopicName

_SYSTEM_PROMPT = (
    "너는 게임 리뷰 토픽 분석 결과를 정리하는 도우미다. "
    "주어진 키워드들은 한국어 리뷰에서 글자 단위로 추출돼 조각나 있다. "
    "이 조각들을 보고 해당 토픽이 무엇에 관한 것인지 짧은 한국어 이름(2~6단어)으로만 답하라. "
    "설명·따옴표·마침표 없이 이름만 출력한다."
)


class LLMTopicNamer:
    """TopicNamer 프로토콜 구현"""

    def __init__(self) -> None:
        # ChatOllama: base_url의 Ollama 서버에 model로 요청. 설정은 전부 settings.llm(§6 교체 지점)에서 주입
        self._llm = ChatOllama(
            model=settings.llm.model,
            base_url=settings.llm.base_url,
            num_ctx=settings.llm.num_ctx,
            temperature=0.0,  # 0=결정적(같은 입력→같은 이름). 재현성 위해 고정
        )

    def name_topics(self, appid: int, topics: Sequence[tuple[int, list[str]]]) -> list[TopicName]:
        names: list[TopicName] = []
        for topic_id, keywords in topics:
            if topic_id == -1:  # 이상한 토픽은 이름 안 붙임
                continue

            keywords_str = ", ".join(keywords)
            # invoke(): 메시지 리스트를 LLM에 보내고 응답 1개를 받음.
            #   (role, content) 튜플 형식 — "system"=지시, "human"=사용자 입력
            response = self._llm.invoke([("system", _SYSTEM_PROMPT), ("human", f"키워드: {keywords_str}")])

            # response.content 는 str | list 일 수 있어 str로 정규화 후 공백 제거

            name = str(response.content).strip()

            names.append(TopicName(appid=appid, topic_id=topic_id, name=name, keywords=keywords_str))
        return names
