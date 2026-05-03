# Implementation Plan: Todo 태그 기능 추가

**Branch**: `002-todo-tag-feature` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/002-todo-tag-feature/spec.md`

## Summary

기존 CLI Todo 앱에 태그 기능을 추가한다. `todo add` 명령에 `--tag` 옵션(반복 가능)을 추가하고, `todo list --tag <태그>`로 필터링할 수 있게 한다. 태그는 `todos` 테이블의 `tags_json` TEXT 컬럼에 JSON으로 저장하며, 기존 코드와의 하위 호환성을 유지한다. 신규 외부 패키지 없이 기존 SQLAlchemy + Typer 스택 내에서 구현한다.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: Typer 0.25.1, SQLAlchemy 2.0, pytest 9.0.3, pytest-cov 7.1.0  
**Storage**: SQLite (`~/.todo/todo.db`) — `todos` 테이블에 `tags_json` TEXT 컬럼 추가  
**Testing**: pytest + pytest-cov (커버리지 임계치 90%)  
**Target Platform**: 로컬 터미널 (Windows/macOS/Linux)  
**Project Type**: CLI 도구  
**Performance Goals**: 1,000개 항목 기준 `list --tag` 3초 이내 (Python 레벨 필터로 충분)  
**Constraints**: 추가 외부 패키지 없음, 기존 테스트 하위 호환 유지, 커버리지 90%+  
**Scale/Scope**: 단일 사용자, 수백~수천 항목

## Constitution Check

*GATE: 위반 시 ERROR — 미정당화 위반 항목은 구현 진행 불가*

| 원칙 | 준수 여부 | 근거 |
|------|-----------|------|
| **I. 레이어 분리** | ✅ PASS | 태그 검증(`services.py`), 직렬화(`models.py`), 필터(`repository.py`), CLI 파싱(`cli/main.py`), 출력(`cli/formatters.py`) 각 레이어 분리 |
| **II. 테스트 우선** | ✅ PASS | 각 구현 태스크 앞에 실패 테스트 작성 태스크 배치 (tasks.md에 명시) |
| **III. 최소 의존성** | ✅ PASS | `json` 표준 라이브러리만 추가 사용. SQLAlchemy Text 컬럼으로 별도 패키지 불필요 |
| **IV. 단순함 우선** | ✅ PASS | 별도 `tags` 테이블 대신 JSON 컬럼 선택. Python 레벨 필터로 SQLite JSON 함수 의존 제거 |
| **V. CLI 범위** | ✅ PASS | REST API·GUI 없음. `--tag` 옵션 형태로만 인터페이스 제공 |

**Constitution Check: ALL PASS — 구현 진행 가능**

## Project Structure

### Documentation (this feature)

```text
specs/002-todo-tag-feature/
├── plan.md              # 이 파일 (/speckit.plan 출력)
├── research.md          # Phase 0 출력 ✅
├── data-model.md        # Phase 1 출력 ✅
├── contracts/
│   └── cli-contract.md  # Phase 1 출력 ✅ (v2, 태그 반영)
└── tasks.md             # Phase 2 출력 (/speckit.tasks — 미생성)
```

### Source Code (변경 파일)

```text
todo_lib/
├── models.py        # tags_json 컬럼 + tags property 추가
├── db.py            # _migrate_add_tags_column() 추가
├── services.py      # validate_tags() + add_todo/list_todos 시그니처 확장
└── repository.py    # list_all(tag=) 파라미터 추가

cli/
├── main.py          # add --tag 옵션, list --tag 옵션 추가
└── formatters.py    # fmt_todo_row()에 tags 출력 추가

tests/
├── unit/
│   ├── test_add_todo.py          # tags 파라미터 케이스 추가
│   ├── test_list_todos.py        # tag 필터 케이스 추가
│   └── test_tag_validation.py   # validate_tags() 단위 테스트 (신규)
├── integration/
│   ├── test_cli_add.py           # --tag 옵션 시나리오 추가
│   └── test_cli_list.py          # --tag 필터 시나리오 추가, 출력 포맷 수정
└── contract/
    └── test_cli_contract.py      # 출력 포맷(tags=[]) 반영 수정
```

**Structure Decision**: 단일 프로젝트 구조 (Option 1). 기존 `todo_lib/` + `cli/` + `tests/` 레이아웃 유지.

## Complexity Tracking

> Constitution Check 위반 없음 — 이 섹션 적용 불필요

---

## Implementation Phases

### Phase A: 도메인 레이어 (todo_lib/)

#### A-1. 모델 확장 (`todo_lib/models.py`)

**변경 내용**:
```python
import json

class Todo(Base):
    # 기존 컬럼 유지
    ...
    tags_json: Mapped[str] = mapped_column(
        Text, nullable=False, default="[]", server_default="'[]'"
    )

    @property
    def tags(self) -> list[str]:
        """태그 목록을 반환한다."""
        return json.loads(self.tags_json)

    @tags.setter
    def tags(self, value: list[str]) -> None:
        """태그 목록을 JSON으로 직렬화하여 저장한다."""
        self.tags_json = json.dumps(value, ensure_ascii=False)
```

**하위 호환**: 기존 필드/생성자 변경 없음. `tags` property 신규 추가.

---

#### A-2. DB 마이그레이션 (`todo_lib/db.py`)

**변경 내용**:
```python
from sqlalchemy import text

def _migrate_add_tags_column(engine: Engine) -> None:
    """기존 DB에 tags_json 컬럼이 없으면 추가한다."""
    with engine.connect() as conn:
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(todos)"))]
        if "tags_json" not in cols:
            conn.execute(text("ALTER TABLE todos ADD COLUMN tags_json TEXT NOT NULL DEFAULT '[]'"))
            conn.commit()

def create_db_engine(db_path: str | None = None) -> Engine:
    path = db_path or get_db_path()
    engine = create_engine(f"sqlite:///{path}", echo=False)
    Base.metadata.create_all(engine)
    _migrate_add_tags_column(engine)  # 기존 DB 호환
    return engine
```

---

#### A-3. 태그 검증 함수 (`todo_lib/services.py`)

**변경 내용**:
```python
TAG_RE = re.compile(r'^[\w가-힣\-]{1,20}$', re.UNICODE)
MAX_TAGS = 5

def validate_tags(tags: list[str]) -> list[str]:
    """태그 목록을 검증하고 중복 제거된 목록을 반환한다."""
    if len(tags) > MAX_TAGS:
        raise ValueError(f"태그는 최대 {MAX_TAGS}개까지 허용됩니다. (현재 {len(tags)}개)")
    seen: dict[str, None] = {}
    for tag in tags:
        if not tag:
            raise ValueError("태그는 빈 값일 수 없습니다.")
        if not TAG_RE.match(tag):
            raise ValueError(
                f"태그에 허용되지 않는 문자가 포함되어 있습니다: '{tag}'. "
                "알파벳·숫자·한글·하이픈·언더스코어만 허용됩니다 (1~20자)."
            )
        seen[tag] = None
    return list(seen.keys())
```

**참고**: 길이 검증은 `TAG_RE`의 `{1,20}`에 포함됨 (0자·21자 이상 모두 불일치).

---

#### A-4. 서비스 시그니처 확장 (`todo_lib/services.py`)

**변경 내용**:
```python
def add_todo(
    self,
    title: str,
    due_date: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,  # 신규, 기본값 None → []
) -> Todo:
    ...
    clean_tags = validate_tags(tags or [])
    todo = Todo(title=clean_title, due_date=clean_due, priority=clean_priority,
                created_at=now, updated_at=now)
    todo.tags = clean_tags
    return self._repo.add(todo)

def list_todos(
    self,
    status: str | None = None,
    priority: str | None = None,
    tag: str | None = None,  # 신규, 기본값 None
) -> list[Todo]:
    ...
    return self._repo.list_all(status=clean_status, priority=clean_priority, tag=tag)
```

---

#### A-5. 리포지토리 필터 확장 (`todo_lib/repository.py`)

**변경 내용**:
```python
def list_all(
    self,
    status: str | None = None,
    priority: str | None = None,
    tag: str | None = None,  # 신규
) -> list[Todo]:
    query = self._session.query(Todo)
    if status is not None:
        query = query.filter(Todo.status == status)
    if priority is not None:
        query = query.filter(Todo.priority == priority)
    todos = query.order_by(Todo.id).all()
    if tag is not None:
        todos = [t for t in todos if tag in t.tags]
    return todos
```

---

### Phase B: CLI 레이어 (cli/)

#### B-1. add 명령 확장 (`cli/main.py`)

**변경 내용**:
```python
from typing import List

@app.command()
def add(
    title: str = typer.Argument(...),
    due: Optional[str] = typer.Option(None, "--due"),
    priority: Optional[str] = typer.Option(None, "--priority"),
    tag: Optional[List[str]] = typer.Option(None, "--tag", help="태그 (반복 가능, 최대 5개)"),
) -> None:
    service = _get_service()
    try:
        todo = service.add_todo(title=title, due_date=due, priority=priority, tags=tag or [])
        typer.echo(formatters.fmt_add_success(todo))
    except ValueError as e:
        typer.echo(formatters.fmt_add_error(str(e)), err=True)
        raise typer.Exit(code=2)
```

---

#### B-2. list 명령 확장 (`cli/main.py`)

**변경 내용**:
```python
@app.command(name="list")
def list_todos(
    filter_: Optional[str] = typer.Option(None, "--filter"),
    priority: Optional[str] = typer.Option(None, "--priority"),
    tag: Optional[str] = typer.Option(None, "--tag", help="태그 필터 (단일 태그)"),
) -> None:
    service = _get_service()
    try:
        todos = service.list_todos(status=filter_, priority=priority, tag=tag)
    except ValueError as e:
        typer.echo(formatters.fmt_add_error(str(e)), err=True)
        raise typer.Exit(code=2)
    ...
```

---

#### B-3. 출력 포맷 확장 (`cli/formatters.py`)

**변경 내용**:
```python
def fmt_todo_row(todo: Todo) -> str:
    due = todo.due_date or "-"
    priority = todo.priority or "-"
    tags_str = f"tags=[{', '.join(todo.tags)}]"
    return f"[{todo.id}] {todo.title}  due={due}  priority={priority}  status={todo.status}  {tags_str}"
```

**주의**: `fmt_list_todos()`의 rows 생성 부분도 `fmt_todo_row()` 일관 호출로 통일.

---

### Phase C: 테스트

#### C-1. 신규 단위 테스트 (`tests/unit/test_tag_validation.py`)

| 케이스 | 기대 결과 |
|--------|---------|
| 빈 목록 `[]` | `[]` 반환 |
| 태그 1개 | `["work"]` 반환 |
| 태그 5개 | 정상 반환 |
| 태그 6개 | `ValueError` |
| 빈 문자열 `""` | `ValueError` |
| 21자 태그 | `ValueError` |
| 공백 포함 `"a b"` | `ValueError` |
| `@` 포함 `"a@b"` | `ValueError` |
| 중복 `["a", "a"]` | `["a"]` 반환 |
| 한글 태그 `"작업"` | 정상 반환 |
| 하이픈/언더스코어 `"my-tag_1"` | 정상 반환 |

#### C-2. 기존 단위 테스트 수정

| 파일 | 수정 내용 |
|------|---------|
| `tests/unit/test_add_todo.py` | `tags` 기본값 하위 호환 확인 (기존 호출 방식 그대로 통과 검증) |
| `tests/unit/test_list_todos.py` | `tag=None` 기본 동작 + tag 필터 케이스 추가 |

#### C-3. 통합 테스트 수정/추가

| 파일 | 수정 내용 |
|------|---------|
| `tests/integration/test_cli_add.py` | US1 AC1~AC6 시나리오 추가 |
| `tests/integration/test_cli_list.py` | US2 AC1~AC5 추가, **출력 포맷 `tags=[]` 포함으로 수정** |
| `tests/contract/test_cli_contract.py` | **출력 포맷 `tags=[]` 포함으로 수정** |

#### C-4. 커버리지 목표

- 전체 커버리지 ≥ 90% (현재 95.09% 기준 유지)
- `todo_lib/models.py`, `services.py`, `repository.py`, `cli/main.py`, `cli/formatters.py` 신규 코드 모두 테스트 커버 필수

---

## Risk & Mitigation

| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| 기존 통합/계약 테스트 출력 포맷 불일치 | **높음** | `test_cli_list.py`, `test_cli_contract.py` 출력 비교 문자열 `tags=[]` 포함으로 수정 |
| 기존 DB 마이그레이션 실패 | 낮음 | `_migrate_add_tags_column()` 방어 구현 + 통합 테스트 커버 |
| `tags` property와 ORM 세션 충돌 | 낮음 | `tags_json` 컬럼 직접 조작, property는 순수 Python 래퍼 |
| `fmt_list_todos()` rows 포맷 이중화 | 낮음 | `fmt_todo_row()` 호출로 통일 |

---

## Definition of Done

- [ ] `todo add "X" --tag work` → 태그 포함 항목 생성
- [ ] `todo list` → 모든 항목에 `tags=[...]` 표시
- [ ] `todo list --tag work` → 해당 태그 항목만 출력
- [ ] 기존 `todo add/list/done/delete` (태그 없는 케이스) 동작 유지
- [ ] US1 AC1~AC6, US2 AC1~AC5 모든 Acceptance Scenarios 테스트 통과
- [ ] 전체 커버리지 ≥ 90%
- [ ] Constitution Check 항목 모두 충족
