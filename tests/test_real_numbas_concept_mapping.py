from pathlib import Path

from backend.app.content.ingestion.concept_mapper import (
    ContentConceptMapper,
)
from backend.app.content.ingestion.numbas.importer import (
    NumbasContentImporter,
)
from backend.app.content.ingestion.numbas.rules import (
    NUMBAS_TRANSITION_MAPPING_RULES,
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


def test_real_numbas_fraction_maps_to_fractions() -> None:
    record = (
        NumbasContentImporter()
        .import_file(
            SOURCE
        )
    )

    graph = KnowledgeGraphRepository(
        load_knowledge_graph(
            GRAPH
        )
    )

    mapper = ContentConceptMapper(
        knowledge_graph=graph,
        rules=(
            NUMBAS_TRANSITION_MAPPING_RULES
        ),
    )

    decision = mapper.map_record(
        record
    )

    assert decision.is_mapped

    assert decision.concept_id == (
        "fractions"
    )
