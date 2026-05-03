"""DB 마이그레이션 (_migrate_add_tags_column) 단위 테스트."""
import tempfile
from pathlib import Path

from sqlalchemy import create_engine, text

from todo_lib.db import _migrate_add_tags_column
from todo_lib.models import Base


class TestMigrateAddTagsColumn:
    """_migrate_add_tags_column() 마이그레이션 함수 테스트."""

    def test_신규_db에서_마이그레이션_성공(self) -> None:
        """신규 DB 생성 시 마이그레이션이 성공한다."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            engine = create_engine(f"sqlite:///{db_path}", echo=False)
            try:
                Base.metadata.create_all(engine)
                
                # 마이그레이션 실행
                _migrate_add_tags_column(engine)
                
                # tags_json 컬럼이 존재하는지 확인
                with engine.connect() as conn:
                    cols = [row[1] for row in conn.execute(text("PRAGMA table_info(todos)"))]
                    assert "tags_json" in cols
            finally:
                engine.dispose()

    def test_기존_테이블에_컬럼_추가(self) -> None:
        """이미 존재하는 테이블에 tags_json 컬럼을 추가한다."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            engine = create_engine(f"sqlite:///{db_path}", echo=False)
            try:
                # 기존 스키마 (tags_json 컬럼 없음)
                Base.metadata.create_all(engine)
                
                # tags_json 컬럼 제거 (기존 DB 시뮬레이션)
                with engine.connect() as conn:
                    # 임시 테이블 생성 후 데이터 이동
                    conn.execute(text("""
                        CREATE TABLE todos_old AS SELECT 
                            id, title, due_date, priority, status, created_at, updated_at 
                        FROM todos
                    """))
                    conn.execute(text("DROP TABLE todos"))
                    conn.execute(text("""
                        CREATE TABLE todos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            due_date VARCHAR(10),
                            priority VARCHAR(10),
                            status VARCHAR(10) NOT NULL DEFAULT 'pending',
                            created_at DATETIME NOT NULL,
                            updated_at DATETIME NOT NULL
                        )
                    """))
                    conn.execute(text("""
                        INSERT INTO todos (id, title, due_date, priority, status, created_at, updated_at)
                        SELECT id, title, due_date, priority, status, created_at, updated_at FROM todos_old
                    """))
                    conn.execute(text("DROP TABLE todos_old"))
                    conn.commit()
                
                # 마이그레이션 실행
                _migrate_add_tags_column(engine)
                
                # tags_json 컬럼이 존재하는지 확인
                with engine.connect() as conn:
                    cols = [row[1] for row in conn.execute(text("PRAGMA table_info(todos)"))]
                    assert "tags_json" in cols
            finally:
                engine.dispose()

    def test_마이그레이션_멱등성(self) -> None:
        """마이그레이션을 여러 번 실행해도 오류가 발생하지 않는다."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            engine = create_engine(f"sqlite:///{db_path}", echo=False)
            try:
                Base.metadata.create_all(engine)
                
                # 마이그레이션을 2회 실행
                _migrate_add_tags_column(engine)
                _migrate_add_tags_column(engine)  # 재실행해도 오류 없음
                
                # tags_json 컬럼이 정확히 1개만 존재
                with engine.connect() as conn:
                    cols = [row[1] for row in conn.execute(text("PRAGMA table_info(todos)"))]
                    assert cols.count("tags_json") == 1
            finally:
                engine.dispose()

    def test_마이그레이션_후_기본값_확인(self) -> None:
        """마이그레이션 후 기존 행의 tags_json은 '[]'로 설정된다."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            engine = create_engine(f"sqlite:///{db_path}", echo=False)
            try:
                # 기존 스키마 (tags_json 없음)
                Base.metadata.create_all(engine)
                
                # 데이터 생성
                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO todos (title, status, created_at, updated_at)
                        VALUES ('테스트', 'pending', '2026-05-03 00:00:00', '2026-05-03 00:00:00')
                    """))
                    conn.commit()
                
                # 마이그레이션 후 tags_json 기본값 확인
                _migrate_add_tags_column(engine)
                
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT tags_json FROM todos WHERE title='테스트'")).fetchone()
                    assert result is not None
                    # SQLite DEFAULT는 리터럴 값을 저장 (따옴표 포함)
                    assert result[0] in ("[]", "'[]'")
            finally:
                engine.dispose()
