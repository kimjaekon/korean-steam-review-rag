# 개발 로드맵 — 수직 슬라이스 실행 계획

> 이 문서는 [`ARCHITECTURE.md`](./ARCHITECTURE.md)에서 확정한 청사진을 **"무엇을 어떤 순서로 만드는가"**로 푼 실행 계획입니다.
> 아키텍처가 *구조*(무엇이 어디에 있는가)라면, 이 로드맵은 *순서*(무엇을 먼저 만드는가)입니다.

---

## 0. 로드맵을 읽는 법

### 개발 방식: 수직 슬라이스 (Vertical Slice)

계층을 하나씩 완성(수집 전부 → 저장 전부 → …)하지 않고, **모든 계층을 관통하는 얇은 기능 하나**를 먼저 끝냅니다. 그래서 **1일차부터 end-to-end가 동작**하고, 커밋마다 "돌아가는 제품"이 남습니다.

> **용어**: **수직 슬라이스**(vertical slice = 세로로 얇게 자르기) — "리뷰 1개가 수집돼 API로 나온다"처럼 여러 층을 관통하는 얇은 기능 하나를 먼저 완성하는 방식. **end-to-end**(E2E = 끝에서 끝까지) — 시작(수집)부터 끝(응답)까지 전 과정이 실제로 이어져 동작하는 것.

### 매 기능(feature)은 9단계로

각 슬라이스는 여러 기능으로 쪼개지고, **각 기능**을 아래 9단계로 만듭니다. 이 리듬이 학습의 뼈대입니다.

1. **목적 설명** — 이번 기능이 무엇을 하는가.
2. **왜 필요한지** — 이 기능이 없으면 무엇이 안 되는가.
3. **파일 설계** — 어떤 파일을 만들고 각각 무슨 역할인가.
4. **디렉터리 생성** — 폴더·빈 파일 만들기 (스캐폴딩).
5. **코드 작성** — 직접 타이핑할 수 있도록 전체 코드 제시.
6. **코드 해설** — 블록 단위로 무슨 일을 하는지. **라이브러리를 쓸 땐 "이 라이브러리의 이 기능을 이렇게 쓴다"를 중심으로** (원칙 4).
7. **실행 테스트** — 실제로 돌려서 동작 확인 (보통 `scripts/`의 진입점으로).
8. **Git 커밋** — 의미 있는 커밋 메시지로 저장.
9. **README 백업 후 업데이트** — 기존 README를 `backup/README_NN.md`로 백업한 뒤 진행 상황·사용법 반영 → 다음 기능으로.

### 설계 4원칙 (모든 기능이 지킴)

1. **교체 가능성** — 저장소·LLM·수집기는 인터페이스 뒤에 숨긴다.
2. **계층 격리** — 도메인은 FastAPI도 PostgreSQL도 모른다.
3. **항상 동작** — 매 단계 끝에 `docker compose up` 하면 전체가 돈다.
4. **라이브러리 우선** — 검증된 라이브러리가 하는 일을 손으로 재구현하지 않는다. **라이브러리 쓰는 법을 익히며 소스를 채운다.**

### 진행 상태 표기

- ⬜ 예정  🟦 진행 중  ✅ 완료
- 상태는 실제 진행에 맞춰 갱신하고, **README의 "현재 진행 상황" 섹션을 세션 간 연속성의 기준(single source of truth)**으로 삼습니다.

---

## 전체 슬라이스 지도

| 슬라이스 | 이름 | 핵심 산출 | 상태 |
|---|---|---|---|
| **0** | 뼈대 (Skeleton) | venv·requirements·docker-compose(Postgres)·설정 로더·CI 뼈대 | ⬜ |
| **1** | 얇은 관통 (Walking Skeleton) ★ | 리뷰 1개 수집 → 저장 → API 조회 | ⬜ |
| **2** | 저장 계층 정식화 | SQLAlchemy·Alembic·Repository·Redis 캐시 | ⬜ |
| **3** | 분석 파이프라인 | 언어필터·감성·토픽·피처·GX 검증 | ⬜ |
| **4** | AI/RAG (LangChain) ★★ | 임베딩·pgvector·LLM 추상·단발 RAG·추천 | ⬜ |
| **5** | LangGraph 에이전트 ★★★ | 상태머신·조건분기·루프·모드 토글 | ⬜ |
| **6** | 스트리밍 & 오케스트레이션 | Kafka·Airflow·Spark | ⬜ |
| **7** | 검색 & 모니터링 | Elasticsearch·Prometheus·Grafana | ⬜ |
| **8** | 프로덕션 마감 | 테스트·pre-commit·CI/CD·배포·문서 | ⬜ |

★ = 하이라이트. Slice 1(뼈대 검증)·Slice 4(RAG)·Slice 5(에이전트)가 포트폴리오의 핵심 서사입니다.

---

## Slice 0 — 뼈대 (Skeleton)

**목표**: 빈 FastAPI가 뜨고, Postgres 컨테이너가 붙고, 개발 도구(Ruff·mypy)가 동작하는 최소 골격.

### 환경 부트스트랩 (PowerShell)

```powershell
winget install --id=Python.Python.3.13 -e     # 파이썬 3.13 (없으면 한 번만)
python -m venv .venv                            # 가상환경 생성
.\.venv\Scripts\Activate.ps1                    # 활성화 (PATH·VIRTUAL_ENV 설정)
python -m pip install --upgrade pip             # pip 최신화
pip install -r requirements.txt                 # 런타임 의존성
pip install -r requirements-dev.txt             # 개발 의존성
uvicorn steam_rag.serving.api.main:app --reload # 실행
```

### 기능

- ⬜ **F0.1 프로젝트 구조 + 패키징** — `pyproject.toml`(Ruff·mypy 설정), `requirements.txt`/`requirements-dev.txt`(버전 핀 고정), `.vscode/`(인터프리터·저장 시 Ruff).
- ⬜ **F0.2 Docker Compose (Postgres)** — pgvector 이미지로 Postgres 컨테이너. `docker-compose.yml` + `.override.yml`.
- ⬜ **F0.3 설정 로더** — `config/settings.py` (Pydantic Settings로 `.env` 로드). `.env.example` 작성.
- ⬜ **F0.4 FastAPI 뼈대 + `/health`** — `serving/api/main.py`.
- ⬜ **F0.5 Invoke 태스크 + CI 뼈대** — `tasks.py`(up·test·lint), GitHub Actions 최소 워크플로.

**완료 기준**: `docker compose up`(Postgres) + `uvicorn ...` → 빈 `/health` 응답. VSCode가 `.venv\Scripts\python.exe`를 인식하고 Ruff가 저장 시 동작.

**산출 파일**: `pyproject.toml` · `requirements*.txt` · `.vscode/*` · `docker-compose.yml` · `config/settings.py` · `serving/api/main.py` · `tasks.py`

---

## Slice 1 — 얇은 관통 (Walking Skeleton) ★ 가장 중요

**목표**: 리뷰 하나가 수집돼 API로 나온다. Kafka·Spark·RAG 없음. **이게 통과하면 전체 아키텍처 뼈대가 검증된 것.**

### 기능

- ⬜ **F1.1 도메인 모델 + 인터페이스** — `domain/models.py`(`Review` 엔티티), `domain/interfaces.py`(`ReviewCollector`·`ReviewRepository` 프로토콜). **프레임워크 import 0.**
- ⬜ **F1.2 Steam 수집기** — `ingestion/collectors/steam.py` (`httpx`로 공개 엔드포인트 호출, 커서 페이지네이션, 원본 dict → `Review` 변환).
- ⬜ **F1.3 최소 정제** — `etl/transform.py` (Pandas로 빈 리뷰·중복 제거).
- ⬜ **F1.4 Postgres 저장 (raw)** — `storage/postgres/repository.py` 초판 (psycopg raw SQL로 INSERT/조회 — Slice 2에서 SQLAlchemy로 정식화).
- ⬜ **F1.5 조회 API** — `serving/api/main.py`에 `GET /reviews/{appid}`, `serving/schemas.py`(`ReviewOut`).

> **첫 데이터 소스**: `https://store.steampowered.com/appreviews/<appid>?json=1&language=koreana&num_per_page=100&cursor=*` — API 키 없이 수집 가능. 페이지네이션은 응답의 `cursor`를 다음 요청에 넘김.

**데이터 흐름**: `httpx 수집 → dict → Review → 정제 → Postgres INSERT → GET /reviews/{appid} → JSON 응답`

**완료 기준**: 특정 게임(appid)의 한국어 리뷰가 수집돼 DB에 저장되고, `GET /reviews/{appid}`로 조회된다.

**라이브러리 우선**: 수집은 `httpx`(HTTP 클라이언트), 정제는 Pandas를 씀. Steam 전용 API라 수집기 자체는 직접 작성(대체 라이브러리 없음).

---

## Slice 2 — 저장 계층 정식화

**목표**: 저장소가 인터페이스 뒤로 숨고, 마이그레이션으로 스키마를 버전 관리하고, 캐시가 붙는다.

### 기능

- ⬜ **F2.1 SQLAlchemy ORM** — `storage/postgres/models.py`(`ReviewORM`·`DeclarativeBase`), `storage/postgres/session.py`(`SessionLocal`).
- ⬜ **F2.2 Alembic 마이그레이션** — `alembic/`(env.py·versions), 첫 마이그레이션으로 `reviews` 테이블 생성.
- ⬜ **F2.3 Repository 패턴** — `storage/postgres/repository.py`를 `PostgresReviewRepository`로 리팩터 (raw psycopg → SQLAlchemy). `domain/interfaces.py`의 추상 뒤로 숨김.
- ⬜ **F2.4 Redis 캐시** — `storage/cache.py`(`RedisCache`, `cached_property`), `storage/caching_repository.py`(`CachingReviewRepository` 데코레이터 — 조회 결과 캐싱).

**완료 기준**: 저장소가 `ReviewRepository` 인터페이스 뒤에 숨고, 환경변수로 저장 백엔드(로컬 Postgres↔RDS)를 갈아끼운다. Alembic으로 스키마 변경이 코드로 남는다.

**산출 파일**: `storage/postgres/{models,session,repository}.py` · `storage/{cache,caching_repository}.py` · `alembic/versions/*`

> **왜 Alembic**: `create_all()`은 최초 생성만 가능하고 컬럼 추가·변경을 못 함. Alembic은 DB 구조 변경을 Git처럼 버전 관리 — 특히 다음 슬라이스의 pgvector 확장·`vector(768)`·HNSW 인덱스를 `op.execute()`로 명시적으로 넣을 때 필수.

---

## Slice 3 — 분석 파이프라인

**목표**: 저장된 리뷰에 감성·토픽·피처 메타데이터가 붙고, 감성 예측을 실제 추천 라벨과 비교한 정확도가 나온다.

### 기능

- ⬜ **F3.1 한국어 언어 필터** — `etl/language.py` (`langdetect`, `DetectorFactory.seed=0`으로 재현성).
- ⬜ **F3.2 수집 파이프라인 오케스트레이션** — `etl/pipeline.py` (`ingest_reviews()`: collector→clean→filter→save를 하나로 꿴다). 실행: `scripts/produce_reviews.py`.
- ⬜ **F3.3 감성 분석** — `etl/analysis/sentiment.py` (`transformers`, `tabularisai/multilingual-sentiment-analysis`, 5-class). 저장: `storage/postgres/analysis_repository.py`(`ON CONFLICT DO UPDATE`). 실행: `scripts/analyze_sentiment.py`.
- ⬜ **F3.4 평가지표 + 임계값 보정** — `etl/analysis/metrics.py`(**scikit-learn**: `confusion_matrix`·`balanced_accuracy_score`·`precision_recall_fscore_support`), `etl/analysis/split.py`(**scikit-learn**: `train_test_split(stratify=...)`). 실행: `scripts/calibrate.py`.
- ⬜ **F3.5 토픽 분석** — `etl/analysis/topic.py` (BERTopic + UMAP + `char_wb` 벡터라이저). 실행: `scripts/extract_topics.py`.
- ⬜ **F3.6 토픽 이름 생성** — `etl/analysis/topic_namer.py` (LLM으로 c-TF-IDF 키워드 → 사람이 읽는 이름). 저장: `storage/postgres/topic_repository.py`(UPSERT, 복합 PK). 실행: `scripts/name_topics.py`.
- ⬜ **F3.7 피처 추출** — `etl/analysis/features.py` (플레이타임 사분위 등 → `review_analysis.features` JSONB). 실행: `scripts/extract_features.py`.
- ⬜ **F3.8 Great Expectations 검증** — `etl/validation/{expectations,runner,report}.py` (ephemeral context, YAML 없음). 실행: `scripts/validate_data.py`.

**완료 기준**: 리뷰에 감성/토픽/피처가 붙고, 감성 예측 vs 실제 `voted_up`을 비교한 정확도 지표(balanced accuracy·F1)가 나온다. GX 검증이 데이터 불변식을 코드로 고정한다.

**라이브러리 우선**: 감성은 `transformers`, 토픽은 BERTopic, 평가·분할은 **scikit-learn**, 검증은 Great Expectations. **손으로 짜지 않고 각 라이브러리 사용법을 익히는 데 집중.**

> **도메인 강점**: 스팀 리뷰엔 "추천/비추천" 정답 라벨이 이미 있어, 감성 모델을 **정량 검증**할 수 있음. `matches_voted_up`으로 예측 일치 여부를 저장해 Slice 7 대시보드에서 관측.

---

## Slice 4 — AI/RAG (LangChain) ★★ 두 번째 하이라이트

**목표**: "이 게임 최근 한국어 여론 브리핑" 질의 → 요약 + 근거 리뷰. 별도로 유사 게임 추천. **로컬 GPU에서 동작.**

### 기능

- ⬜ **F4.1 임베딩 생성** — `ai/embedding.py` (`sentence-transformers` · `ko-sroberta-multitask`, 768-dim). pgvector 확장·`vector(768)`·HNSW 인덱스 마이그레이션. 저장: `storage/vector/repository.py`(`PgVectorRepository`, `cosine_distance`). 실행: `scripts/embed_reviews.py`.
- ⬜ **F4.2 LLM 추상 계층** — `ai/llm/base.py`(`LLMProvider` 추상 + `LLMError`), `ai/llm/ollama.py`(**langchain-ollama** `ChatOllama`), `ai/llm/anthropic.py`(**langchain-anthropic** `ChatAnthropic`), `ai/llm/factory.py`(`LLM_PROVIDER`로 분기 — 유일한 분기점).
- ⬜ **F4.3 토픽 이름 소비** — RAG 컨텍스트에 토픽 이름을 얹는 연결 (F3.6 산출을 읽음).
- ⬜ **F4.4 단발 RAG 파이프라인** — `ai/rag.py` (**LangChain**: retriever·`PromptTemplate`·LCEL 체인). 질의 임베딩 → pgvector 검색 → 프롬프트 조립 → LLM 생성. **부채 방어**: 인용 리뷰에 `created_at`·`playtime_quartile` 병기(HNSW 시간 무지 드러내기). 실행: `scripts/brief.py`.
- ⬜ **F4.5 크로스 게임 추천** — `ai/recommend.py` (`CrossGameRecommender`: seed 게임 임베딩 centroid → 다른 게임과 유사도 비교 → top-N). 실행: `scripts/recommend.py`.
- ⬜ **F4.6 서빙 연결** — `serving/api/main.py`에 `POST /brief`·`GET /recommend`, `serving/api/dependencies.py`(의존성 주입).

**데이터 흐름 (브리핑)**: `질의 → 임베딩 → pgvector top-k 검색 → 토픽 이름 + 근거 리뷰로 프롬프트 조립 → LLM 생성 → 브리핑 + 근거`

**완료 기준**: `POST /brief`가 여론 브리핑 + 근거 리뷰를 반환하고, `GET /recommend`가 유사 게임을 반환. 로컬 Ollama(qwen3:14b)로 동작하며 `LLM_PROVIDER=anthropic`으로 Claude 폴백 전환 가능.

**라이브러리 우선**: RAG 조립·LLM 호출을 raw HTTP로 손구현하지 않고 **LangChain**(`langchain`·`langchain-ollama`·`langchain-anthropic`)의 기성 부품으로. 단, LLM은 `LLMProvider` 도메인 인터페이스 뒤에 감싸 교체 가능성 유지(원칙 1·2).

---

## Slice 5 — LangGraph 에이전트 ★★★ 세 번째 하이라이트

**목표**: 검색이 부실하면 스스로 쿼리를 재작성해 재검색하는 **반복형 에이전트**. 단발 RAG(Slice 4)와 토글로 전환.

### 기능

- ⬜ **F5.1 상태 스키마** — `ai/graph/state.py` (`RagState` TypedDict: 질의·검색쿼리·문서·생성답변·관련성·재시도횟수·근거여부). **langgraph import 없음** — 데이터 계약만.
- ⬜ **F5.2 노드 함수** — `ai/graph/nodes.py` (`RagNodes`: retrieve/grade/rewrite/generate/check). 각 노드는 순수 함수, 의존성 주입. **langgraph import 없음** — 계산 로직만.
- ⬜ **F5.3 그래프 조립** — `ai/graph/builder.py` (**langgraph** `StateGraph`·`add_node`·`add_conditional_edges`·`compile`). grade에서 조건 분기, rewrite→retrieve 루프, check→generate 재생성. **여기서 처음 langgraph 결합.**
- ⬜ **F5.4 에이전트 팩토리 + 모드 토글** — `ai/agent_factory.py` (`AGENT_MODE`로 simple↔graph 실행 경로 선택, 반환은 동일한 `(query, appid) -> Briefing`). 실행: `scripts/agent.py`.

**상태머신 흐름**:
```
START → retrieve → grade → (조건 분기)
                            ├─ generate → check → (조건 분기)
                            │                       ├─ END (근거 있음)
                            │                       └─ generate (재생성, 상한까지)
                            └─ rewrite → retrieve (검색 루프, 상한까지)
```

**완료 기준**: `AGENT_MODE=graph`에서 검색이 부실(관련 문서 부족)하면 쿼리를 재작성해 재검색하고, 생성 답변에 근거가 없으면 재생성하는 동작이 확인됨. `AGENT_MODE=simple`은 Slice 4의 단발 RAG로 동작.

**라이브러리 우선**: 상태머신·분기·루프를 손으로 짜지 않고 **langgraph**의 `StateGraph`로. 단, LLM은 여전히 `LLMProvider` 추상을 씀(langgraph의 ChatModel 통합 미도입 — 계층 격리).

> **왜 어필되나**: "RAG 만들었어요"는 흔하지만, "언제 LangChain 단발로 충분하고 언제 LangGraph 상태머신이 필요한지 판단해 **둘 다 적재적소에** 썼어요"는 실무 이해도를 보여줌.

---

## Slice 6 — 스트리밍 & 오케스트레이션

**목표**: 수집이 배치 스크립트에서 **이벤트 기반**으로 전환되고, Airflow가 주기 실행한다.

### 기능

- ⬜ **F6.1 Kafka 프로듀서** — `ingestion/producer.py` (수집 → `reviews.raw` 토픽 발행, JSON 직렬화). `docker-compose.yml`에 Kafka 추가.
- ⬜ **F6.2 Kafka 컨슈머** — `etl/consumer.py` (`reviews.raw` 소비 → 정제·분석 파이프라인 투입).
- ⬜ **F6.3 Airflow DAG** — `airflow/dags/` (게임별 신규 리뷰 폴링을 주기 실행하는 DAG 1개).
- ⬜ **F6.4 Spark 배치 잡** — `etl/spark_jobs/` (게임별 집계 같은 배치 잡 1개, PySpark).

**완료 기준**: 수집이 Kafka 토픽을 통과하고, Airflow 스케줄러가 주기적으로 수집 태스크를 실행한다. Spark 잡이 배치 집계를 돌린다.

> **범위 주의(간소화 방침)**: 이 스택들은 "다양성 확보"를 위해 남겼지만 **각각 "동작 시연 수준"으로** 만든다 — Kafka는 토픽 1개·프로듀서/컨슈머 각 1개, Airflow는 태스크 1개짜리 DAG, Spark는 집계 잡 1개. 리뷰 수천 개 규모엔 Pandas로도 충분하므로 Spark는 순수 학습 목적.

---

## Slice 7 — 검색 & 모니터링

**목표**: 키워드 전문 검색이 동작하고, 대시보드에서 파이프라인 상태를 관측한다.

### 기능

- ⬜ **F7.1 Elasticsearch 전문 검색** — `serving/search.py` (리뷰 텍스트 키워드 검색 엔드포인트). `infra/elasticsearch/`(인덱스 매핑). pgvector(의미 검색) ↔ ES(키워드 검색) **비교 학습**.
- ⬜ **F7.2 Prometheus 메트릭** — `monitoring/metrics.py` (요청 수·RAG 응답시간·감성 정확도 등 핵심 지표 노출). `infra/prometheus/`(스크레이프 설정).
- ⬜ **F7.3 Grafana 대시보드** — `infra/grafana/` (핵심 지표 패널 하나 — 요청·응답시간·감성 정확도).

**완료 기준**: 키워드 검색이 동작하고, Grafana 대시보드에서 파이프라인 상태(처리량·응답시간·모델 정확도)를 눈으로 확인.

> **범위 주의**: 대시보드는 여러 개가 아니라 핵심 지표 3~4개짜리 패널 하나로. Superset은 Grafana와 역할이 겹쳐 제외됨(간소화 결정).

---

## Slice 8 — 프로덕션 마감

**목표**: PR마다 CI 통과, AWS 배포 가능, 문서 완성.

### 기능

- ⬜ **F8.1 테스트 커버리지** — `tests/` 계층별 pytest 보강.
- ⬜ **F8.2 pre-commit 훅** — Ruff 린트+포맷을 커밋 전 자동 실행.
- ⬜ **F8.3 CI/CD** — GitHub Actions (`actions/setup-python` + `pip install -r requirements.txt` + 린트/타입/테스트).
- ⬜ **F8.4 AWS 배포** — RDS(Postgres) 전환, 컨테이너 배포.
- ⬜ **F8.5 문서·ERD 마감** — `docs/ERD.md` 완성, README 최종화.

**완료 기준**: PR마다 CI가 통과하고, AWS에 배포 가능하며, README·ERD가 완성됨.

---

## 스택 → 슬라이스 도입 시점 (요약)

| 계층 | 스택 | 도입 |
|---|---|---|
| 수집 | httpx, Steam API, Kafka | 1, 6 |
| 처리 | Pandas, langdetect, transformers, BERTopic, scikit-learn, Spark, Airflow, Great Expectations | 1, 3, 6 |
| 저장 | PostgreSQL, pgvector, SQLAlchemy, Alembic, Redis | 2, 4 |
| AI/RAG | Ollama(qwen3), LangChain(langchain·langchain-ollama·langchain-anthropic), LangGraph, sentence-transformers, 추천 | 4, 5 |
| 서빙 | FastAPI, Pydantic, Elasticsearch | 1, 7 |
| 모니터링 | Grafana, Prometheus | 7 |
| 횡단 | pip/venv, Docker, AWS, GitHub Actions, pytest, Ruff, mypy, Invoke | 전 슬라이스 |

> 상세 구조·근거는 [`ARCHITECTURE.md`](./ARCHITECTURE.md), 데이터 모델은 [`ERD.md`](./ERD.md) 참조.

---

## 다음 작업

현재 진행 중인 슬라이스·기능은 **README의 "현재 진행 상황"** 섹션에서 확인합니다 (세션 간 연속성의 기준).
