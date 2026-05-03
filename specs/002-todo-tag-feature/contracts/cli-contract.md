# CLI Contract: todo (v2 - 태그 기능 추가)

**Version**: 2.0.0  
**Changed From**: specs/001-cli-todo-app/contracts/cli-contract.md  
**Date**: 2026-05-03

## Scope
- 인터페이스 형태: 로컬 터미널 CLI
- 범위 제외: REST API, GUI, Web UI

## Command Signatures

### 1) Add *(변경)*
- Signature: `todo add "<제목>" [--due YYYY-MM-DD] [--priority high|medium|low] [--tag <태그>]...`
- **신규**: `--tag <태그>` — 0회 이상 반복 가능 (예: `--tag work --tag urgent`)
- Behavior:
  - 성공: 항목 생성, `pending` 상태, 새 ID 출력
  - 태그 없음: 기존과 동일하게 동작 (하위 호환)
  - 실패: 제목·날짜·우선순위·태그 오류 시 생성 거부
- Exit Code:
  - 0: 성공
  - 2: 입력 검증 실패 (태그 6개 초과, 21자 이상, 빈 태그, 허용 외 문자 포함)

### 2) List *(변경)*
- Signature: `todo list [--filter done|pending] [--priority high|medium|low] [--tag <태그>]`
- **신규**: `--tag <태그>` — 단일 태그 필터 (복수 지정 불가, v1 범위 외)
- Behavior:
  - 기본 정렬: ID 오름차순
  - `--tag`: 해당 태그를 가진 항목만 출력
  - `--tag` + `--filter` + `--priority` 동시 사용 가능
  - 결과 없음: "저장된 항목이 없습니다." 출력
- Exit Code:
  - 0: 성공
  - 2: 입력 검증 실패

### 3) Done *(변경 없음)*
- Signature: `todo done <id>`
- Exit Code: 0(성공), 1(미존재), 2(검증 실패)

### 4) Delete *(변경 없음)*
- Signature: `todo delete <id>`
- Exit Code: 0(성공), 1(미존재), 2(검증 실패)

## Output Contract

### 목록 출력 (변경)
각 항목 행 끝에 `tags=[...]` 형태가 추가된다.

**Before (v1)**:
```
[1] 보고서 작성  due=2026-05-10  priority=high  status=pending
```

**After (v2)**:
```
[1] 보고서 작성  due=2026-05-10  priority=high  status=pending  tags=[work, urgent]
[2] 메모         due=-           priority=-      status=pending  tags=[]
```

- 태그 있음: `tags=[work, urgent]` (삽입 순서 유지)
- 태그 없음: `tags=[]`
- 기존 `fmt_todo_row()` 출력 포맷 끝에 `  tags=[...]` 추가

### 추가 성공 출력 *(변경 없음)*
```
추가됨 (ID: 1): 보고서 작성
```

### 오류 출력 *(변경 없음)*
```
오류: 태그는 최대 5개까지 허용됩니다.
```

## Persistence Contract
- DB 파일 위치: `~/.todo/todo.db`
- 태그: `todos.tags_json` 컬럼 (TEXT, JSON 직렬화)
- 기존 DB 호환: 앱 시작 시 `tags_json` 컬럼 자동 추가 (기존 항목 `tags=[]` 유지)

## Tag Validation Contract

| 조건 | 동작 |
|------|------|
| 태그 수 0개 | 정상 (태그 없음으로 저장) |
| 태그 수 1~5개 | 정상 저장 (중복 자동 제거) |
| 태그 수 6개 이상 | 오류, exit 2 |
| 태그 길이 1~20자 | 정상 |
| 태그 길이 0자 또는 21자 이상 | 오류, exit 2 |
| 허용 문자: 알파벳·숫자·한글·`-`·`_` | 정상 |
| 공백·특수문자 포함 | 오류, exit 2 |
| 중복 태그 지정 | 중복 제거 후 저장 (경고 없음) |
| 대소문자 구분 | `Work` ≠ `work` (구분함) |
