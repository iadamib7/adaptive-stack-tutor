from pathlib import Path

from backend.app.content.ingestion.concept_mapper import (
    ContentConceptMapper,
)
from backend.app.content.ingestion.numbas.converter import (
    NumbasContentConverter,
)
from backend.app.content.ingestion.numbas.pipeline import (
    NumbasBulkContentPipeline,
)
from backend.app.content.ingestion.numbas.rules import (
    NUMBAS_TRANSITION_MAPPING_RULES,
)
from backend.app.content.sources.default_registry import (
    DEFAULT_CONTENT_SOURCE_REGISTRY,
)
from backend.app.learning.knowledge_graph.loader import (
    load_knowledge_graph,
)
from backend.app.learning.knowledge_graph.repository import (
    KnowledgeGraphRepository,
)


SOURCE_DIR = Path(
    "resources/raw/numbas"
)

CATALOG = (
    SOURCE_DIR
    / "catalog.json"
)

GRAPH = Path(
    "resources/knowledge_graph/"
    "grade9_grade10_transition.json"
)


def build_pipeline():
    graph = KnowledgeGraphRepository(
        load_knowledge_graph(
            GRAPH
        )
    )

    known_ids = {
        concept.concept_id
        for concept
        in graph.all_concepts()
    }

    mapper = ContentConceptMapper(
        knowledge_graph=graph,
        rules=(
            NUMBAS_TRANSITION_MAPPING_RULES
        ),
    )

    converter = (
        NumbasContentConverter(
            source_registry=(
                DEFAULT_CONTENT_SOURCE_REGISTRY
            ),
            known_transition_concept_ids=(
                known_ids
            ),
        )
    )

    return NumbasBulkContentPipeline(
        concept_mapper=mapper,
        converter=converter,
    )


def test_bulk_pipeline_discovers_real_question() -> None:
    result = build_pipeline().build(
        source_directory=SOURCE_DIR,
        catalog_path=CATALOG,
    )

    assert result.discovered_count >= 1


def test_bulk_pipeline_accepts_real_fraction_question() -> None:
    result = build_pipeline().build(
        source_directory=SOURCE_DIR,
        catalog_path=CATALOG,
    )

    ids = {
        item.content_id
        for item in result.items
    }

    assert "numbas:24060" in ids


def test_bulk_pipeline_real_question_is_deliverable() -> None:
    result = build_pipeline().build(
        source_directory=SOURCE_DIR,
        catalog_path=CATALOG,
    )

    item = next(
        item
        for item in result.items
        if item.content_id
        == "numbas:24060"
    )

    assert item.can_be_delivered


def test_bulk_pipeline_maps_fraction_concept() -> None:
    result = build_pipeline().build(
        source_directory=SOURCE_DIR,
        catalog_path=CATALOG,
    )

    item = next(
        item
        for item in result.items
        if item.content_id
        == "numbas:24060"
    )

    assert item.concept_id == (
        "fractions"
    )
