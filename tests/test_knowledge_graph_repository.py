import pytest

from backend.app.learning.knowledge_graph.models import (
    KnowledgeConcept,
)
from backend.app.learning.knowledge_graph.repository import (
    KnowledgeGraphRepository,
)


def concept(
    concept_id: str,
    *,
    prerequisites: tuple[
        str,
        ...
    ] = (),
) -> KnowledgeConcept:
    return KnowledgeConcept(
        concept_id=concept_id,
        name=concept_id.replace(
            "-",
            " ",
        ).title(),
        domain="Mathematics",
        strand="Transition",
        level_id="G9-G10",
        prerequisite_concept_ids=(
            prerequisites
        ),
    )


def build_repository(
) -> KnowledgeGraphRepository:
    return KnowledgeGraphRepository(
        [
            concept(
                "integers"
            ),
            concept(
                "fractions"
            ),
            concept(
                "ratios",
                prerequisites=(
                    "fractions",
                ),
            ),
            concept(
                "algebraic-expressions",
                prerequisites=(
                    "integers",
                    "fractions",
                ),
            ),
            concept(
                "linear-equations",
                prerequisites=(
                    "algebraic-expressions",
                ),
            ),
        ]
    )


def test_get_known_concept() -> None:
    repository = (
        build_repository()
    )

    assert (
        repository
        .require("fractions")
        .name
        == "Fractions"
    )


def test_unknown_concept_returns_none() -> None:
    repository = (
        build_repository()
    )

    assert (
        repository.get("unknown")
        is None
    )


def test_duplicate_concepts_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Duplicate",
    ):
        KnowledgeGraphRepository(
            [
                concept("integers"),
                concept("integers"),
            ]
        )


def test_prerequisites_are_returned() -> None:
    repository = (
        build_repository()
    )

    prerequisites = (
        repository.prerequisites_for(
            "algebraic-expressions"
        )
    )

    assert {
        item.concept_id
        for item in prerequisites
    } == {
        "integers",
        "fractions",
    }


def test_dependents_are_returned() -> None:
    repository = (
        build_repository()
    )

    dependents = (
        repository
        .direct_dependents_of(
            "fractions"
        )
    )

    assert {
        item.concept_id
        for item in dependents
    } == {
        "ratios",
        "algebraic-expressions",
    }


def test_new_learner_gets_foundation_concepts() -> None:
    repository = (
        build_repository()
    )

    eligible = (
        repository
        .eligible_concepts(
            mastered_concept_ids=set()
        )
    )

    assert {
        item.concept_id
        for item in eligible
    } == {
        "integers",
        "fractions",
    }


def test_mastery_unlocks_new_concepts() -> None:
    repository = (
        build_repository()
    )

    eligible = (
        repository
        .eligible_concepts(
            mastered_concept_ids={
                "integers",
                "fractions",
            }
        )
    )

    assert {
        item.concept_id
        for item in eligible
    } == {
        "ratios",
        "algebraic-expressions",
    }


def test_descendants_follow_entire_path() -> None:
    repository = (
        build_repository()
    )

    descendants = (
        repository.descendants_of(
            "integers"
        )
    )

    assert {
        item.concept_id
        for item in descendants
    } == {
        "algebraic-expressions",
        "linear-equations",
    }
