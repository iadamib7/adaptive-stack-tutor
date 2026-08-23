from pathlib import Path

from backend.app.content.coverage import (
    ContentCoverageAuditor,
)
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
from backend.app.content.repository import (
    LearningContentRepository,
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


def test_numbas_fraction_reduces_fraction_gap() -> None:
    graph = KnowledgeGraphRepository(
        load_knowledge_graph(
            GRAPH
        )
    )

    record = (
        NumbasContentImporter()
        .import_file(
            SOURCE
        )
    )

    mapper = ContentConceptMapper(
        knowledge_graph=graph,
        rules=(
            NUMBAS_TRANSITION_MAPPING_RULES
        ),
    )

    mapping = mapper.map_record(
        record
    )

    known_ids = {
        concept.concept_id
        for concept
        in graph.all_concepts()
    }

    metadata = NumbasQuestionMetadata(
        question_id="24060",
        title=record.title,
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
        author_names=(
            "Christian Lawson-Perfect",
            "Lauren Richards",
        ),
    )

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
            metadata=metadata,
        )
    )

    repository = (
        LearningContentRepository(
            [
                item
            ]
        )
    )

    rows = (
        ContentCoverageAuditor()
        .audit(
            knowledge_graph=graph,
            content_repository=repository,
        )
    )

    fractions = next(
        row
        for row in rows
        if row.concept_id
        == "fractions"
    )

    assert fractions.total_questions == 1

    assert (
        fractions.deliverable_questions
        == 1
    )

    assert fractions.question_gap == 11
