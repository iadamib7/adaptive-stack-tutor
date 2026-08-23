import pytest

from backend.app.content.models import (
    ContentDifficulty,
    ContentKind,
    ContentSource,
    LearningContentItem,
    LicenseDecision,
)
from backend.app.content.repository import (
    LearningContentRepository,
)


def item(
    content_id: str,
    *,
    concept_id: str = "fractions",
    kind: ContentKind = (
        ContentKind.QUESTION
    ),
    difficulty: ContentDifficulty = (
        ContentDifficulty.MEDIUM
    ),
    deliverable: bool = True,
    mastery: bool = False,
    variant_group: str | None = None,
) -> LearningContentItem:
    return LearningContentItem(
        content_id=content_id,
        concept_id=concept_id,
        title=content_id,
        kind=kind,
        source=ContentSource.INTERNAL,
        difficulty=difficulty,
        license_code="INTERNAL",
        license_decision=(
            LicenseDecision.ALLOWED
            if deliverable
            else LicenseDecision.REVIEW
        ),
        is_mastery_evidence=mastery,
        variant_group_id=variant_group,
    )


def repository(
) -> LearningContentRepository:
    return LearningContentRepository(
        [
            item(
                "fraction-easy-1",
                difficulty=(
                    ContentDifficulty.EASY
                ),
            ),
            item(
                "fraction-medium-1"
            ),
            item(
                "fraction-mastery-1",
                difficulty=(
                    ContentDifficulty.MASTERY
                ),
                mastery=True,
            ),
            item(
                "fraction-review",
                deliverable=False,
            ),
            item(
                "fraction-hint",
                kind=ContentKind.HINT,
            ),
            item(
                "variant-a",
                variant_group="vg-1",
            ),
            item(
                "variant-b",
                variant_group="vg-1",
            ),
            item(
                "integer-question",
                concept_id="integers",
            ),
        ]
    )


def test_duplicate_content_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Duplicate",
    ):
        LearningContentRepository(
            [
                item("same"),
                item("same"),
            ]
        )


def test_repository_gets_known_item() -> None:
    repo = repository()

    assert (
        repo.require(
            "fraction-medium-1"
        ).concept_id
        == "fractions"
    )


def test_concept_query_excludes_review_items() -> None:
    repo = repository()

    ids = {
        content.content_id
        for content in repo.for_concept(
            "fractions"
        )
    }

    assert "fraction-review" not in ids


def test_difficulty_filter_works() -> None:
    repo = repository()

    questions = (
        repo.questions_for_concept(
            "fractions",
            difficulty=(
                ContentDifficulty.EASY
            ),
        )
    )

    assert [
        content.content_id
        for content in questions
    ] == [
        "fraction-easy-1"
    ]


def test_mastery_items_are_found() -> None:
    repo = repository()

    ids = {
        content.content_id
        for content
        in repo.mastery_items_for(
            "fractions"
        )
    }

    assert ids == {
        "fraction-mastery-1"
    }


def test_hints_are_found() -> None:
    repo = repository()

    ids = {
        content.content_id
        for content
        in repo.hints_for(
            "fractions"
        )
    }

    assert ids == {
        "fraction-hint"
    }


def test_seen_content_can_be_excluded() -> None:
    repo = repository()

    questions = (
        repo.questions_for_concept(
            "fractions"
        )
    )

    remaining = repo.excluding_seen(
        questions,
        {
            "fraction-easy-1",
            "fraction-medium-1",
        },
    )

    ids = {
        content.content_id
        for content in remaining
    }

    assert "fraction-easy-1" not in ids
    assert "fraction-medium-1" not in ids


def test_variants_can_be_discovered() -> None:
    repo = repository()

    variants = repo.variants_of(
        "variant-a"
    )

    assert [
        content.content_id
        for content in variants
    ] == [
        "variant-b"
    ]
