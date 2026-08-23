import pytest

from backend.app.learning.knowledge_graph.models import (
    ConceptDifficultyBand,
    KnowledgeConcept,
)


def build_concept(
    **overrides,
) -> KnowledgeConcept:
    values = {
        "concept_id": "fractions",
        "name": "Fractions",
        "domain": "Mathematics",
        "strand": "Number",
        "level_id": "transition",
    }

    values.update(
        overrides
    )

    return KnowledgeConcept(
        **values
    )


def test_concept_has_safe_defaults() -> None:
    concept = build_concept()

    assert concept.mastery_threshold == 0.8

    assert (
        concept.recommended_question_count
        == 5
    )

    assert concept.difficulty_band == (
        ConceptDifficultyBand.DEVELOPING
    )


def test_concept_can_have_prerequisites() -> None:
    concept = build_concept(
        prerequisite_concept_ids=(
            "whole-numbers",
            "division",
        )
    )

    assert concept.prerequisite_concept_ids == (
        "whole-numbers",
        "division",
    )


def test_empty_concept_id_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="concept_id",
    ):
        build_concept(
            concept_id=" "
        )


def test_invalid_mastery_threshold_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="mastery_threshold",
    ):
        build_concept(
            mastery_threshold=1.5
        )


def test_nonpositive_question_count_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="recommended_question_count",
    ):
        build_concept(
            recommended_question_count=0
        )


def test_self_prerequisite_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="own prerequisite",
    ):
        build_concept(
            prerequisite_concept_ids=(
                "fractions",
            )
        )
