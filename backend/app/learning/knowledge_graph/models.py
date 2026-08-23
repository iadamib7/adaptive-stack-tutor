from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ConceptDifficultyBand(
    str,
    Enum,
):
    FOUNDATION = "foundation"
    DEVELOPING = "developing"
    PROFICIENT = "proficient"
    ADVANCED = "advanced"


@dataclass(frozen=True)
class KnowledgeConcept:
    """
    One learnable skill or mathematical concept in the
    curriculum-agnostic knowledge graph.
    """

    concept_id: str
    name: str
    domain: str
    strand: str
    level_id: str

    description: str = ""

    difficulty_band: ConceptDifficultyBand = (
        ConceptDifficultyBand.DEVELOPING
    )

    prerequisite_concept_ids: tuple[str, ...] = (
        field(
            default_factory=tuple
        )
    )

    remediation_concept_ids: tuple[str, ...] = (
        field(
            default_factory=tuple
        )
    )

    extension_concept_ids: tuple[str, ...] = (
        field(
            default_factory=tuple
        )
    )

    mastery_threshold: float = 0.8

    recommended_question_count: int = 5

    curriculum_tags: tuple[str, ...] = (
        field(
            default_factory=tuple
        )
    )

    def __post_init__(self) -> None:
        if not self.concept_id.strip():
            raise ValueError(
                "concept_id must not be empty."
            )

        if not self.name.strip():
            raise ValueError(
                "Concept name must not be empty."
            )

        if not self.domain.strip():
            raise ValueError(
                "Concept domain must not be empty."
            )

        if not self.strand.strip():
            raise ValueError(
                "Concept strand must not be empty."
            )

        if not self.level_id.strip():
            raise ValueError(
                "Concept level_id must not be empty."
            )

        if not (
            0.0
            < self.mastery_threshold
            <= 1.0
        ):
            raise ValueError(
                "mastery_threshold must be greater "
                "than 0 and at most 1."
            )

        if (
            self.recommended_question_count
            <= 0
        ):
            raise ValueError(
                "recommended_question_count must "
                "be positive."
            )

        if (
            self.concept_id
            in self.prerequisite_concept_ids
        ):
            raise ValueError(
                "A concept cannot be its own "
                "prerequisite."
            )
