# Data Model: 002-todo-tag-feature

**Date**: 2026-05-03  
**Status**: Complete

## 엔티티 변경 요약

이 기능은 신규 테이블을 추가하지 않는다. 기존 `todos` 테이블에 `tags_json` 컬럼을 추가한다.

---

## Todo (확장)

**테이블**: `todos`  
**변경**: `tags_json` 컬럼 추가

| 컬럼 | 타입 | Nullable | Default | 설명 |
|------|------|----------|---------|------|
| `id` | INTEGER | NOT NULL | autoincrement | PK |
| `title` | TEXT | NOT NULL | — | 할 일 제목 |
| `due_date` | VARCHAR(10) | NULL | NULL | 마감일 (YYYY-MM-DD) |
| `priority` | VARCHAR(10) | NULL | NULL | 우선순위 |
| `status` | VARCHAR(10) | NOT NULL | `pending` | 상태 |
| `created_at` | DATETIME | NOT NULL | utcnow | 생성 시각 |
| `updated_at` | DATETIME | NOT NULL | utcnow | 수정 시각 |
| `tags_json` ✨ | TEXT | NOT NULL | `'[]'` | JSON 직렬화 태그 목록 |

### tags_json 저장 형식

```json
["work", "urgent"]   // 태그 2개
[]                   // 태그 없음
["한국어-태그"]      // 한글 태그
```

### Python Property 접근

```python
# Todo 인스턴스에서 태그 읽기/쓰기
todo.tags          # list[str] 반환
todo.tags = ["work", "urgent"]  # 직렬화하여 tags_json에 저장
```

---

## 검증 규칙 (도메인 레이어)

태그 검증은 `todo_lib/services.py`의 `validate_tags()` 함수에서 수행한다.

```python
TAG_RE = re.compile(r'^[\w가-힣\-]{1,20}$', re.UNICODE)
MAX_TAGS = 5
```

| 규칙 | 위반 시 |
|------|---------|
| 태그 수 ≤ 5 | `ValueError("태그는 최대 5개까지 허용됩니다.")` |
| 빈 문자열 태그 | `ValueError("태그는 빈 값일 수 없습니다.")` |
| 길이 1~20자 | `ValueError("태그는 1자 이상 20자 이하여야 합니다.")` |
| 허용 문자 위반 | `ValueError("태그에 허용되지 않는 문자가 포함되어 있습니다: ...")` |
| 중복 | 자동 제거 (오류 없음) |

---

## 마이그레이션 전략

```
기존 DB (tags_json 컬럼 없음)
    ↓  앱 시작 시 create_db_engine() 호출
    ↓  _migrate_add_tags_column() 실행
    ↓  PRAGMA table_info(todos) 확인
    ↓  tags_json 컬럼 없으면 ALTER TABLE 실행
기존 항목 tags_json = '[]' (태그 없음으로 유지)
```

신규 DB는 `create_all()`로 컬럼 포함하여 생성된다.

---

## 상태 전이 (변경 없음)

태그는 Todo 항목의 상태 전이(`pending → done`)에 영향을 주지 않는다.

```
pending ──(done 명령)──▶ done
```

태그 있는 항목도 기존과 동일하게 `done`/`delete` 처리된다.

---

## 레이어별 책임 분리

```
cli/main.py          : --tag 옵션 파싱, List[str] 수집
    ↓
todo_lib/services.py : validate_tags() 검증, 중복 제거
    ↓
todo_lib/models.py   : Todo.tags property (직렬화/역직렬화)
    ↓
todo_lib/repository.py : list_all(tag=) Python 레벨 필터
    ↓
SQLite todos.tags_json : JSON 텍스트 저장
```
