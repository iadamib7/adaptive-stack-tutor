from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ContentKind(
    str,
    Enum,
):
    QUESTION = "question"
    HINT = "hint"
    WORKED_EXAMPLE = "worked_example"
    EXPLANATION = "explanation"


class ContentSource(
    str,
    Enum,
):
    STACK = "stack"
    OPENSTAX = "openstax"
    OER = "oer"
    TEACHER = "teacher"
    GENERATED = "generated"
    INTERNAL = "internal"


class ContentDifficulty(
    str,
    Enum,
):
    FOUNDATION = "foundation"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    MASTERY = "mastery"


class LicenseDecision(
    str,
    Enum,
):
    ALLOWED = "allowed"
    REVIEW = "review"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class LearningContentItem:
    """
    One reusable learning resource linked to a knowledge
    concept.

    The adaptive engine should depend on this common
    representation rather than on a particular question
    provider.
    """

    content_id: str
    concept_id: str
    title: str
    kind: ContentKind
    source: ContentSource

    source_reference: str = ""

    difficulty: ContentDifficulty = (
        ContentDifficulty.MEDIUM
    )

    skill_tags: tuple[str, ...] = field(
        default_factory=tuple
    )

    misconception_tags: tuple[str, ...] = field(
        default_factory=tuple
    )

    prerequisite_concept_ids: tuple[str, ...] = field(
        default_factory=tuple
    )

    license_code: str = ""

    license_url: str = ""

    attribution: str = ""

    license_decision: LicenseDecision = (
        LicenseDecision.REVIEW
    )

    estimated_time_seconds: int | None = None

    is_mastery_evidence: bool = False

    variant_group_id: str | None = None

    active: bool = True

    metadata: tuple[
        tuple[str, str],
        ...
    ] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        if not self.content_id.strip():
            raise ValueError(
                "content_id must not be empty."
            )

        if not self.concept_id.strip():
            raise ValueError(
                "concept_id must not be empty."
            )

        if not self.title.strip():
            raise ValueError(
                "Content title must not be empty."
            )

        if (
            self.estimated_time_seconds
            is not None
            and self.estimated_time_seconds
            <= 0
        ):
            raise ValueError(
                "estimated_time_seconds must "
                "be positive."
            )

        if (
            self.content_id
            in self.prerequisite_concept_ids
        ):
            raise ValueError(
                "Content ID cannot be used as "
                "a prerequisite concept ID."
            )

    @property
    def can_be_delivered(
        self,
    ) -> bool:
        return (
            self.active
            and self.license_decision
            == LicenseDecision.ALLOWED
        )
