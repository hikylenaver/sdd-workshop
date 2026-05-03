# Research: CLI ToDo App

## Decision 1: Python 3.12 + uv 사용
- Decision: 런타임은 Python 3.12, 패키지 관리는 uv를 사용한다.
- Rationale: 사용자 입력 조건과 일치하며, uv는 잠금 파일 기반 재현성과 빠른 설치를 제공한다.
- Alternatives considered: pip + requirements.txt (재현성 관리 비용 증가), poetry (기능 과다).

## Decision 2: 레이어 분리 구조 고정
- Decision: 비즈니스 레이어는 `todo_lib/`, CLI 레이어는 `cli/`, 테스트는 `tests/`로 분리한다.
- Rationale: constitution의 레이어 분리 원칙을 직접 반영하고, 도메인 테스트를 CLI와 독립적으로 실행할 수 있다.
- Alternatives considered: 단일 `app.py` 구조 (초기 단순하나 테스트/변경 격리 불리).

## Decision 3: 저장소는 SQLite 로컬 파일
- Decision: 데이터 저장소는 SQLite 파일(`~/.todo/todo.db`)을 사용한다.
- Rationale: 서버 없이 로컬 영속성을 만족하고, 검색/필터/정렬에 필요한 질의를 단순하게 처리한다.
- Alternatives considered: JSON 파일 (초기 단순하지만 필터/정렬/동시성 안정성 약함), 원격 DB (범위 초과).

## Decision 4: 최소 의존성 패키지 제한
- Decision: 런타임 의존성은 `typer`, `sqlalchemy`만 사용하고, 개발 의존성은 `pytest`, `pytest-cov`만 사용한다.
- Rationale: 사용자 제약(목록 외 패키지 금지)과 constitution의 최소 의존성 원칙을 동시에 충족한다.
- Alternatives considered: rich, pydantic 등 추가 패키지 (편의성은 있으나 요구사항 위배).

## Decision 5: CLI 프레임워크는 Typer
- Decision: 명령 파싱과 도움말은 Typer로 구현한다.
- Rationale: 타입 힌트 기반 옵션 선언이 간결하고, 지정된 명령 인터페이스를 명확히 반영할 수 있다.
- Alternatives considered: argparse (표준이지만 보일러플레이트 큼), click (직접 제약 조건과 불일치).

## Decision 6: ORM/DB 접근은 SQLAlchemy 2.x
- Decision: SQLite 접근 계층은 SQLAlchemy ORM + Session 단위 트랜잭션을 사용한다.
- Rationale: CRUD 및 필터/정렬 요구를 안정적으로 구현하고 테스트 대역(DB 파일 교체)이 쉽다.
- Alternatives considered: sqlite3 직접 사용 (초기 단순하나 쿼리/매핑 관리 부담 증가).

## Decision 7: 테스트 우선 전략 강제
- Decision: US 단위로 "단위 테스트 -> 통합 테스트 -> 구현" 순서를 강제한다.
- Rationale: constitution의 NON-NEGOTIABLE 원칙 충족, 회귀 방지, 명세 기반 검증 가능.
- Alternatives considered: 구현 후 테스트 (정책 위배).

## Decision 8: 단순 구현 원칙 적용
- Decision: `ITodoRepository` 같은 추상 인터페이스는 도입하지 않고, 구체 클래스/함수로 직접 구현한다.
- Rationale: 사용자의 명시 제약(추상 인터페이스 금지)과 constitution의 단순함 우선 원칙에 부합한다.
- Alternatives considered: 인터페이스 기반 DI 구조 (확장성은 있으나 현재 범위에서 과설계).

## Decision 9: CLI 계약 명세 산출물 유지
- Decision: `/contracts/cli-contract.md`에 명령 시그니처, 옵션, 오류 코드, 출력 의미를 명세한다.
- Rationale: CLI-only 프로젝트에서도 외부 인터페이스는 계약으로 관리해야 테스트와 구현 일치가 쉽다.
- Alternatives considered: 계약 문서 생략 (tasks 단계에서 해석 불일치 위험 증가).
