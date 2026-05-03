"""validate_tags() 함수 단위 테스트."""
import pytest

from todo_lib.services import validate_tags


class TestValidateTags:
    """validate_tags() 검증 함수 테스트."""

    def test_빈_목록_허용(self) -> None:
        """빈 태그 목록은 유효하다."""
        result = validate_tags([])
        assert result == []

    def test_단일_유효한_태그(self) -> None:
        """단일 유효한 태그를 반환한다."""
        result = validate_tags(["work"])
        assert result == ["work"]

    def test_다중_유효한_태그(self) -> None:
        """여러 유효한 태그를 반환한다."""
        result = validate_tags(["work", "urgent", "backend"])
        assert result == ["work", "urgent", "backend"]

    def test_최대_5개_태그_허용(self) -> None:
        """5개 태그는 허용된다."""
        tags = ["tag1", "tag2", "tag3", "tag4", "tag5"]
        result = validate_tags(tags)
        assert result == tags
        assert len(result) == 5

    def test_6개_이상_태그_오류(self) -> None:
        """6개 이상 태그는 ValueError를 발생시킨다."""
        tags = ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"]
        with pytest.raises(ValueError, match="태그는 최대 5개까지"):
            validate_tags(tags)

    def test_빈_태그_항목_오류(self) -> None:
        """빈 태그 항목은 ValueError를 발생시킨다."""
        with pytest.raises(ValueError, match="태그는 빈 값일 수 없습니다"):
            validate_tags(["work", "", "urgent"])

    def test_21자_태그_오류(self) -> None:
        """21자 이상 태그는 ValueError를 발생시킨다."""
        long_tag = "a" * 21  # 21자
        with pytest.raises(ValueError, match="허용되지 않는 문자"):
            validate_tags([long_tag])

    def test_20자_태그_허용(self) -> None:
        """20자 태그는 유효하다."""
        tag = "a" * 20  # 20자
        result = validate_tags([tag])
        assert result == [tag]

    def test_특수문자_포함_오류(self) -> None:
        """특수문자(!@#$%)를 포함한 태그는 ValueError를 발생시킨다."""
        with pytest.raises(ValueError, match="허용되지 않는 문자"):
            validate_tags(["tag@work"])

    def test_한글_태그_허용(self) -> None:
        """한글 태그는 유효하다."""
        result = validate_tags(["업무", "긴급"])
        assert result == ["업무", "긴급"]

    def test_하이픈_언더스코어_허용(self) -> None:
        """하이픈과 언더스코어는 허용된다."""
        result = validate_tags(["work-item", "urgent_task"])
        assert result == ["work-item", "urgent_task"]

    def test_중복_태그_제거(self) -> None:
        """중복된 태그는 제거된다."""
        result = validate_tags(["work", "urgent", "work"])
        assert result == ["work", "urgent"]
        assert len(result) == 2

    def test_공백만_있는_태그_오류(self) -> None:
        """공백만 있는 태그는 유효하지 않다."""
        with pytest.raises(ValueError, match="허용되지 않는 문자"):
            validate_tags(["   "])

    def test_숫자로_시작하는_태그_허용(self) -> None:
        """숫자로 시작하는 태그는 허용된다."""
        result = validate_tags(["2024-task", "99problems"])
        assert result == ["2024-task", "99problems"]
