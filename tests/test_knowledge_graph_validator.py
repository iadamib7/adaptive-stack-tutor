import pytest

from backend.app.learning.knowledge_graph.models import (
    KnowledgeConcept,
)
from backend.app.learning.knowledge_graph.validator import (
    KnowledgeGraphValidator,
)


def concept(
    concept_id: str,
    *,
    prerequisites: tuple[
        str,
        ...
    ] = (),
    remediation: tuple[
        str,
        ...
    ] = (),
) -> KnowledgeConcept:
    return KnowledgeConcept(
        concept_id=concept_id,
        name=concept_id,
        domain="Mathematics",
        strand="Transition",
        level_id="G9-G10",
        prerequisite_concept_ids=(
            prerequisites
        ),
        remediation_concept_ids=(
            remediation
        ),
    )


def test_valid_graph_has_no_errors() -> None:
    concepts = [
        concept(
            "integers"
        ),
        concept(
            "algebra",
            prerequisites=(
                "integers",
            ),
        ),
    ]

    errors = (
        KnowledgeGraphValidator()
        .validate(
            concepts
        )
    )

    assert errors == []


def test_unknown_prerequisite_is_reported() -> None:
    concepts = [
        concept(
            "algebra",
            prerequisites=(
                "missing",
            ),
        )
    ]

    errors = (
        KnowledgeGraphValidator()
        .validate(
            concepts
        )
    )

    assert any(
        error.code
        == "unknown_reference"
        for error in errors
    )


def test_unknown_remediation_is_reported() -> None:
    concepts = [
        concept(
            "algebra",
            remediation=(
                "missing",
            ),
        )
    ]

    errors = (
        KnowledgeGraphValidator()
        .validate(
            concepts
        )
    )

    assert any(
        error.code
        == "unknown_reference"
        for error in errors
    )


def test_prerequisite_cycle_is_reported() -> None:
    concepts = [
        concept(
            "a",
            prerequisites=("c",),
        ),
        concept(
            "b",
            prerequisites=("a",),
        ),
        concept(
            "c",
            prerequisites=("b",),
        ),
    ]

    errors = (
        KnowledgeGraphValidator()
        .validate(
            concepts
        )
    )

    assert any(
        error.code
        == "prerequisite_cycle"
        for error in errors
    )


def test_duplicate_concept_is_reported() -> None:
    concepts = [
        concept("integers"),
        concept("integers"),
    ]

    errors = (
        KnowledgeGraphValidator()
        .validate(
            concepts
        )
    )

    assert any(
        error.code
        == "duplicate_concept"
        for error in errors
    )


def test_require_valid_raises_for_bad_graph() -> None:
    with pytest.raises(
        ValueError,
        match="Invalid knowledge graph",
    ):
        KnowledgeGraphValidator().require_valid(
            [
                concept(
                    "algebra",
                    prerequisites=(
                        "missing",
                    ),
                )
            ]
        )
