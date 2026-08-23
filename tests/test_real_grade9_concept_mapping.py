from pathlib import Path

from backend.app.content.ingestion.concept_mapper import (
    ContentConceptMapper,
)
from backend.app.content.ingestion.grade9_stack_rules import (
    GRADE9_STACK_MAPPING_RULES,
)
from backend.app.content.ingestion.stack_importer import (
    StackContentImporter,
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


def mapper(
) -> ContentConceptMapper:
    concepts = load_knowledge_graph(
        GRAPH_PATH
    )

    return ContentConceptMapper(
        knowledge_graph=(
            KnowledgeGraphRepository(
                concepts
            )
        ),
        rules=(
            GRADE9_STACK_MAPPING_RULES
        ),
    )


def records_by_id():
    records = (
        StackContentImporter()
        .import_file(
            STACK_EXPORT
        )
    )

    return {
        record.external_id: record
        for record in records
    }


def test_real_integer_question_maps_to_integer_operations() -> None:
    records = records_by_id()

    decision = mapper().map_record(
        records["207582"]
    )

    assert decision.concept_id == (
        "integer-operations"
    )


def test_real_indices_question_maps_to_indices() -> None:
    records = records_by_id()

    decision = mapper().map_record(
        records["206946"]
    )

    assert decision.concept_id == (
        "indices"
    )


def test_real_matrix_question_maps_to_matrices() -> None:
    records = records_by_id()

    decision = mapper().map_record(
        records["207288"]
    )

    assert decision.concept_id == (
        "matrices"
    )


def test_real_gradient_question_maps_to_gradient() -> None:
    records = records_by_id()

    decision = mapper().map_record(
        records["207350"]
    )

    assert decision.concept_id == (
        "gradient"
    )


def test_mapping_pipeline_maps_multiple_real_topics() -> None:
    records = list(
        records_by_id().values()
    )

    decisions = (
        mapper().map_records(
            records
        )
    )

    mapped_ids = {
        decision.concept_id
        for decision in decisions
        if decision.is_mapped
    }

    assert "integer-operations" in mapped_ids
    assert "indices" in mapped_ids
    assert "matrices" in mapped_ids
    assert "mensuration" in mapped_ids
    assert "trigonometry" in mapped_ids
