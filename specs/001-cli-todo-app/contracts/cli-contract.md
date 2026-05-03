# CLI Contract: todo

## Scope
- 인터페이스 형태: 로컬 터미널 CLI
- 범위 제외: REST API, GUI, Web UI

## Command Signatures

### 1) Add
- Signature: `todo add "<제목>" [--due YYYY-MM-DD] [--priority high|medium|low]`
- Behavior:
  - 성공: 항목 생성, `pending` 상태, 새 ID 출력
  - 실패: 제목 길이/날짜/우선순위 오류 시 생성 거부
- Exit Code:
  - 0: 성공
  - 2: 입력 검증 실패

### 2) List
- Signature: `todo list [--filter done|pending] [--priority high|medium|low]`
- Behavior:
  - 기본 정렬: ID 오름차순
  - 필터 없음: 전체 출력
  - `--filter`: 상태 필터
  - `--priority`: 우선순위 필터
  - 두 옵션 동시 사용 가능
- Exit Code:
  - 0: 성공
  - 2: 입력 검증 실패

### 3) Done
- Signature: `todo done <id>`
- Behavior:
  - pending -> done
  - 이미 done이면 상태 유지 + 안내 메시지
  - id가 없으면 오류
- Exit Code:
  - 0: 성공(이미 done 포함)
  - 1: 리소스 없음(id 미존재)
  - 2: 입력 검증 실패

### 4) Delete
- Signature: `todo delete <id>`
- Behavior:
  - pending/done 구분 없이 삭제
  - id가 없으면 오류
- Exit Code:
  - 0: 성공
  - 1: 리소스 없음(id 미존재)
  - 2: 입력 검증 실패

## Output Contract
- 기본 출력: 사람이 읽기 쉬운 텍스트
- 오류 출력: 원인(입력 오류/미존재)을 명시
- 목록 출력 컬럼: id, title, due_date, priority, status

## Persistence Contract
- DB 파일 위치: `~/.todo/todo.db`
- 같은 사용자 세션 재실행 시 데이터 유지
