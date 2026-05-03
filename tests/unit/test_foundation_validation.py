"""공통 검증 함수 단위 테스트 (T011)."""
import pytest

from todo_lib.services import (
    validate_due_date,
    validate_priority,
    validate_status_filter,
    validate_title,
)


class TestValidateTitle:
    def test_정상_제목_반환(self):
        assert validate_title("보고서 작성") == "보고서 작성"

    def test_앞뒤_공백_제거(self):
        assert validate_title("  작업  ") == "작업"

    def test_빈_문자열_오류(self):
        with pytest.raises(ValueError, match="빈 값"):
            validate_title("")

    def test_공백만_있으면_오류(self):
        with pytest.raises(ValueError, match="빈 값"):
            validate_title("   ")

    def test_200자_경계_허용(self):
        title = "a" * 200
        assert validate_title(title) == title

    def test_201자_초과_오류(self):
        with pytest.raises(ValueError, match="200자 이하"):
            validate_title("a" * 201)


class TestValidateDueDate:
    def test_None_허용(self):
        assert validate_due_date(None) is None

    def test_유효한_날짜_반환(self):
        assert validate_due_date("2026-12-31") == "2026-12-31"

    def test_형식_불일치_오류(self):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            validate_due_date("31-12-2026")

    def test_존재하지_않는_날짜_오류(self):
        with pytest.raises(ValueError):
            validate_due_date("2026-02-30")

    def test_숫자가_아닌_값_오류(self):
        with pytest.raises(ValueError):
            validate_due_date("abcd-ef-gh")


class TestValidatePriority:
    def test_None_허용(self):
        assert validate_priority(None) is None

    def test_high_허용(self):
        assert validate_priority("high") == "high"

    def test_medium_허용(self):
        assert validate_priority("medium") == "medium"

    def test_low_허용(self):
        assert validate_priority("low") == "low"

    def test_허용되지_않는_값_오류(self):
        with pytest.raises(ValueError, match="우선순위"):
            validate_priority("urgent")


class TestValidateStatusFilter:
    def test_None_허용(self):
        assert validate_status_filter(None) is None

    def test_pending_허용(self):
        assert validate_status_filter("pending") == "pending"

    def test_done_허용(self):
        assert validate_status_filter("done") == "done"

    def test_허용되지_않는_값_오류(self):
        with pytest.raises(ValueError, match="상태 필터"):
            validate_status_filter("archived")
