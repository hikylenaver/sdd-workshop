<!--
Sync Impact Report
- Version change: 0.0.0 -> 1.0.0
- Modified principles:
	- template PRINCIPLE_1_NAME -> I. 레이어 분리
	- template PRINCIPLE_2_NAME -> II. 테스트 우선 (NON-NEGOTIABLE)
	- template PRINCIPLE_3_NAME -> III. 최소 의존성
	- template PRINCIPLE_4_NAME -> IV. 단순함 우선
	- template PRINCIPLE_5_NAME -> V. CLI 도구 구현 범위
- Added sections:
	- 추가 제약 사항
	- 개발 워크플로 및 품질 게이트
- Removed sections:
	- 없음
- Templates requiring updates:
	- ✅ .specify/templates/plan-template.md
	- ✅ .specify/templates/spec-template.md
	- ✅ .specify/templates/tasks-template.md
	- ⚠ pending: .specify/templates/commands/*.md (현재 경로 자체가 없어 점검 불가)
- Deferred TODOs:
	- 없음
-->

# Todo CLI Productivity Constitution

## Core Principles

### I. 레이어 분리
비즈니스 로직은 CLI 입력/출력 처리 코드와 분리된 독립 레이어에서 구현해야 한다.
도메인 규칙은 UI 포맷, 표준 출력 형식, 인자 파싱 구현에 의존하면 안 된다. 모든
도메인 동작은 독립 테스트가 가능해야 하며, CLI 어댑터는 도메인 레이어를 호출하는
조립 책임만 가진다. 이는 변경 비용을 줄이고 회귀 위험을 최소화하기 위한 필수
원칙이다.

### II. 테스트 우선 (NON-NEGOTIABLE)
모든 기능 변경은 테스트 코드 작성이 구현 코드보다 먼저 수행되어야 한다. 테스트가
없는 구현 코드는 허용되지 않으며, 구현 시작 전 실패하는 테스트(Red)를 반드시
확인해야 한다. 구현 완료 기준은 테스트 통과(Green)와 중복 제거/가독성 개선
(Refactor)까지 포함한다. 이 원칙은 품질 게이트이며 예외는 없다.

### III. 최소 의존성
외부 패키지를 추가하기 전에 표준 라이브러리 또는 기존 의존성으로 해결 가능한지
검토해야 한다. 새 의존성 도입 시 필요성, 유지보수 비용, 보안 리스크를 문서화해야
하며, 불필요하거나 중복되는 패키지 추가를 금지한다. 의존성 수를 억제해 빌드 안정성
및 장기 유지보수성을 확보한다.

### IV. 단순함 우선
현재 요구사항으로 정당화되지 않는 추상화 레이어, 범용 프레임워크화, 조기 일반화를
금지한다. 구현은 명확하고 직접적인 흐름을 우선하며, 복잡성은 검증된 필요가 있을 때만
추가할 수 있다. 설계 선택 시 더 단순한 대안을 먼저 평가하고, 복잡한 대안을 채택한
경우 근거를 명시해야 한다.

### V. CLI 도구 구현 범위
이 프로젝트의 제품 형태는 터미널에서 실행되는 CLI 기반 ToDo 생산성 관리 도구로
한정한다. REST API 서버, GUI 애플리케이션, 웹 인터페이스 구현은 프로젝트 범위에서
제외한다. 요구사항/계획/태스크는 모두 CLI 사용자 흐름 중심으로 정의되어야 하며,
범위 외 제안은 별도 프로젝트로 분리한다.

## 추가 제약 사항

- 실행 환경은 로컬 터미널 사용 시나리오를 기준으로 정의한다.
- 사용자 가치 전달 단위는 CLI 명령 단위 기능으로 분해한다.
- 문서, spec, plan, tasks는 본 헌법의 범위 제약과 품질 원칙을 명시적으로 반영해야
	한다.

## 개발 워크플로 및 품질 게이트

- 모든 구현 태스크는 테스트 태스크와 1:1 또는 N:1로 추적 가능해야 한다.
- Code Review는 다음 항목을 반드시 확인해야 한다: 레이어 분리, 테스트 우선 증거,
	의존성 추가 근거, 단순성 유지, CLI 범위 준수.
- Constitution Check를 통과하지 못한 spec/plan/tasks는 승인할 수 없다.
- 범위 외 요구가 확인되면 구현이 아니라 요구 재정의 또는 별도 backlog로 이관한다.

## Governance

이 헌법은 프로젝트의 상위 규범이며 하위 문서(spec, plan, tasks, 구현 지침)보다
우선한다. 개정은 변경 제안서, 영향도(기존 산출물/워크플로/품질 게이트), 마이그레이션
계획을 포함해야 하며, 승인 후 버전 규칙에 따라 반영한다.

버전 정책은 Semantic Versioning을 따른다.
- MAJOR: 원칙 제거 또는 하위 호환 불가능한 거버넌스 재정의.
- MINOR: 신규 원칙/섹션 추가 또는 강제 규칙의 실질적 확장.
- PATCH: 의미 변화 없는 문구 명확화, 오탈자 수정, 표현 개선.

컴플라이언스 리뷰는 모든 PR/병합 시점에 수행하며, 위반 사항은 수정 또는 예외 승인
기록 없이 병합할 수 없다.

**Version**: 1.0.0 | **Ratified**: 2026-05-02 | **Last Amended**: 2026-05-02
