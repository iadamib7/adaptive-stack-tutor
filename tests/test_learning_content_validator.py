import pytest

from backend.app.content.models import (
    ContentKind,
    ContentSource,
    LearningContentItem,
    LicenseDecision,
)
from backend.app.content.validator import (
    LearningContentValidator,
)


KNOWN = {
    "fractions",
    "integers",
}


def item(
    **overrides,
) -> LearningContentItem:
    values = {
        "content_id": "q-1",
        "concept_id": "fractions",
        "title": "Question",
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


def test_valid_content_has_no_errors() -> None:
    errors = (
        LearningContentValidator()
        .validate(
            items=[
                item()
            ],
            known_concept_ids=KNOWN,
        )
    )

    assert errors == []


def test_unknown_concept_is_rejected() -> None:
    errors = (
        LearningContentValidator()
        .validate(
            items=[
                item(
                    concept_id="unknown"
                )
            ],
            known_concept_ids=KNOWN,
        )
    )

    assert any(
        error.code
        == "unknown_concept"
        for error in errors
    )


def test_unknown_prerequisite_is_rejected() -> None:
    errors = (
        LearningContentValidator()
        .validate(
            items=[
                item(
                    prerequisite_concept_ids=(
                        "missing",
                    )
                )
            ],
            known_concept_ids=KNOWN,
        )
    )

    assert any(
        error.code
        == "unknown_prerequisite"
        for error in errors
    )


def test_external_source_needs_reference() -> None:
    errors = (
        LearningContentValidator()
        .validate(
            items=[
                item(
                    source=(
                        ContentSource.OPENSTAX
                    ),
                    source_reference="",
                )
            ],
            known_concept_ids=KNOWN,
        )
    )

    assert any(
        error.code
        == "missing_source_reference"
        for error in errors
    )


def test_allowed_content_needs_license() -> None:
    errors = (
        LearningContentValidator()
        .validate(
            items=[
                item(
                    license_code=""
                )
            ],
            known_concept_ids=KNOWN,
        )
    )

    assert any(
        error.code
        == "missing_license"
        for error in errors
    )


def test_duplicate_content_is_reported() -> None:
    errors = (
        LearningContentValidator()
        .validate(
            items=[
                item(),
                item(),
            ],
            known_concept_ids=KNOWN,
        )
    )

    assert any(
        error.code
        == "duplicate_content"
        for error in errors
    )


def test_require_valid_raises() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Invalid learning content repository"
        ),
    ):
        LearningContentValidator().require_valid(
            items=[
                item(
                    concept_id="missing"
                )
            ],
            known_concept_ids=KNOWN,
        )
