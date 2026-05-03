# Quickstart: CLI ToDo App

## 1. 환경 준비

1. Python 3.12 확인
2. uv 설치 확인
3. 프로젝트 루트에서 의존성 동기화

```powershell
uv sync
```

## 2. 실행

```powershell
uv run todo add "문서 작성" --priority high
uv run todo list
uv run todo done 1
uv run todo delete 1
```

## 3. 테스트 우선 워크플로

1. 먼저 테스트 작성
2. 실패 확인(Red)
3. 최소 구현(Green)
4. 리팩터링(Refactor)

```powershell
uv run pytest -q
uv run pytest --cov=todo_lib --cov=cli --cov-report=term-missing
```

## 4. 디렉터리 구조

```text
todo_lib/
cli/
tests/
```

## 5. 저장소 파일

- SQLite 파일: `~/.todo/todo.db`
- 앱은 실행 디렉터리와 무관하게 위 경로를 사용

## 6. 디버깅 체크포인트

- add 후 list에 즉시 표시되는지 확인
- done 재실행 시 idempotent 메시지 확인
- delete 후 list에서 제거 확인
- 잘못된 날짜/우선순위 입력 시 오류 코드 2 반환 확인
