# CLI ToDo App

로컬 터미널에서 사용하는 개인용 ToDo 관리 도구.

## 설치 및 실행 환경

- Python 3.12+
- 가상환경(`.venv`) 활성화 후 사용

```powershell
# 의존성 설치
.\.venv\Scripts\python.exe -m pip install typer sqlalchemy

# 프로젝트 설치 (editable)
.\.venv\Scripts\python.exe -m pip install -e .
```

## 명령어

```powershell
# 항목 추가
todo add "보고서 작성"
todo add "미팅 준비" --due 2026-12-31 --priority high

# 전체 목록 조회
todo list

# 필터 조회
todo list --filter pending
todo list --filter done
todo list --priority high
todo list --filter pending --priority high

# 완료 처리
todo done 1

# 삭제
todo delete 1
```

## 테스트 실행

```powershell
# 전체 테스트 + 커버리지
.\.venv\Scripts\python.exe -m pytest

# 커버리지 없이 빠른 실행
.\.venv\Scripts\python.exe -m pytest --no-cov -q
```

## DB 경로

- 기본 경로: `~/.todo/todo.db` (SQLite)
- 테스트용 경로 변경: 환경변수 `TODO_DB_PATH` 설정

## 제약사항

- 허용 패키지(typer, sqlalchemy, pytest, pytest-cov) 외 의존성 추가 금지
- REST API / GUI / Web 인터페이스 구현 범위 외
- 멀티 유저 동시 접근 미지원 (단일 사용자 로컬 도구)
