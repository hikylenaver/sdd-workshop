# Implementation Plan: CLI 기반 ToDo 관리 앱

**Branch**: `001-cli-todo-app` | **Date**: 2026-05-03 | **Spec**: `/specs/001-cli-todo-app/spec.md`
**Input**: Feature specification from `/specs/001-cli-todo-app/spec.md`

## Summary

개인 개발자를 위한 로컬 CLI ToDo 도구를 구현한다. 핵심 기능은 add/list/done/delete이며,
도메인 로직은 `todo_lib/`에 분리하고 `cli/`는 명령 파싱과 출력만 담당한다. 저장소는
서버 없는 SQLite 파일(`~/.todo/todo.db`)을 사용하고, 테스트는 pytest/pytest-cov 기반
테스트 우선 방식으로 진행한다.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: typer, sqlalchemy  
**Storage**: SQLite (로컬 파일 기반, `~/.todo/todo.db`)  
**Testing**: pytest, pytest-cov (Red-Green-Refactor)  
**Target Platform**: 로컬 터미널 환경 (Windows/macOS/Linux)
**Project Type**: CLI application + internal domain library  
**Performance Goals**: 1,000개 항목 목록 조회 3초 이내, 단일 명령 p95 200ms 이내 목표  
**Constraints**:
- 허용 패키지 외 의존성 추가 금지
- 추상 인터페이스(`ITodoRepository` 등) 도입 금지
- REST API/GUI/Web 인터페이스 구현 금지
- 실행 디렉터리 무관한 고정 DB 경로 사용  
**Scale/Scope**: 단일 사용자 로컬 사용, 수천 건 ToDo 항목 규모

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate

- Layer Separation: PASS (`todo_lib/`와 `cli/` 분리 설계 확정)
- Test-First Evidence: PASS (pytest/pytest-cov 기반 테스트 선행 전략 명시)
- Dependency Minimalism: PASS (typer/sqlalchemy + pytest/pytest-cov로 제한)
- Simplicity First: PASS (추상 인터페이스 금지, 직접 클래스/함수 구현)
- CLI Scope Boundary: PASS (명령 계약 add/list/done/delete만 포함)

### Post-Design Re-Check (After Phase 1)

- Layer Separation: PASS (`data-model.md`, `quickstart.md`에 계층 책임 분리 반영)
- Test-First Evidence: PASS (`quickstart.md` 테스트 선행 절차 포함)
- Dependency Minimalism: PASS (`research.md`에 의존성 제한 근거 기록)
- Simplicity First: PASS (contracts/data model에서 과설계 요소 없음)
- CLI Scope Boundary: PASS (`contracts/cli-contract.md`가 CLI 인터페이스만 정의)

## Phase 0: Research Output

- `research.md` 생성 완료
- 모든 기술 선택 항목의 의사결정 근거와 대안 비교 기록 완료
- 미해결 항목(NEEDS CLARIFICATION): 없음

## Phase 1: Design & Contracts Output

- `data-model.md` 생성 완료
- `contracts/cli-contract.md` 생성 완료
- `quickstart.md` 생성 완료

## Project Structure

### Documentation (this feature)

```text
specs/001-cli-todo-app/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
todo_lib/
├── models.py
├── services.py
├── repository.py
└── db.py

cli/
├── main.py
└── formatters.py

tests/
├── unit/
│   ├── test_add_todo.py
│   ├── test_list_todos.py
│   ├── test_mark_done.py
│   └── test_delete_todo.py
├── integration/
│   ├── test_cli_add.py
│   ├── test_cli_list.py
│   ├── test_cli_done.py
│   └── test_cli_delete.py
└── contract/
    └── test_cli_contract.py
```

**Structure Decision**: constitution 원칙에 따라 도메인(`todo_lib`)과 CLI(`cli`)를 분리한
단일 프로젝트 구조를 채택한다. 테스트는 `tests/` 하위에서 유형별로 분리한다.

## Complexity Tracking

위반 없음. 헌법 게이트 전 항목 PASS.
