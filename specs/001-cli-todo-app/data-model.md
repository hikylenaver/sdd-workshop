# Data Model: CLI ToDo App

## Entity: Todo

### Fields
- id: INTEGER, Primary Key, Auto Increment, Not Null
- title: TEXT, Not Null, Length 1..200
- due_date: DATE, Nullable
- priority: TEXT, Nullable, Allowed: high | medium | low
- status: TEXT, Not Null, Default: pending, Allowed: pending | done
- created_at: DATETIME, Not Null
- updated_at: DATETIME, Not Null

## Validation Rules
- title은 공백 제외 길이 1~200자여야 한다.
- due_date가 존재하면 YYYY-MM-DD 형식으로 해석 가능한 날짜여야 한다.
- priority가 존재하면 high/medium/low 중 하나여야 한다.
- done 처리 시 status는 pending -> done으로만 전이한다.
- done 상태에서 done 재요청 시 상태를 유지하고 안내 메시지를 반환한다.

## State Transitions
- create: (없음) -> pending
- mark done: pending -> done
- mark done again: done -> done (idempotent)
- delete: pending|done -> (행 삭제)

## Relationships
- 현재 버전에서는 단일 테이블 모델만 사용한다.
- 외래키 관계는 없다.

## Query Shapes
- list all: ORDER BY id ASC
- filter by status: WHERE status = :status ORDER BY id ASC
- filter by priority: WHERE priority = :priority ORDER BY id ASC
- combined filter: WHERE status = :status AND priority = :priority ORDER BY id ASC
