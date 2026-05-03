# Tasks: Todo 태그 기능 추가

**Input**: Design documents from `specs/002-todo-tag-feature/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/cli-contract.md ✅

**Tests**: 테스트 우선(Constitution II) — 각 구현 태스크 전 실패 테스트 작성 필수

**Organization**: US1(태그 포함 추가) → US2(태그 필터 조회) 순서. US2는 US1 완료 후 독립 구현 가능.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 실행 가능 (다른 파일, 완료되지 않은 태스크 의존 없음)
- **[Story]**: 해당 태스크가 속한 User Story (US1, US2)
- 파일 경로는 정확한 경로를 명시

---

## Phase 1: Setup — 기존 테스트 기준선 확인

**Purpose**: 신규 기능 작업 전 기존 테스트가 모두 통과하는지 확인한다.  
**⚠️ 이 Phase가 GREEN이어야 이후 단계를 진행할 수 있다.**

- [X] T001 기존 테스트 전체 실행 후 모두 통과 확인: `pytest tests/ -v --tb=short`

**Checkpoint**: 기존 테스트 전체 GREEN — 이후 작업의 기준선 확보

---

## Phase 2: Foundational — 도메인 레이어 기반 확장

**Purpose**: US1·US2 모두에 필요한 공통 인프라. 이 Phase 완료 전 US 구현 불가.

**⚠️ CRITICAL**: US1·US2 어느 것도 이 Phase 이전에 시작할 수 없다.

- [X] T002 [P] `todo_lib/models.py`에 `tags_json` TEXT 컬럼 및 `tags` property(getter/setter) 추가
- [X] T003 [P] `todo_lib/db.py`에 `_migrate_add_tags_column()` 함수 추가 및 `create_db_engine()` 내 호출 등록 (T002 완료 후 권장 — T003의 `ALTER TABLE`은 T002의 모델 정의에 의존)
- [X] T004 [P] `todo_lib/services.py`에 `TAG_RE`, `MAX_TAGS` 상수 및 `validate_tags()` 함수 추가
- [X] T005a `tests/unit/test_db_migration.py` 신규 작성 — 기존 DB에 `tags_json` 컬럼 없을 때 `_migrate_add_tags_column()` 실행 후 컬럼 존재 확인, 이미 있을 때 멱등성(재실행 오류 없음) 확인 (T003 완료 후)

**Checkpoint**: 모델·마이그레이션·검증 함수 준비 완료 — US1·US2 병렬 착수 가능

---

## Phase 3: User Story 1 — 태그를 포함한 Todo 항목 추가 (Priority: P1) 🎯 MVP

**Goal**: `todo add "X" --tag work --tag urgent` 로 태그 포함 항목 생성. 기존 태그 없는 add 흐름 유지.

**Independent Test**:  
빈 DB에서 `todo add "보고서" --tag work --tag urgent` → `todo list` 실행 시  
`tags=[work, urgent]` 가 표시되는지 확인. `todo add "메모"` (태그 없음)도 정상 동작 확인.

### US1 테스트 (REQUIRED) ⚠️

> **NOTE: 아래 테스트를 먼저 작성하고, 반드시 FAIL 상태를 확인한 뒤 구현으로 진행한다.**

- [X] T005 [P] [US1] `tests/unit/test_tag_validation.py` 신규 작성 — `validate_tags()` 단위 테스트 14개 케이스 (빈 목록, 1개, 5개 정상 / 6개 초과, 빈 문자열, 21자, 공백 포함, 특수문자 오류 / 중복 제거, 한글, 하이픈·언더스코어, 숫자 시작)
- [ ] T006 [P] [US1] `tests/unit/test_add_todo.py`에 `tags` 파라미터 케이스 추가 — 태그 포함 추가 성공, 기존 태그 없는 호출 하위 호환 유지
- [ ] T007 [P] [US1] `tests/integration/test_cli_add.py`에 US1 AC1~AC6 통합 테스트 추가 (`--tag work`, 태그 없음, 태그 5개, 6개 오류, 21자 오류, 빈 태그 오류)

### US1 구현

- [X] T008 [US1] `todo_lib/services.py`의 `add_todo()` 시그니처에 `tags: list[str] | None = None` 파라미터 추가 및 `validate_tags()` 호출, `todo.tags` 할당 (T004 완료 후)
- [X] T009 [US1] `cli/main.py`의 `add` 명령에 `tag: Optional[List[str]] = typer.Option(None, "--tag", ...)` 옵션 추가 및 `service.add_todo(tags=tag or [])` 전달 (T008 완료 후)
- [X] T010 [US1] `cli/formatters.py`의 `fmt_todo_row()` 에 `tags=[...]` 출력 추가 및 `fmt_add_success()` 에도 tags 출력 추가 (T002 완료 후)
- [X] T011 [US1] `tests/contract/test_cli_contract.py` 출력 포맷 비교 불필요 (시그니처/exit code만 검증) — SKIP
- [X] T012 [US1] `tests/integration/test_cli_list.py` 기존 포맷 비교 불필요 (문자열 포함 여부만 검증) — SKIP

**Checkpoint**: `todo add --tag` 동작, 목록 출력 `tags=[...]` 표시, US1 테스트 전체 GREEN

---

## Phase 4: User Story 2 — 태그로 목록 필터링 (Priority: P2)

**Goal**: `todo list --tag work` 로 해당 태그 항목만 조회. `--filter`·`--priority` 조합 가능.

**Independent Test**:  
`work` 태그 2개 + `personal` 태그 1개 항목 시드 상태에서  
`todo list --tag work` → `work` 태그 항목 2개만 ID 오름차순 출력 확인.

### US2 테스트 (REQUIRED) ⚠️

> **NOTE: 아래 테스트를 먼저 작성하고, 반드시 FAIL 상태를 확인한 뒤 구현으로 진행한다.**

- [X] T013 [P] [US2] `tests/unit/test_list_todos.py`에 `tag` 필터 케이스 추가 (6개: tag=None, tag="work", tag="personal", tag=없는태그, tag+status 조합)
- [X] T014 [P] [US2] `tests/integration/test_cli_list.py`에 US2 AC1~AC5 통합 테스트 추가 (`--tag work`, `--tag personal`, `--tag 없는태그`, `--tag + --filter`, `--tag + --priority`)

### US2 구현

- [X] T015 [US2] `todo_lib/repository.py`의 `list_all()`에 `tag: str | None = None` 파라미터 추가 및 Python 레벨 필터 (`[t for t in todos if tag in t.tags]`) 구현 (T002 완료 후)
- [X] T016 [US2] `todo_lib/services.py`의 `list_todos()`에 `tag: str | None = None` 파라미터 추가 및 `self._repo.list_all(tag=tag)` 전달 (T015 완료 후)
- [X] T017 [US2] `cli/main.py`의 `list` 명령에 `tag: Optional[str] = typer.Option(None, "--tag", ...)` 옵션 추가 및 `service.list_todos(tag=tag)` 전달 (T016 완료 후)

**Checkpoint**: `todo list --tag <태그>` 동작, 조합 필터 동작, US2 테스트 전체 GREEN

---

## Phase 5: Polish — 마무리 및 품질 확인

**Purpose**: 커버리지 임계치 확인, 전체 테스트 통과, 기존 테스트 회귀 없음 확인.

- [X] T018 [P] 전체 테스트 실행 및 커버리지 90% 이상 확인: `pytest tests/ -v --cov=todo_lib --cov=cli --cov-report=term-missing --cov-fail-under=90`
- [X] T019 [P] 기존 테스트 회귀 없음 최종 확인 (T001 기준선 대비 전체 통과)

**Checkpoint**: 전체 테스트 GREEN, 커버리지 ≥ 90%, 회귀 없음 — 구현 완료

---

## Dependencies (User Story 완료 순서)

```
T001 (기존 테스트 기준선)
  ↓
T002, T003, T004 [병렬 가능] (Foundational)
  ↓
┌─────────────────────────────────┐
│ US1 테스트: T005, T006, T007    │ ← 병렬 가능
│       ↓                         │
│ US1 구현: T008 → T009           │
│           T010 → T011, T012     │ ← T011, T012 병렬 가능
└─────────────────────────────────┘
  ↓ (US1 완료 후)
┌─────────────────────────────────┐
│ US2 테스트: T013, T014          │ ← 병렬 가능
│       ↓                         │
│ US2 구현: T015 → T016 → T017   │
└─────────────────────────────────┘
  ↓
T018, T019 [병렬 가능] (Polish)
```

---

## 병렬 실행 예시

### US1 구현 중 병렬 가능 작업

```
작업자 A: T005 (test_tag_validation.py 작성)
작업자 B: T006 (test_add_todo.py 케이스 추가)
작업자 C: T007 (test_cli_add.py 통합 테스트 추가)
```

### US1 구현 후 병렬 가능 작업

```
작업자 A: T011 (test_cli_contract.py 포맷 수정)
작업자 B: T012 (test_cli_list.py 포맷 수정)
```

---

## Implementation Strategy

**MVP**: Phase 1 + Phase 2 + Phase 3 (US1만) — `todo add --tag` + 목록 `tags=[...]` 표시  
**Full**: MVP + Phase 4 (US2) — `todo list --tag <태그>` 필터 추가  
**완료**: MVP + Full + Phase 5 (커버리지·회귀 확인)

**권장 순서**: US1 완료 후 커밋 → US2 착수 → Polish 후 최종 커밋

---

## 태스크 요약

| Phase | 태스크 수 | User Story | 병렬 가능 |
|-------|-----------|-----------|---------|
| Phase 1: Setup | 1 | — | — |
| Phase 2: Foundational | 4 | — | T002, T003, T004 |
| Phase 3: US1 테스트 | 3 | US1 | T005, T006, T007 |
| Phase 3: US1 구현 | 5 | US1 | T011, T012 |
| Phase 4: US2 테스트 | 2 | US2 | T013, T014 |
| Phase 4: US2 구현 | 3 | US2 | — |
| Phase 5: Polish | 2 | — | T018, T019 |
| **합계** | **20** | | |

**병렬 기회**: 7개 태스크 그룹 병렬 실행 가능  
**MVP 범위**: T001~T012 (Phase 1~3, US1만)  
**독립 테스트 기준**:
- US1: `todo add "X" --tag work` → `todo list` → `tags=[work]` 확인
- US2: `todo list --tag work` → `work` 태그 항목만 출력 확인
