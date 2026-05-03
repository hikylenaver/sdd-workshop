# Research: 002-todo-tag-feature

**Date**: 2026-05-03  
**Status**: Complete

## 1. 태그 저장 전략

### Decision
**JSON 컬럼** (Text 타입으로 `todos` 테이블에 인라인 저장)

### Rationale
- 단순함 우선(Constitution IV): 별도 `tags` 테이블 + JOIN 없이 단일 테이블로 관리
- 추가 외부 패키지 불필요 (Constitution III): `json` 표준 라이브러리로 직렬화/역직렬화
- 최대 5개, 조회 빈도 낮음 → 정규화 오버헤드 미정당화
- 기존 `Base.metadata.create_all()` 호출 한 번으로 새 컬럼 자동 생성

### Alternatives Considered

| 대안 | 거부 이유 |
|------|---------|
| 별도 `tags` 테이블 (정규화) | JOIN 필요, 관계 관리 복잡성 증가, v1 5개 태그 규모에 과도함 |
| SQLAlchemy `JSON` 타입 | SQLite 드라이버 버전 따라 지원 다름; `Text` + `json.dumps/loads`가 더 안전 |
| PostgreSQL `ARRAY` 타입 | SQLite 미지원 |

### Implementation Detail
```python
# models.py 추가
import json
tags_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

# 직렬화/역직렬화는 property로 캡슐화
@property
def tags(self) -> list[str]:
    return json.loads(self.tags_json)

@tags.setter
def tags(self, value: list[str]) -> None:
    self.tags_json = json.dumps(value, ensure_ascii=False)
```

---

## 2. 태그 필터링 전략

### Decision
**Python 레벨 필터링** (repository에서 전체 로드 후 필터)

### Rationale
- SQLite의 `json_each()` 함수는 SQLite 3.38+(2022-02) 이상 필요; 환경 보장 불가
- 최대 항목 수 현실적 범위(수백~수천)에서 성능 충분 (SC-002: 1,000개 기준 3초 이내)
- `list_all()` 시그니처에 `tag: str | None = None` 추가 후 Python 리스트 필터

### Implementation Detail
```python
# repository.py
def list_all(self, status=None, priority=None, tag=None) -> list[Todo]:
    todos = ... # 기존 SQL 필터 적용
    if tag is not None:
        todos = [t for t in todos if tag in t.tags]
    return todos
```

---

## 3. 태그 검증 정규식

### Decision
```python
TAG_RE = re.compile(r'^[\w가-힣\-]{1,20}$', re.UNICODE)
```
- `\w`: 알파벳·숫자·언더스코어
- `가-힣`: 한글 완성형 범위
- `\-`: 하이픈
- 길이: 1~20자 (정규식 내 `{1,20}`)

### 검증 규칙 요약

| 규칙 | 제약 |
|------|------|
| 최대 태그 수 | 5개 초과 → ValueError |
| 태그 길이 | 1자 이상 20자 이하 |
| 허용 문자 | 알파벳·숫자·한글·`-`·`_` |
| 중복 | 자동 중복 제거 (dict.fromkeys 활용) |
| 빈 문자열 | 오류 처리 |

---

## 4. 기존 DB 호환성

### Decision
`create_all(checkfirst=True)` (기존 호출 방식 유지)

### Rationale
- SQLAlchemy `create_all`은 이미 존재하는 테이블을 건드리지 않음
- **단, 기존 `todos` 테이블에 새 컬럼(`tags_json`)은 자동 추가되지 않음**
- 해결: `tags_json` 컬럼에 `server_default="'[]'"` 설정 + 앱 첫 실행 시 `ALTER TABLE` 실행

### Migration 전략
```python
# db.py create_db_engine() 내 추가
def _migrate_add_tags_column(engine):
    """tags_json 컬럼이 없으면 추가한다 (기존 DB 호환)."""
    with engine.connect() as conn:
        cols = [r[1] for r in conn.execute(text("PRAGMA table_info(todos)"))]
        if "tags_json" not in cols:
            conn.execute(text("ALTER TABLE todos ADD COLUMN tags_json TEXT NOT NULL DEFAULT '[]'"))
            conn.commit()
```

---

## 5. 기존 테스트 영향 분석

| 파일 | 영향 | 조치 |
|------|------|------|
| `tests/unit/test_add_todo.py` | `add_todo()` 시그니처 변경 | `tags` 기본값 `[]`로 하위 호환 유지 |
| `tests/unit/test_list_todos.py` | `list_todos()` 시그니처 변경 | `tag` 기본값 `None`으로 하위 호환 유지 |
| `tests/integration/test_cli_add.py` | `--tag` 옵션 없는 케이스 유지 | 기존 테스트 수정 없이 통과해야 함 |
| `tests/integration/test_cli_list.py` | 출력 포맷 변경 (`tags=[]` 추가) | **기존 테스트 출력 비교 수정 필요** |
| `tests/contract/test_cli_contract.py` | 출력 포맷 변경 | **기존 테스트 출력 비교 수정 필요** |
