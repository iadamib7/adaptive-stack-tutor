from pathlib import Path

from backend.app.content.ingestion.concept_mapper import (
    ContentConceptMapper,
)
from backend.app.content.ingestion.numbas.converter import (
    NumbasContentConverter,
)
from backend.app.content.ingestion.numbas.importer import (
    NumbasContentImporter,
)
from backend.app.content.ingestion.numbas.models import (
    NumbasQuestionMetadata,
    NumbasQuestionStatus,
)
from backend.app.content.ingestion.numbas.rules import (
    NUMBAS_TRANSITION_MAPPING_RULES,
)
from backend.app.content.models import (
    LicenseDecision,
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


SOURCE = Path(
    "resources/raw/numbas/"
    "question-24060-addition-and-"
    "subtraction-of-fractions.exam"
)

GRAPH = Path(
    "resources/knowledge_graph/"
    "grade9_grade10_transition.json"
)


def build_graph():
    return KnowledgeGraphRepository(
        load_knowledge_graph(
            GRAPH
        )
    )


def build_record():
    return (
        NumbasContentImporter()
        .import_file(
            SOURCE
        )
    )


def build_mapping(
    graph,
    record,
):
    mapper = ContentConceptMapper(
        knowledge_graph=graph,
        rules=(
            NUMBAS_TRANSITION_MAPPING_RULES
        ),
    )

    return mapper.map_record(
        record
    )


def build_metadata():
    return NumbasQuestionMetadata(
        question_id="24060",
        title=(
            "Addition and subtraction "
            "of fractions"
        ),
        source_url=(
            "https://numbas.mathcentre.ac.uk/"
            "question/24060/"
        ),
        project_name=(
            "Transition to university"
        ),
        status=(
            NumbasQuestionStatus.READY
        ),
        license_code=(
            "CC-BY-4.0"
        ),
        license_url=(
            "https://creativecommons.org/"
            "licenses/by/4.0/"
        ),
        tags=(
            "fractions",
            "adding fractions",
            "subtracting fractions",
        ),
        author_names=(
            "Christian Lawson-Perfect",
            "Lauren Richards",
        ),
    )


def test_real_numbas_question_becomes_deliverable() -> None:
    graph = build_graph()

    record = build_record()

    mapping = build_mapping(
        graph,
        record,
    )

    known_ids = {
        concept.concept_id
        for concept
        in graph.all_concepts()
    }

    item = (
        NumbasContentConverter(
            source_registry=(
                DEFAULT_CONTENT_SOURCE_REGISTRY
            ),
            known_transition_concept_ids=(
                known_ids
            ),
        )
        .convert(
            record=record,
            mapping=mapping,
            metadata=build_metadata(),
        )
    )

    assert item.content_id == (
        "numbas:24060"
    )

    assert item.concept_id == (
        "fractions"
    )

    assert (
        item.license_decision
        == LicenseDecision.ALLOWED
    )

    assert item.can_be_delivered is True


def test_real_numbas_question_preserves_attribution() -> None:
    graph = build_graph()

    record = build_record()

    mapping = build_mapping(
        graph,
        record,
    )

    known_ids = {
        concept.concept_id
        for concept
        in graph.all_concepts()
    }

    item = (
        NumbasContentConverter(
            source_registry=(
                DEFAULT_CONTENT_SOURCE_REGISTRY
            ),
            known_transition_concept_ids=(
                known_ids
            ),
        )
        .convert(
            record=record,
            mapping=mapping,
            metadata=build_metadata(),
        )
    )

    assert (
        "Christian Lawson-Perfect"
        in item.attribution
    )

    assert (
        "Lauren Richards"
        in item.attribution
    )


def test_real_numbas_question_keeps_cc_by_license() -> None:
    graph = build_graph()

    record = build_record()

    mapping = build_mapping(
        graph,
        record,
    )

    known_ids = {
        concept.concept_id
        for concept
        in graph.all_concepts()
    }

    item = (
        NumbasContentConverter(
            source_registry=(
                DEFAULT_CONTENT_SOURCE_REGISTRY
            ),
            known_transition_concept_ids=(
                known_ids
            ),
        )
        .convert(
            record=record,
            mapping=mapping,
            metadata=build_metadata(),
        )
    )

    assert item.license_code == (
        "CC-BY-4.0"
    )
