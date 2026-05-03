# Tasks: CLI 기반 ToDo 관리 앱

**Input**: Design documents from `/specs/001-cli-todo-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-contract.md, quickstart.md

**Tests**: constitution에 따라 테스트는 필수이며, 각 User Story에서 테스트를 먼저 작성하고 실패(Red)를 확인한 뒤 구현한다.

**Organization**: 태스크는 User Story별로 독립 구현/검증 가능하도록 구성한다.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 프로젝트 실행/테스트 기반과 기본 디렉터리 구조 준비

- [ ] T001 `todo_lib/`, `cli/`, `tests/unit/`, `tests/integration/`, `tests/contract/` 디렉터리 및 `__init__.py` 생성
- [ ] T002 `pyproject.toml`에 Python 3.12, runtime 의존성(typer, sqlalchemy), dev 의존성(pytest, pytest-cov), `todo` 스크립트 엔트리 정의
- [ ] T003 [P] `README` 실행 예시를 `specs/001-cli-todo-app/quickstart.md` 기준으로 정렬
- [ ] T004 [P] `tests/conftest.py`에 공통 fixture 골격(임시 DB 경로, CLI runner) 생성

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 모든 User Story 구현 전에 필요한 공통 도메인/영속성 기반 구현

**⚠️ CRITICAL**: 이 단계 완료 전에는 User Story 구현을 시작하지 않는다.

- [ ] T005 `todo_lib/models.py`에 `Todo` 도메인 모델 및 상태/우선순위 상수 정의
- [ ] T006 `todo_lib/db.py`에 SQLite 엔진/세션 팩토리와 기본 DB 경로(`~/.todo/todo.db`) 초기화 구현
- [ ] T007 `todo_lib/repository.py`에 SQLAlchemy 기반 `TodoRepository` 구체 클래스 구현(추상 인터페이스 금지)
- [ ] T008 `todo_lib/services.py`에 `TodoService` 골격 및 공통 검증 함수(제목 길이, 날짜 형식, 우선순위) 구현
- [ ] T009 `cli/formatters.py`에 목록/단건 메시지 출력 포맷 함수 구현
- [ ] T010 `cli/main.py`에 Typer 앱 생성 및 명령 등록 골격(add/list/done/delete) 구현
- [ ] T011 `tests/unit/test_foundation_validation.py`에 공통 검증 함수 단위 테스트 추가
- [ ] T012 `tests/integration/test_foundation_db_path.py`에 고정 DB 경로 및 세션 재실행 영속성 테스트 추가

**Checkpoint**: 공통 기반 준비 완료. User Story 구현 시작 가능.

---

## Phase 3: User Story 1 - ToDo 항목 추가 (Priority: P1) 🎯 MVP

**Goal**: `todo add` 명령으로 유효한 할 일을 생성하고 ID를 부여한다.

**Independent Test**: 빈 저장소에서 `todo add "보고서 작성"` 실행 시 항목이 생성되고 ID가 반환된다. 잘못된 입력은 저장되지 않는다.

### Tests for User Story 1 (REQUIRED)

- [ ] T013 [P] [US1] `tests/contract/test_cli_contract.py`에 `todo add` 시그니처/옵션 계약 테스트 추가
- [ ] T014 [P] [US1] `tests/unit/test_add_todo.py`에 제목/우선순위/날짜 검증 실패 케이스 단위 테스트 추가
- [ ] T015 [P] [US1] `tests/integration/test_cli_add.py`에 add 성공/실패 CLI 통합 테스트 추가

### Implementation for User Story 1

- [ ] T016 [US1] `todo_lib/services.py`에 add 유스케이스 구현(제목 1~200자, due 형식, priority 검증)
- [ ] T017 [US1] `todo_lib/repository.py`에 add 저장 및 자동 증가 ID 반환 로직 구현(삭제 ID 미재사용)
- [ ] T018 [US1] `cli/main.py`에 `todo add "<제목>" [--due] [--priority]` 명령 구현
- [ ] T019 [US1] `cli/formatters.py`에 add 성공/오류 메시지 포맷 구현 및 연결

**Checkpoint**: US1 단독 동작 및 테스트 통과.

---

## Phase 4: User Story 2 - 전체 목록 조회 및 필터링 (Priority: P2)

**Goal**: `todo list`로 전체 조회, 상태/우선순위 필터 조회를 지원한다.

**Independent Test**: 시드 데이터 기준으로 `todo list`, `todo list --filter pending`, `todo list --priority high`가 각각 정확한 결과를 ID 오름차순으로 출력한다.

### Tests for User Story 2 (REQUIRED)

- [ ] T020 [P] [US2] `tests/contract/test_cli_contract.py`에 `todo list` 옵션 계약 테스트 추가
- [ ] T021 [P] [US2] `tests/unit/test_list_todos.py`에 필터 조합/정렬 로직 단위 테스트 추가
- [ ] T022 [P] [US2] `tests/integration/test_cli_list.py`에 빈 목록/전체/필터 CLI 통합 테스트 추가

### Implementation for User Story 2

- [ ] T023 [US2] `todo_lib/repository.py`에 목록 조회 질의 구현(기본 ID ASC, 상태/우선순위 조합 필터)
- [ ] T024 [US2] `todo_lib/services.py`에 list 유스케이스 구현(필터 파라미터 검증 포함)
- [ ] T025 [US2] `cli/main.py`에 `todo list [--filter] [--priority]` 명령 구현
- [ ] T026 [US2] `cli/formatters.py`에 빈 목록/테이블형 목록 출력 포맷 구현

**Checkpoint**: US2 단독 동작 및 테스트 통과.

---

## Phase 5: User Story 3 - 항목 완료 처리 (Priority: P3)

**Goal**: `todo done <id>`로 pending 항목을 done으로 변경하고 idempotent 동작을 보장한다.

**Independent Test**: 미완료 항목 ID를 완료 처리하면 done으로 변경되고, 같은 ID 재실행 시 상태 유지 메시지가 출력된다.

### Tests for User Story 3 (REQUIRED)

- [ ] T027 [P] [US3] `tests/contract/test_cli_contract.py`에 `todo done <id>` 계약 테스트 추가
- [ ] T028 [P] [US3] `tests/unit/test_mark_done.py`에 상태 전이/재요청/id 미존재 단위 테스트 추가
- [ ] T029 [P] [US3] `tests/integration/test_cli_done.py`에 CLI 완료 처리 통합 테스트 추가

### Implementation for User Story 3

- [ ] T030 [US3] `todo_lib/repository.py`에 done 업데이트 및 대상 조회 로직 구현
- [ ] T031 [US3] `todo_lib/services.py`에 done 유스케이스 구현(idempotent 처리 포함)
- [ ] T032 [US3] `cli/main.py`에 `todo done <id>` 명령 구현
- [ ] T033 [US3] `cli/formatters.py`에 done 성공/이미 완료/미존재 메시지 포맷 구현

**Checkpoint**: US3 단독 동작 및 테스트 통과.

---

## Phase 6: User Story 4 - 항목 삭제 (Priority: P4)

**Goal**: `todo delete <id>`로 pending/done 구분 없이 항목을 삭제한다.

**Independent Test**: 항목 삭제 후 목록에서 사라지고, 미존재 ID 삭제 시 오류를 반환한다.

### Tests for User Story 4 (REQUIRED)

- [ ] T034 [P] [US4] `tests/contract/test_cli_contract.py`에 `todo delete <id>` 계약 테스트 추가
- [ ] T035 [P] [US4] `tests/unit/test_delete_todo.py`에 삭제 성공/미존재 단위 테스트 추가
- [ ] T036 [P] [US4] `tests/integration/test_cli_delete.py`에 CLI 삭제 통합 테스트 추가

### Implementation for User Story 4

- [ ] T037 [US4] `todo_lib/repository.py`에 delete 로직 구현(상태 무관 삭제)
- [ ] T038 [US4] `todo_lib/services.py`에 delete 유스케이스 구현
- [ ] T039 [US4] `cli/main.py`에 `todo delete <id>` 명령 구현
- [ ] T040 [US4] `cli/formatters.py`에 delete 성공/미존재 메시지 포맷 구현

**Checkpoint**: US4 단독 동작 및 테스트 통과.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 전체 스토리에 공통 영향을 주는 마감 품질 작업

- [ ] T041 [P] `tests/contract/test_cli_contract.py`에 Exit Code(0/1/2) 공통 검증 케이스 보강
- [ ] T042 `tests/integration/` 전체 실행 시나리오 테스트 추가(세션 재실행 영속성 포함)
- [ ] T043 [P] `specs/001-cli-todo-app/quickstart.md` 명령 예시를 실제 구현 옵션과 동기화
- [ ] T044 `pyproject.toml`의 pytest-cov 설정 정리 및 커버리지 임계치(예: 90%) 설정
- [ ] T045 `README`에 설치/실행/테스트/DB 경로/제약사항(의존성 추가 금지) 문서화

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): 즉시 시작 가능
- Foundational (Phase 2): Setup 완료 후 시작, 모든 User Story의 선행 조건
- User Stories (Phase 3~6): Foundational 완료 후 시작 가능
- Polish (Phase 7): 모든 목표 User Story 완료 후 수행

### User Story Dependencies

- US1 (P1): Foundational 이후 즉시 시작 가능 (MVP)
- US2 (P2): Foundational 이후 시작 가능, US1과 독립 검증 가능
- US3 (P3): Foundational 이후 시작 가능, 테스트 fixture로 독립 검증 가능
- US4 (P4): Foundational 이후 시작 가능, 테스트 fixture로 독립 검증 가능

### Within Each User Story

- 테스트 작성/실패 확인이 구현보다 먼저
- 도메인 로직(`todo_lib`) 구현 후 CLI 어댑터(`cli`) 연결
- 스토리별 테스트 전부 통과 후 다음 우선순위로 이동

---

## Parallel Opportunities

- Setup: T003, T004 병렬 가능
- US1: T013~T015 병렬 가능
- US2: T020~T022 병렬 가능
- US3: T027~T029 병렬 가능
- US4: T034~T036 병렬 가능
- Polish: T041, T043 병렬 가능

---

## Parallel Example: User Story 1

```bash
# US1 테스트를 먼저 병렬로 작성
Task: T013 tests/contract/test_cli_contract.py의 add 계약 테스트
Task: T014 tests/unit/test_add_todo.py의 add 검증 단위 테스트
Task: T015 tests/integration/test_cli_add.py의 add 통합 테스트
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Phase 1~2 완료
2. US1 테스트 먼저 작성하고 실패 확인
3. US1 구현 후 테스트 통과
4. add 명령 단독 데모

### Incremental Delivery

1. US1 완료 후 커밋/검증
2. US2 추가 후 커밋/검증
3. US3 추가 후 커밋/검증
4. US4 추가 후 커밋/검증
5. Polish로 마감

### Commit Strategy

- 모든 태스크는 1커밋 단위로 분해되어 있다.
- 커밋 메시지는 `task: T0xx <short-description>` 형태를 권장한다.
- [P] 태스크라도 파일 충돌이 없을 때만 병렬로 진행한다.
