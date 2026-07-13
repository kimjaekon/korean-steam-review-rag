# 데이터 모델 (ERD)

> 이 문서는 [`ARCHITECTURE.md`](./ARCHITECTURE.md) §8의 개요를 **컬럼·타입·제약·인덱스까지** 상세화한 것입니다.
> 실제 구현은 `src/steam_rag/storage/postgres/models.py`(SQLAlchemy ORM)이며, 이 문서와 항상 일치시킵니다.

> **ERD** (Entity-Relationship Diagram = 개체-관계도): 데이터베이스의 테이블(개체)과 그들 사이의 관계를 그림으로 나타낸 것.

---

## 전체 관계도

```mermaid
erDiagram
    REVIEW ||--o| REVIEW_ANALYSIS : "1:1 (분석)"
    REVIEW ||--o| REVIEW_EMBEDDING : "1:1 (임베딩)"
    REVIEW ||--o{ REVIEW_TOPIC : "1:N (토픽 태깅)"
    REVIEW }o..o{ TOPIC_NAME : "appid+topic_id 로 참조"

    REVIEW {
        bigint id PK "autoincrement 내부 키"
        bigint recommendation_id UK "Steam 고유 ID — FK 대상"
        bigint appid "게임 ID (index)"
        string author_steamid "작성자 (varchar 32)"
        text content "리뷰 본문"
        bool voted_up "추천 여부 = 정답 라벨"
        int playtime_at_review_min "작성 시점 플레이타임(분)"
        int votes_helpful "도움됨 투표 수"
        timestamptz created_at "리뷰 작성 시각"
        timestamptz collected_at "수집 시각"
    }

    REVIEW_ANALYSIS {
        bigint review_recommendation_id PK_FK "reviews.recommendation_id"
        float sentiment_score "감성 점수"
        string sentiment_label "감성 라벨 (varchar 16, index)"
        bool matches_voted_up "예측이 실제 추천과 일치?"
        timestamptz analyzed_at "분석 시각"
        jsonb features "playtime_quartile 등 (nullable)"
    }

    REVIEW_EMBEDDING {
        bigint review_recommendation_id PK_FK "reviews.recommendation_id"
        vector embedding "vector(768) — ko-sroberta"
    }

    REVIEW_TOPIC {
        bigint review_recommendation_id PK_FK "reviews.recommendation_id"
        int topic_id PK "토픽 ID (복합 PK)"
        text keywords "토픽 키워드"
        float weight "이 리뷰의 토픽 소속 가중치"
    }

    TOPIC_NAME {
        bigint appid PK "게임 ID (복합 PK)"
        bigint topic_id PK "토픽 ID (복합 PK)"
        text name "사람이 읽는 토픽 이름"
        text keywords "대표 키워드"
    }
```

---

## 테이블 상세

### `reviews` — 리뷰 원본

수집된 리뷰 하나가 한 행. 이 프로젝트의 **중심 테이블**이며, 나머지 테이블은 전부 이 테이블을 참조합니다.

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| `id` | BigInteger | **PK**, autoincrement | 내부 자동 증가 키 |
| `recommendation_id` | BigInteger | **Unique**, NOT NULL | **Steam이 부여한 고유 리뷰 ID** — 다른 테이블의 FK 대상 |
| `appid` | BigInteger | NOT NULL, **index** | 게임 ID |
| `author_steamid` | String(32) | NOT NULL | 작성자 SteamID |
| `content` | Text | NOT NULL | 리뷰 본문 |
| `voted_up` | Boolean | NOT NULL | **추천/비추천 = 정답 라벨** |
| `playtime_at_review_min` | Integer | NOT NULL | 작성 시점 누적 플레이타임(분) |
| `votes_helpful` | Integer | NOT NULL | "도움이 됨" 투표 수 |
| `created_at` | DateTime(tz) | NOT NULL | 리뷰 작성 시각 (timezone 포함) |
| `collected_at` | DateTime(tz) | NOT NULL | 우리가 수집한 시각 |

> **`id`와 `recommendation_id`가 둘 다 있는 이유**: `id`는 DB 내부용 자동 증가 키, `recommendation_id`는 Steam이 부여한 안정적 고유 키입니다. **FK는 `recommendation_id`를 씁니다** — 수집 시점에 이미 정해진 값이라, 재수집·UPSERT 시 매칭이 어긋나지 않습니다.

> **`voted_up`·`playtime_at_review_min`이 핵심 차별점**: 뉴스 기사엔 없는 **정답 라벨**과 **작성 시점 플레이타임**이 리뷰엔 있습니다. 감성 모델 예측을 `voted_up`과 대조해 정량 검증(→ `review_analysis.matches_voted_up`)하고, 플레이타임은 "장시간 플레이 후 비추천" 같은 신뢰도 높은 피드백을 가려내는 피처로 씁니다.

---

### `review_analysis` — 감성·피처 분석 결과

리뷰 하나당 분석 결과 한 행 (**1:1**). 감성 분석(Slice 3)과 피처 추출의 산출물.

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| `review_recommendation_id` | BigInteger | **PK**, **FK** → `reviews.recommendation_id`, ON DELETE CASCADE | 리뷰 참조 (동시에 PK) |
| `sentiment_score` | Float | NOT NULL | 감성 점수 (연속값) |
| `sentiment_label` | String(16) | NOT NULL, **index** | 감성 라벨 (Positive/Negative 등) |
| `matches_voted_up` | Boolean | NOT NULL | **예측이 실제 `voted_up`과 일치하는가** |
| `analyzed_at` | DateTime(tz) | NOT NULL | 분석 실행 시각 |
| `features` | JSONB | nullable | `playtime_quartile` 등 유연 피처 |

> **`matches_voted_up`의 역할**: 감성 모델의 예측과 실제 추천 라벨의 일치 여부를 저장해 두면, 모델 정확도를 Slice 7 대시보드에서 바로 관측할 수 있습니다. 스팀 리뷰 도메인의 강점(정답 라벨 존재)을 활용하는 지점.

> **`features`가 JSONB인 이유**: 피처를 컬럼으로 고정하지 않고 JSONB로 두면, 새 피처(예: 리뷰 길이·이모지 비율)를 스키마 변경 없이 추가할 수 있습니다.

---

### `review_embedding` — 임베딩 벡터

리뷰 하나당 벡터 한 행 (**1:1**, PK=FK). 임베딩 생성(Slice 4)의 산출물.

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| `review_recommendation_id` | BigInteger | **PK**, **FK** → `reviews.recommendation_id`, ON DELETE CASCADE | 리뷰 참조 (동시에 PK) |
| `embedding` | Vector(768) | NOT NULL | ko-sroberta 출력 벡터 |

- **타입**: pgvector 확장의 `vector` 타입. ko-sroberta 출력 차원(768)에 맞춰 `vector(768)`.
- **인덱스**: **HNSW** 인덱스로 유사도 검색 (Alembic 마이그레이션에서 `op.execute()`로 생성).
- **거리 측정**: 코사인 거리 (`cosine_distance`).

> **용어**
> - **차원**(dimension): 임베딩 벡터의 숫자 개수. ko-sroberta는 문장 하나를 숫자 768개 벡터로 표현 → `vector(768)`.
> - **HNSW** (Hierarchical Navigable Small World): 수많은 벡터 중 "가장 비슷한 top-k"를 빠르게 찾는 인덱스. 전부 비교하지 않고 지름길로 근처를 탐색.
> - **⚠️ HNSW는 시간을 모른다**: 유사도만 보고 "최근 리뷰"를 우선하지 않습니다. 그래서 RAG는 검색 결과에 `created_at`을 병기해 시점 편향을 드러냅니다.

---

### `review_topic` — 리뷰별 토픽 태깅

리뷰 하나가 여러 토픽에 속할 수 있음 (**1:N**). BERTopic 분석(Slice 3)의 산출물.

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| `review_recommendation_id` | BigInteger | **복합 PK**, **FK** → `reviews.recommendation_id`, ON DELETE CASCADE | 리뷰 참조 |
| `topic_id` | Integer | **복합 PK** | 토픽 ID |
| `keywords` | Text | NOT NULL | 토픽 키워드 |
| `weight` | Float | NOT NULL | 이 리뷰의 토픽 소속 가중치 |

> **복합 PK `(review_recommendation_id, topic_id)`**: 한 리뷰가 여러 토픽을 가질 수 있으므로, 리뷰 ID만으로는 PK가 안 됩니다. 리뷰+토픽 조합이 유일합니다.

---

### `topic_names` — 토픽 이름 (게임별)

토픽 하나당 한 행 (**토픽 단위**, 리뷰 단위 아님). 토픽 이름 생성(Slice 3, LLM)의 산출물.

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| `appid` | BigInteger | **복합 PK** | 게임 ID |
| `topic_id` | BigInteger | **복합 PK** | 토픽 ID |
| `name` | Text | NOT NULL | 사람이 읽는 토픽 이름 (LLM 생성) |
| `keywords` | Text | NOT NULL | 대표 키워드 |

> **`review_topic`과의 차이**: `review_topic`은 "리뷰 → 토픽" 매핑(리뷰마다 여러 행)이고, `topic_names`는 "토픽 → 이름"(게임의 토픽마다 딱 1행)입니다. c-TF-IDF 키워드를 LLM이 사람이 읽는 이름으로 바꿔 저장하며, RAG 브리핑의 컨텍스트에 얹힙니다(Slice 4).

> **복합 PK `(appid, topic_id)`**: 토픽 ID는 게임마다 독립적으로 매겨지므로, 게임 ID와 함께여야 유일합니다.

---

## 설계 노트

### 왜 `GAME` 테이블이 없는가

게임 메타데이터(이름·장르·출시일)를 별도 테이블로 두지 않고, `appid`를 `reviews`에 직접 저장합니다. 지금 범위(리뷰 분석·RAG·추천)에선 게임 엔티티 자체가 필요 없어 단순하게 갑니다.

> **확장 시**: 게임 메타가 필요해지면 `GAME { appid PK, name, genres, released_at }` 테이블을 추가하고 `reviews.appid`를 FK로 연결하는 마이그레이션으로 확장합니다.

### FK 삭제 정책: ON DELETE CASCADE

모든 자식 테이블(`review_analysis`·`review_embedding`·`review_topic`)의 FK는 `ON DELETE CASCADE`입니다. 리뷰가 삭제되면 그에 딸린 분석·임베딩·토픽도 함께 삭제돼, 고아 행(orphan)이 남지 않습니다.

### 마이그레이션

스키마는 **Alembic**으로 버전 관리합니다 (Slice 2). 특히 pgvector 확장 설치, `vector(768)` 컬럼, HNSW 인덱스는 `op.execute()`로 마이그레이션에 명시적으로 넣습니다 — `create_all()`로는 깔끔하게 잡히지 않기 때문입니다.

---

> 구조·근거는 [`ARCHITECTURE.md`](./ARCHITECTURE.md), 개발 순서는 [`ROADMAP.md`](./ROADMAP.md) 참조.
