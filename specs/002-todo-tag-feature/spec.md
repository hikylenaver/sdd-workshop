# Feature Specification: Todo 태그 기능 추가

**Feature Branch**: `002-todo-tag-feature`
**Created**: 2026-05-03
**Status**: Draft
**Related Issues**: #1, #2
**Input**: 기존 Todo 앱에 태그 생성/필터 기능 추가 (이슈 #1, #2)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 태그를 포함한 Todo 항목 추가 (Priority: P1)

사용자는 Todo를 생성할 때 태그를 선택적으로 붙일 수 있다. 태그는 항목을 분류하고 나중에 빠르게 찾기 위한 수단이다. 기존 태그 없는 생성 흐름은 그대로 유지되어야 한다.

**Why this priority**: 태그 필터링(US2)의 선행 조건이며, 기존 add 명령 확장이므로 MVP를 구성하는 핵심 스토리다.

**Independent Test**: 빈 저장소에서 `todo add "보고서 작성" --tag work --tag urgent` 실행 후 `todo list`로 태그가 표시되는지 확인한다. 태그 없는 `todo add "메모"` 도 여전히 정상 동작해야 한다.

**Acceptance Scenarios**:

1. **Given** 빈 저장소, **When** `todo add "작업" --tag work` 실행, **Then** 항목이 생성되고 `work` 태그와 함께 ID가 출력된다.
2. **Given** 빈 저장소, **When** `todo add "작업"` 태그 없이 실행, **Then** 기존과 동일하게 항목이 생성된다.
3. **Given** 빈 저장소, **When** `todo add "작업" --tag work --tag urgent --tag meeting --tag review --tag personal` (5개), **Then** 항목이 정상 생성된다.
4. **Given** 빈 저장소, **When** `todo add "작업" --tag t1 --tag t2 --tag t3 --tag t4 --tag t5 --tag t6` (6개), **Then** 오류 메시지와 exit code 2를 반환하고 저장하지 않는다.
5. **Given** 빈 저장소, **When** 21자 태그를 포함해 추가, **Then** 오류 메시지와 exit code 2를 반환하고 저장하지 않는다.
6. **Given** 빈 저장소, **When** 빈 문자열 태그 `--tag ""` 포함해 추가, **Then** 오류 메시지와 exit code 2를 반환한다.

---

### User Story 2 - 태그로 목록 필터링 (Priority: P2)

사용자는 `todo list --tag <태그명>`으로 특정 태그가 붙은 항목만 빠르게 조회할 수 있다. 기존 `--filter`/`--priority` 필터와 조합도 가능하다.

**Why this priority**: US1이 완료된 이후에만 의미 있는 기능이다. 태그 데이터가 없으면 필터링도 없다.

**Independent Test**: 시드 데이터(`work`, `personal` 태그 항목 혼재) 기준으로 `todo list --tag work` 실행 시 `work` 태그가 붙은 항목만 ID 오름차순으로 반환된다.

**Acceptance Scenarios**:

1. **Given** `work` 태그 2개 + `personal` 태그 1개 항목, **When** `todo list --tag work`, **Then** `work` 태그 항목 2개만 출력된다.
2. **Given** 태그 있는 항목과 없는 항목 혼재, **When** `todo list --tag work`, **Then** `work` 태그 항목만 출력된다 (태그 없는 항목 제외).
3. **Given** 항목 존재, **When** `todo list --tag 없는태그`, **Then** "저장된 항목이 없습니다" 메시지를 출력한다.
4. **Given** 항목 존재, **When** `todo list --tag work --filter pending`, **Then** `work` 태그이면서 pending 상태인 항목만 출력된다.
5. **Given** 항목 존재, **When** `todo list --tag work --priority high`, **Then** `work` 태그이면서 high 우선순위인 항목만 출력된다.

---

### Edge Cases

- 동일 태그를 중복 지정하면(`--tag work --tag work`) 어떻게 처리하는가? → 중복 제거 후 1개로 저장한다.
- 태그 이름의 대소문자 구분은? → 대소문자를 구분한다(`Work`와 `work`는 다른 태그).
- 기존에 태그 없이 저장된 항목을 `--tag` 필터로 조회하면? → 해당 항목은 결과에서 제외된다.
- 태그가 있는 항목의 완료(done)/삭제(delete) 동작은? → 기존과 동일하게 태그와 무관하게 동작한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Todo 추가 시 `--tag <태그명>` 옵션을 0회 이상 반복 지정할 수 있어야 한다.
- **FR-002**: 한 항목에 허용되는 태그는 최대 5개이며, 초과 시 오류 메시지를 출력하고 저장을 거부해야 한다.
- **FR-003**: 각 태그는 1자 이상 20자 이하의 문자열이어야 하며, 빈 태그나 20자 초과 태그는 오류로 처리해야 한다.
- **FR-004**: 중복 태그가 지정된 경우 자동으로 중복을 제거하고 저장한다.
- **FR-005**: 태그 없이 Todo를 생성하는 기존 흐름은 변경 없이 유지되어야 한다.
- **FR-006**: `todo list --tag <태그명>` 옵션으로 해당 태그를 가진 항목만 필터링해 조회할 수 있어야 한다.
- **FR-007**: `--tag` 필터는 기존 `--filter`(상태) 및 `--priority` 필터와 조합하여 사용할 수 있어야 한다.
- **FR-008**: 목록 출력 시 각 항목의 태그 정보가 함께 표시되어야 한다.
- **FR-009**: 기존 add/list/done/delete 명령의 동작 및 exit code는 태그 기능 추가 후에도 변경되지 않아야 한다.
- **FR-010**: 태그가 없는 기존 저장 항목에 대해 `--tag` 필터를 적용하면 해당 항목은 결과에서 제외된다.

### Constitution Alignment *(mandatory)*

- **CA-001 (CLI Scope)**: 태그 기능 인터페이스는 CLI 옵션(`--tag`) 형태로만 제공하며, REST API·GUI·웹 인터페이스는 범위 외다.
- **CA-002 (Test-First)**: US1·US2의 Acceptance Scenarios가 테스트 코드 작성의 기준이 되며, 구현 전 테스트가 먼저 작성되어야 한다.
- **CA-003 (Layer Separation)**: 태그 도메인 로직(검증·저장·필터링)은 `todo_lib/`에, CLI 입출력은 `cli/`에 분리 구현해야 한다.
- **CA-004 (Dependency Review)**: 태그 저장을 위해 추가 외부 패키지를 사용하지 않는다. 기존 SQLAlchemy로 구현 가능한 범위 내에서 처리한다.

### Key Entities

- **Tag**: 단일 태그 문자열. 속성: 태그명(1~20자), 연결된 TodoItem의 ID.
- **TodoItem (확장)**: 기존 TodoItem에 태그 목록(0~5개)이 추가된다. 태그와의 관계는 1:N (하나의 Todo가 여러 태그 보유).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 태그가 포함된 Todo 항목 추가 작업을 명령 1회로 30초 이내에 완료할 수 있다.
- **SC-002**: `todo list --tag <태그명>` 실행 시 1,000개 항목 기준 3초 이내에 결과를 출력한다.
- **SC-003**: 태그 필터링 결과가 대상 항목만 정확히 반환하며 누락·중복이 없다.
- **SC-004**: 기존 태그 없는 add/list/done/delete 명령이 태그 기능 추가 후에도 100% 동일하게 동작한다.
- **SC-005**: 잘못된 태그 입력(태그 6개 초과, 21자 이상, 빈 태그)에 대해 100% 오류 메시지가 출력되고 데이터는 변경되지 않는다.
- **SC-006**: US1·US2의 Acceptance Scenarios를 모두 통과하는 자동화 테스트가 존재한다.

## Clarifications

### Session 2026-05-03

- Q: 중복 태그 처리 방식? → A: 자동 중복 제거 후 1개로 저장
- Q: 태그 대소문자 구분? → A: 대소문자 구분 (Work ≠ work)
- Q: 태그 저장 방식(별도 테이블 vs. 직렬화)? → A: SQLAlchemy 기반 별도 테이블로 정규화 저장 (추가 외부 패키지 없음)

## Assumptions

- 태그는 알파벳·숫자·한글·하이픈·언더스코어 등 유니코드 문자 허용이며, 공백만 있는 태그는 빈 태그로 처리한다.
- 태그 수정(edit) 기능은 이번 기능 범위 밖이다. Todo 항목 자체의 수정 기능도 v1 범위 외다.
- 기존 DB 스키마(`todos` 테이블)에는 영향 없이 별도 `tags` 테이블(또는 연결 테이블)을 추가한다.
- 이슈 #1(태그 추가)과 #2(태그 필터)는 단일 feature 브랜치에서 함께 구현한다.
