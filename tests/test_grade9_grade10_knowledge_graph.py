from pathlib import Path

from backend.app.learning.knowledge_graph.loader import (
    load_knowledge_graph,
)
from backend.app.learning.knowledge_graph.repository import (
    KnowledgeGraphRepository,
)


GRAPH_PATH = Path(
    "resources/knowledge_graph/"
    "grade9_grade10_transition.json"
)


def build_repository(
) -> KnowledgeGraphRepository:
    concepts = load_knowledge_graph(
        GRAPH_PATH
    )

    return KnowledgeGraphRepository(
        concepts
    )


def test_transition_graph_loads() -> None:
    concepts = load_knowledge_graph(
        GRAPH_PATH
    )

    assert len(concepts) >= 25


def test_foundational_number_sense_has_no_prerequisites() -> None:
    repository = build_repository()

    concept = repository.require(
        "number-sense"
    )

    assert (
        concept.prerequisite_concept_ids
        == ()
    )


def test_algebra_requires_foundations() -> None:
    repository = build_repository()

    concept = repository.require(
        "algebraic-expressions"
    )

    assert {
        *concept.prerequisite_concept_ids
    } == {
        "integer-operations",
        "fractions",
        "order-of-operations",
    }


def test_indices_does_not_unlock_matrices_directly() -> None:
    repository = build_repository()

    dependents = (
        repository.direct_dependents_of(
            "indices"
        )
    )

    dependent_ids = {
        concept.concept_id
        for concept in dependents
    }

    assert "matrices" not in dependent_ids


def test_matrices_requires_algebraic_readiness() -> None:
    repository = build_repository()

    matrices = repository.require(
        "matrices"
    )

    assert {
        *matrices.prerequisite_concept_ids
    } == {
        "algebraic-expressions",
        "simultaneous-equations",
    }


def test_trigonometry_requires_geometry_foundations() -> None:
    repository = build_repository()

    trig = repository.require(
        "trigonometry"
    )

    assert {
        *trig.prerequisite_concept_ids
    } == {
        "pythagorean-theorem",
        "similarity",
    }


def test_empty_mastery_starts_with_true_foundations() -> None:
    repository = build_repository()

    eligible = repository.eligible_concepts(
        mastered_concept_ids=set()
    )

    ids = {
        concept.concept_id
        for concept in eligible
    }

    assert ids == {
        "number-sense",
        "relation-foundations",
    }



def test_mastering_number_sense_unlocks_multiple_paths() -> None:
    repository = build_repository()

    eligible = repository.eligible_concepts(
        mastered_concept_ids={
            "number-sense"
        }
    )

    ids = {
        concept.concept_id
        for concept in eligible
    }

    assert "integer-operations" in ids
    assert "fractions" in ids
    assert "decimals" in ids
    assert "angles" in ids


def test_graph_has_multiple_domains() -> None:
    concepts = load_knowledge_graph(
        GRAPH_PATH
    )

    strands = {
        concept.strand
        for concept in concepts
    }

    assert "Number" in strands
    assert "Algebra" in strands
    assert "Geometry" in strands
    assert "Measurement" in strands
    assert "Statistics" in strands
