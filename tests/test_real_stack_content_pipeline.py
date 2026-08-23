from pathlib import Path

from backend.app.content.ingestion.concept_mapper import (
    ContentConceptMapper,
)
from backend.app.content.ingestion.grade9_stack_rules import (
    GRADE9_STACK_MAPPING_RULES,
)
from backend.app.content.ingestion.stack_pipeline import (
    StackContentPipeline,
)
from backend.app.learning.knowledge_graph.loader import (
    load_knowledge_graph,
)
from backend.app.learning.knowledge_graph.repository import (
    KnowledgeGraphRepository,
)


STACK_EXPORT = Path(
    "resources/raw/kenya/grade9/"
    "grade9_questions.xml"
)

GRAPH_PATH = Path(
    "resources/knowledge_graph/"
    "grade9_grade10_transition.json"
)


def build_pipeline() -> StackContentPipeline:
    concepts = load_knowledge_graph(
        GRAPH_PATH
    )

    graph = KnowledgeGraphRepository(
        concepts
    )

    mapper = ContentConceptMapper(
        knowledge_graph=graph,
        rules=GRADE9_STACK_MAPPING_RULES,
    )

    return StackContentPipeline(
        knowledge_graph=graph,
        concept_mapper=mapper,
    )


def test_pipeline_imports_real_questions() -> None:
    result = build_pipeline().build(
        STACK_EXPORT
    )

    assert result.imported_count >= 70


def test_pipeline_maps_real_questions() -> None:
    result = build_pipeline().build(
        STACK_EXPORT
    )

    assert result.mapped_count > 0

    assert result.mapped_count == len(
        result.items
    )


def test_pipeline_leaves_some_content_unmapped() -> None:
    result = build_pipeline().build(
        STACK_EXPORT
    )

    assert result.unmapped_count > 0


def test_pipeline_counts_are_consistent() -> None:
    result = build_pipeline().build(
        STACK_EXPORT
    )

    assert (
        result.mapped_count
        + result.unmapped_count
        + result.review_required_count
        == result.imported_count
    )


def test_pipeline_creates_stack_content_ids() -> None:
    result = build_pipeline().build(
        STACK_EXPORT
    )

    assert result.items

    assert all(
        item.content_id.startswith(
            "stack:"
        )
        for item in result.items
    )


def test_imported_stack_content_stays_under_review() -> None:
    result = build_pipeline().build(
        STACK_EXPORT
    )

    assert result.items

    assert all(
        item.can_be_delivered is False
        for item in result.items
    )


def test_repository_contains_mapped_content() -> None:
    repository = (
        build_pipeline().repository(
            STACK_EXPORT
        )
    )

    all_items = repository.all_items()

    assert len(all_items) > 0


def test_repository_can_group_by_concept() -> None:
    repository = (
        build_pipeline().repository(
            STACK_EXPORT
        )
    )

    # Imported STACK material is deliberately still
    # in license review, so include non-deliverable
    # content for this repository audit.
    integer_items = (
        repository.for_concept(
            "integer-operations",
            deliverable_only=False,
        )
    )

    indices_items = (
        repository.for_concept(
            "indices",
            deliverable_only=False,
        )
    )

    assert integer_items
    assert indices_items
