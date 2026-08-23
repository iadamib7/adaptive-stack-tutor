import pytest

from backend.app.content.models import (
    ContentDifficulty,
    ContentKind,
    ContentSource,
    LearningContentItem,
    LicenseDecision,
)


def item(
    **overrides,
) -> LearningContentItem:
    values = {
        "content_id": "q-001",
        "concept_id": "fractions",
        "title": "Add fractions",
        "kind": ContentKind.QUESTION,
        "source": ContentSource.INTERNAL,
        "license_code": "INTERNAL",
        "license_decision":
            LicenseDecision.ALLOWED,
    }

    values.update(
        overrides
    )

    return LearningContentItem(
        **values
    )


def test_content_has_safe_defaults() -> None:
    content = item()

    assert content.difficulty == (
        ContentDifficulty.MEDIUM
    )

    assert content.active is True


def test_allowed_active_content_is_deliverable() -> None:
    content = item()

    assert content.can_be_delivered is True


def test_review_content_is_not_deliverable() -> None:
    content = item(
        license_decision=(
            LicenseDecision.REVIEW
        )
    )

    assert content.can_be_delivered is False


def test_blocked_content_is_not_deliverable() -> None:
    content = item(
        license_decision=(
            LicenseDecision.BLOCKED
        )
    )

    assert content.can_be_delivered is False


def test_inactive_content_is_not_deliverable() -> None:
    content = item(
        active=False
    )

    assert content.can_be_delivered is False


def test_empty_content_id_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="content_id",
    ):
        item(
            content_id=" "
        )


def test_invalid_estimated_time_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="estimated_time_seconds",
    ):
        item(
            estimated_time_seconds=0
        )
