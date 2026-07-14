# 한국어 스팀 리뷰 분석 + RAG 브리핑 플랫폼

Steam 게임의 **한국어 리뷰**를 수집해 감성·토픽 분석과 임베딩을 수행하고, **RAG 기반 여론 브리핑**과 **유사 게임 추천**을 제공하는 데이터·AI 플랫폼입니다.

> **RAG** (Retrieval-Augmented Generation = 검색 증강 생성): LLM이 그냥 답하지 않고, 먼저 관련 리뷰를 **검색**한 뒤 그 내용을 근거로 답을 **생성**하는 방식. "아는 척"이 아니라 "찾아보고 답하기".

---

## 이 프로젝트가 하는 일

- **수집**: 특정 게임(appid)의 한국어 리뷰를 Steam 공개 API에서 수집
- **분석**: 감성 분석(추천/비추천 라벨과 대조 검증) · 토픽 분석(BERTopic) · 피처 추출(플레이타임 사분위 등)
- **임베딩·검색**: 리뷰를 벡터로 변환(ko-sroberta) → pgvector 유사도 검색
- **RAG 브리핑**: "이 게임 최근 한국어 여론 브리핑" 질의 → 근거 리뷰 기반 요약
- **추천**: 게임 하나를 기준으로 유사한 게임 추천

### 무엇이 다른가

스팀 리뷰에는 뉴스 기사에 없는 **정답 라벨(추천/비추천)**과 **작성 시점 플레이타임**이 붙어 있습니다. 그래서 감성 모델의 예측을 실제 라벨과 비교해 **정량 검증**할 수 있고, RAG 생성 답변의 근거도 실제 리뷰로 대조하기 쉽습니다.

---

## 기술 스택

| 계층 | 스택 |
|---|---|
| **수집** | httpx, Steam Store/Steamworks API, Kafka |
| **처리** | Pandas, langdetect, transformers, BERTopic, scikit-learn, Spark, Airflow, Great Expectations |
| **저장** | PostgreSQL, pgvector, SQLAlchemy, Alembic, Redis |
| **AI/RAG** | Ollama(qwen3), LangChain(langchain·langchain-ollama·langchain-anthropic), LangGraph, sentence-transformers(ko-sroberta) |
| **서빙** | FastAPI, Pydantic, Elasticsearch |
| **모니터링** | Prometheus, Grafana |
| **횡단** | pip/venv, Docker, AWS, GitHub Actions, pytest, Ruff, mypy, Invoke |

> **설계 문서**: 전체 구조와 근거는 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), 개발 순서는 [`docs/ROADMAP.md`](docs/ROADMAP.md), 데이터 모델은 [`docs/ERD.md`](docs/ERD.md) 참조.

---

## 설계 원칙

1. **교체 가능성** — 저장소·LLM·수집기는 인터페이스 뒤에 숨긴다. 환경변수 하나로 로컬 ↔ 클라우드, Ollama ↔ Claude 교체.
2. **계층 격리** — 도메인 로직은 FastAPI도 PostgreSQL도 모른다.
3. **항상 동작** — 매 개발 단계 끝에 `docker compose up` 하면 전체가 돈다.
4. **라이브러리 우선** — 검증된 라이브러리가 하는 일을 손으로 재구현하지 않는다. **라이브러리를 제대로 쓰는 법을 익히며 소스를 채운다.**

---

## 개발 환경

| 항목 | 값 |
|---|---|
| OS | Windows 11 (Docker Desktop + WSL2 백엔드) |
| GPU | RTX 5060 Ti 16GB (Blackwell, CUDA 12.8) |
| 파이썬 | 3.13 (venv) |
| 패키지 | pip + `requirements.txt` (버전 핀 고정) |
| LLM 런타임 | Ollama (Windows 네이티브) — 호스트에서 `ollama serve`, 컨테이너는 `host.docker.internal:11434` 접속 |

---

## 시작하기

### 1. 사전 준비

```powershell
# 파이썬 3.13 (없으면 한 번만)
winget install --id=Python.Python.3.13 -e

# 저장소 클론 후 폴더로 이동
git clone https://github.com/kimjaekon/korean-steam-review-rag.git
cd korean-steam-review-rag
```

### 2. 가상환경 + 의존성

```powershell
python -m venv .venv                 # 가상환경 생성
.\.venv\Scripts\Activate.ps1         # 활성화 (PATH·VIRTUAL_ENV 설정됨)
python -m pip install --upgrade pip  # pip 최신화
pip install -r requirements.txt      # 런타임 의존성
pip install -r requirements-dev.txt  # 개발 의존성
pip install -e .                     # steam_rag 를 편집 가능 패키지로 설치 (import 경로 인식)
```

### 3. 인프라 + 실행

```powershell
copy .env.example .env               # 환경변수 파일 생성 후 필요한 값 채우기
docker compose up -d                 # Postgres 등 인프라 컨테이너 기동
uvicorn steam_rag.serving.api.main:app --reload  # FastAPI 실행
```

`http://localhost:8000/health` 로 동작 확인.

> **pip + venv 요약**: 활성화 `.\.venv\Scripts\Activate.ps1` / 설치 `pip install -r requirements.txt` / 패키지 추가는 `requirements.txt`에 한 줄 적고 재설치. 재현 가능한 빌드를 위해 `pkg==x.y.z`로 버전을 핀 고정하고 `requirements*.txt`를 커밋.

---

## 프로젝트 구조 (요약)

```
korean-steam-review-rag/
├── docs/            # ARCHITECTURE · ROADMAP · ERD
├── scripts/         # 각 슬라이스의 CLI 실행 진입점 (수동 검증용)
├── src/steam_rag/
│   ├── domain/      # 순수 도메인 (엔티티 · 인터페이스, 외부 의존 0)
│   ├── ingestion/   # 수집 (httpx · Kafka 발행)
│   ├── etl/         # 처리 (정제 · 언어필터 · 분석 · 검증)
│   ├── storage/     # 저장 (Postgres · pgvector · Redis)
│   ├── ai/          # AI/RAG (임베딩 · LLM · LangChain · LangGraph · 추천)
│   ├── serving/     # 서빙 (FastAPI · Elasticsearch)
│   └── monitoring/  # 모니터링 (Prometheus)
├── alembic/         # DB 마이그레이션
├── airflow/dags/    # 배치 스케줄
├── infra/           # grafana · prometheus · elasticsearch 설정
└── tests/           # pytest
```

전체 상세 트리는 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) §4 참조.

---

## 현재 진행 상황

> 이 섹션이 **세션 간 연속성의 기준(single source of truth)**입니다. 작업이 진행되면 여기를 갱신합니다.
> 상태: ⬜ 예정 · 🟦 진행 중 · ✅ 완료

**전체 진척: Slice 0 완료 — Slice 1(얇은 관통) 진행 예정**

| 슬라이스 | 이름 | 상태 |
|---|---|---|
| 0 | 뼈대 (Skeleton) | ✅ |
| 1 | 얇은 관통 (Walking Skeleton) | 🟦 |
| 2 | 저장 계층 정식화 | ⬜ |
| 3 | 분석 파이프라인 | ⬜ |
| 4 | AI/RAG (LangChain) | ⬜ |
| 5 | LangGraph 에이전트 | ⬜ |
| 6 | 스트리밍 & 오케스트레이션 | ⬜ |
| 7 | 검색 & 모니터링 | ⬜ |
| 8 | 프로덕션 마감 | ⬜ |

**Slice 0 기능 진행**

| 기능 | 이름 | 상태 |
|---|---|---|
| F0.1 | 프로젝트 구조 + 패키징 | ✅ |
| F0.2 | Docker Compose (Postgres) | ✅ |
| F0.3 | 설정 로더 | ✅ |
| F0.4 | FastAPI 뼈대 + `/health` | ✅ |
| F0.5 | Invoke 태스크 + CI 뼈대 | ✅ |

**Slice 1 기능 진행**

| 기능 | 이름 | 상태 |
|---|---|---|
| F1.1 | 도메인 모델 + 인터페이스 | ✅ |
| F1.2 | Steam 수집기 | ✅ |
| F1.3 | 최소 정제 | ✅ |
| F1.4 | Postgres 저장 (raw) | ✅ |
| F1.5 | 조회 API | ⬜ |

> **F0.1 완료 내역**: `src/steam_rag/` 패키지 뼈대(§4 트리) · `pyproject.toml`(Ruff·mypy) · `requirements.txt`/`requirements-dev.txt`(버전 핀) · `.vscode/`(인터프리터·저장 시 Ruff) · `.gitignore`. 검증: `pip install -e .`로 패키지 인식, Ruff `select`(I·F 등)·mypy `strict` 동작 확인.

> **F0.2 완료 내역**: `docker-compose.yml`(pgvector/pgvector:pg16 · named volume `pgdata` · `pg_isready` 헬스체크) + `docker-compose.override.yml`(로컬 전용 `5432` 포트 노출). 검증: `docker compose up -d` → `(healthy)`, `pg_available_extensions`에 `vector` 존재 확인. `.env`는 임시 최소본(POSTGRES_* · DB_PORT), F0.3에서 `.env.example`로 정식화 예정.

> **F0.3 완료 내역**: `src/steam_rag/config/settings.py` — Pydantic Settings(`BaseSettings`)로 `.env`·환경변수 로드. **nested 구조**(`DatabaseSettings`·`LLMSettings` 서브모델 + 평면 필드)에 `env_nested_delimiter="__"` 적용 → `DB__HOST`→`settings.db.host` 매핑. `extra="ignore"`로 compose 전용 변수(`POSTGRES_*`·`DB_PORT`)와 `.env` 한 파일 공유. 모듈 끝에서 `settings` 싱글턴 생성(앱 시작 시 검증). `.env.example`에 §6 교체 지점 9개 변수(compose용 홑밑줄 + 앱용 겹밑줄) 정리. 검증: nested 매핑·문자열→int 변환·기본값·잘못된 타입 시작 시 실패 확인, Ruff(E·F·I·UP·B)·mypy strict 통과. **주의**: nested라 §6 표의 `DB_HOST`는 실제 `.env`에서 `DB__HOST`(겹밑줄)로 씀.

> **F0.4 완료 내역**: `src/steam_rag/serving/api/main.py` — FastAPI `app` 인스턴스(모든 엔드포인트가 얹힐 뿌리 객체) + `GET /health`. 응답에 `settings.llm.provider`·`settings.agent_mode`를 실어 `.env`→`Settings`(F0.3)→앱까지 설정 관통을 검증. 라우터 분리(`APIRouter`)·`schemas.py`·`dependencies.py`는 엔드포인트가 늘어나는 Slice 1에서 도입(YAGNI). 검증: `uvicorn steam_rag.serving.api.main:app --reload` → `/health` JSON `{"status":"ok",...}` 응답, `/docs` 자동 문서에 `/health` 노출 확인.

> **F0.5 완료 내역**: `tasks.py` — Invoke 태스크(`lint`·`fmt`·`typecheck`·`test`·`up`·`down` + pre-task로 묶은 `check`). Windows에 `make`가 없어 파이썬 기반 러너 사용. `c.run()`으로 실제 명령(ruff·mypy·docker compose) 위임 → **로컬과 CI가 같은 명령**을 호출. `.github/workflows/ci.yml` — push·main대상 PR 트리거, `actions/checkout@v4` + `actions/setup-python@v5`(3.13, pip 캐시) + `pip install -r requirements-dev.txt` + `pip install -e .` → `invoke lint`·`invoke typecheck`(테스트 스텝은 테스트 도입되는 Slice 8까지 보류). `pyproject.toml`에 `[tool.mypy]`(strict·`files=["src","tests"]`·`ignore_missing_imports`) 추가해 그간 CLI 인자에 의존하던 설정을 파일로 고정. `requirements-dev.txt`의 `invoke` 버전 핀(`2.*`). `tests/__init__.py` 추가로 빈 디렉터리 mypy 에러 방지. 검증: `invoke lint`·`typecheck`·`check` 통과, `ci.yml` YAML 파싱·트리거·스텝 확인. **주의**: Pydantic v2·FastAPI는 자체 타입 정보를 완비해 별도 mypy 플러그인 없이 strict 통과(단, 런타임 deps가 설치돼 있어야 함 — 미설치 시 라이브러리를 Any로 봐 오탐).

> **F1.1 완료 내역**: `domain/models.py` — `Review` 엔티티를 표준 라이브러리 `@dataclass(frozen=True, slots=True)`로 정의(불변 값 객체·메모리 절약·오타 속성 차단). **프레임워크 import 0**(Pydantic조차 안 씀 — 도메인은 순수 파이썬, 검증은 경계인 `schemas.py`/`settings.py`가 담당). DB 자동증가 `id`는 도메인에서 제외하고 Steam `recommendation_id`(자연 키)만 보유 → 도메인 엔티티 ≠ DB 행(계층 격리). `domain/interfaces.py` — `ReviewCollector`·`ReviewRepository`를 `abc.ABC`가 아닌 `typing.Protocol`(+`@runtime_checkable`)로 정의: **구조적 서브타이핑**이라 구현체가 도메인을 상속·import 하지 않아도 mypy가 계약 만족을 정적 검증 → 의존 방향 완전 차단(원칙 1·2). 반환 타입은 최소 능력만 요구(`collect`→`Iterable`로 제너레이터 허용, `get_by_appid`→`Sequence`로 `len()`·인덱싱 허용). 검증: import·Ruff(E·F·I·UP·B)·mypy strict 통과, 상속 없는 `InMemoryRepo`가 `ReviewRepository`로 인정되고 멱등 저장(중복 `recommendation_id` 무시)·`frozen` 변경 차단 동작 확인. **주의**: `frozen=True`+`slots=True` 조합에선 필드 변경 시 `AttributeError`가 아니라 `FrozenInstanceError`가 먼저 발생.

> **F1.2 완료 내역**: `ingestion/collectors/steam.py` — `SteamReviewCollector`가 `httpx.Client`(연결 풀 재사용)로 공개 appreviews 엔드포인트 호출. 커서 페이지네이션은 `params` dict에 커서를 넣어 httpx가 `=`·`+`를 URL 인코딩하게 위임하고, 종료 조건 3개(`success!=1`/빈 배열, `limit` 도달, 커서 불변)로 무한루프 차단. `raise_for_status()`로 4xx·5xx를 예외화(조용한 실패 방지), `response.json()`으로 파싱. 반환은 `Iterator[Review]` 제너레이터라 `limit` 도달 시 즉시 중단해 불필요한 페이지 호출을 아낌. 필드 매핑 주의: `playtime_at_review`·`steamid`는 `author` 중첩에서 꺼내고, `appid`는 응답에 없어 인자 값 사용, `timestamp_created`(Unix초)는 `datetime.fromtimestamp(tz=UTC)`로 tz 인식 변환(ERD `timestamptz` 대응). 언어는 하드코딩 없이 `settings.steam_language`(§6 교체 지점)에서 주입. 검증: `scripts/collect_reviews.py 570 5`로 5개 수집 확인, 상속 없는 `SteamReviewCollector`가 `ReviewCollector`로 `isinstance` 인정, `invoke check` 통과.

> **F1.3 완료 내역**: `etl/transform.py` — `clean_reviews(Iterable[Review]) -> list[Review]`가 Pandas로 빈 content·중복 `recommendation_id` 제거. **왕복 패턴**: `asdict`로 dataclass(`slots=True`라 `vars()` 불가) → dict 리스트 → `DataFrame` → 정제 → `to_dict(orient="records")` → `Review(**row)` 복원 (도메인 엔티티는 Pandas를 모름 — 계층 격리). 정제 3종: `.str.strip().str.len()>0` 불리언 마스킹으로 빈 리뷰 제거, `drop_duplicates(subset="recommendation_id", keep="first")`로 중복 제거(커서 페이지 경계 재출현 대비, 앞 페이지 우선). 손구현 대신 Pandas API 사용법 습득이 목적(원칙 4) — Slice 3 사분위·집계의 뼈대. `requirements.txt`에 `pandas==2.*` 추가. 검증: `scripts/clean_reviews.py 570 100`으로 before/after 카운트, 인위적 입력(빈 1·중복 1)에서 1개만 남음 확인, `invoke check` 통과. **주의**: Pandas가 `datetime`→`Timestamp`, `bool`→`numpy.bool_`로 바꿔 F1.4 psycopg INSERT 시 어댑터가 필요할 수 있음(그때 대응).

> **F1.4 완료 내역**: `storage/postgres/repository.py` — `PostgresReviewRepository`가 psycopg raw SQL로 `ReviewRepository` 프로토콜(F1.1) 구현. Alembic 도입 전이라 `CREATE TABLE IF NOT EXISTS`로 `reviews` 테이블을 저장소가 자족 보장(ERD 스키마 준수, `recommendation_id UNIQUE` — `ON CONFLICT`의 전제). **저장**: `cur.executemany(_INSERT, rows)` — psycopg 3의 `executemany`는 3.1부터 내부적으로 **파이프라인 모드**라 psycopg2의 `execute_values` 없이도 배치 전송이 빠름(원칙 4). `ON CONFLICT (recommendation_id) DO NOTHING`으로 멱등 저장, `cur.rowcount`로 실제 신규 INSERT 수 반환. **조회**: `cursor(row_factory=class_row(Review))`로 SELECT 행을 컬럼명↔dataclass 필드명 매칭해 `Review`로 자동 매핑(그래서 `SELECT *` 대신 컬럼 명시). **F1.3 경고 대응**: Pandas 왕복으로 `datetime→Timestamp`·`bool→numpy.bool_`가 된 값을 `to_pydatetime()`·`int()`·`bool()`로 표준형 캐스팅 후 INSERT. DSN은 `settings.db.url`의 `postgresql+psycopg://`(SQLAlchemy용)에서 `+psycopg`를 떼어 psycopg에 전달. 검증: `scripts/save_reviews.py 570 20`으로 저장·조회 확인, 재실행 시 `저장: 0개`(멱등) 확인, `invoke check` 통과. **주의**: 자리표시자는 f-string이 아니라 psycopg의 `%(name)s` 바인딩(인젝션 방지) — 값은 항상 두 번째 인자로. **부채**: 커넥션을 매 호출 새로 열어(풀 없음) 소규모엔 무해하나 Slice 2에서 SQLAlchemy 세션·`ON CONFLICT`를 정식화하며 해소.

**▶️ 다음 작업**: Slice 1 · F1.5 (조회 API) — `serving/api/main.py`에 `GET /reviews/{appid}` 추가, `serving/schemas.py`에 `ReviewOut`(Pydantic 응답 모델) 정의. `PostgresReviewRepository.get_by_appid`(F1.4)를 호출해 JSON 반환. 이걸로 Slice 1 "리뷰 1개가 수집돼 API로 나온다" 관통이 완성된다.

세부 기능(feature) 단위 체크리스트는 [`docs/ROADMAP.md`](docs/ROADMAP.md) 참조.

---

## 라이선스

(추후 명시)
