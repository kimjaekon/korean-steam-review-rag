from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict  # .env 로더 본체 + 설정 객체


class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "steam"
    password: str = "steam"
    name: str = "steam_rag"

    @property  # 메서드를 마치 변수처럼 사용할 수 있게 해주는 데코레이터
    def url(self) -> str:
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class LLMSettings(BaseModel):
    provider: str = "ollama"
    base_url: str = "http://host.docker.internal:11434"
    model: str = "qwen3:14b"
    num_ctx: int = 8192


class RedisSettings(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0  # Redis 논리 DB번호(0~15). 0번을 캐시 용도로 사용
    ttl_seconds: int = 300  # 캐시 만료 시간(초): Time To Live

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"


class Settings(BaseSettings):
    # model_config: 이 BaseSettings 가 "어떻게 값을 읽을지" 규칙을 정함
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",  # DB__HOST → db.host 매핑. 홑밑줄이면 필드명과 충돌해서 겹밑줄 사용
        extra="ignore",  # .env 에 선언 안 한 변수(POSTGRES_* 등)가 있어도 에러 대신 무시
        case_sensitive=False,  # DB__HOST / db__host 둘 다 허용(기본값이지만 명시)
    )

    # 그룹 필드: 각각 정의한 default_factory로 "값 없으면 기본값들로 생성"
    db: DatabaseSettings = DatabaseSettings()
    llm: LLMSettings = LLMSettings()
    redis: RedisSettings = RedisSettings()

    # 최상위 평면 필드: 서로 무관
    vector_backend: str = "pgvector"
    embedding_model: str = "jhgan/ko-sroberta-multitask"  # EMBEDDING_MODEL — 임베딩 모델(768-dim)
    steam_language: str = "koreana"  # STEAM_LANGUAGE — 수집 리뷰 언어 필터
    agent_mode: str = "simple"  # AGENT_MODE — LangChain 단발(한번요청하면 끝) ↔ LangGraph
    sentiment_model: str = "tabularisai/multilingual-sentiment-analysis"  # SENTIMENT_MODEL — 감성 분석 모델(5-class)


settings = Settings()
