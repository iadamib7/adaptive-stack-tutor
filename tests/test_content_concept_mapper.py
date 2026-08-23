from backend.app.content.ingestion.concept_mapper import (
    ContentConceptMapper,
)
from backend.app.content.ingestion.concept_mapping_models import (
    MappingStatus,
)
from backend.app.content.ingestion.concept_mapping_rules import (
    ConceptMappingRule,
)
from backend.app.content.ingestion.models import (
    ImportedContentRecord,
)
from backend.app.learning.knowledge_graph.models import (
    KnowledgeConcept,
)
from backend.app.learning.knowledge_graph.repository import (
    KnowledgeGraphRepository,
)


def concept(
    concept_id: str,
) -> KnowledgeConcept:
    return KnowledgeConcept(
        concept_id=concept_id,
        name=concept_id,
        domain="Mathematics",
        strand="Test",
        level_id="test",
    )


def record(
    *,
    category: str,
    title: str = "Question",
) -> ImportedContentRecord:
    return ImportedContentRecord(
        source_provider="stack",
        source_reference="test.xml",
        external_id="1",
        title=title,
        category_path=category,
    )


def test_matching_rule_maps_content() -> None:
    repository = (
        KnowledgeGraphRepository(
            [
                concept(
                    "integer-operations"
                )
            ]
        )
    )

    mapper = ContentConceptMapper(
        knowledge_graph=repository,
        rules=[
            ConceptMappingRule(
                rule_id="integers",
                concept_id=(
                    "integer-operations"
                ),
                category_contains=(
                    "integers",
                ),
            )
        ],
    )

    decision = mapper.map_record(
        record(
            category=(
                "Grade 9 / Integers"
            )
        )
    )

    assert decision.is_mapped

    assert decision.concept_id == (
        "integer-operations"
    )


def test_unmatched_content_is_not_guessed() -> None:
    repository = (
        KnowledgeGraphRepository(
            [
                concept(
                    "integer-operations"
                )
            ]
        )
    )

    mapper = ContentConceptMapper(
        knowledge_graph=repository,
        rules=[
            ConceptMappingRule(
                rule_id="integers",
                concept_id=(
                    "integer-operations"
                ),
                category_contains=(
                    "integers",
                ),
            )
        ],
    )

    decision = mapper.map_record(
        record(
            category="Unknown"
        )
    )

    assert decision.status == (
        MappingStatus.UNMAPPED
    )

    assert decision.concept_id is None


def test_conflicting_rules_require_review() -> None:
    repository = (
        KnowledgeGraphRepository(
            [
                concept("a"),
                concept("b"),
            ]
        )
    )

    mapper = ContentConceptMapper(
        knowledge_graph=repository,
        rules=[
            ConceptMappingRule(
                rule_id="rule-a",
                concept_id="a",
                category_contains=(
                    "algebra",
                ),
            ),
            ConceptMappingRule(
                rule_id="rule-b",
                concept_id="b",
                category_contains=(
                    "algebra",
                ),
            ),
        ],
    )

    decision = mapper.map_record(
        record(
            category="Algebra"
        )
    )

    assert decision.status == (
        MappingStatus.REVIEW_REQUIRED
    )

    assert decision.concept_id is None


def test_unknown_rule_concept_is_rejected() -> None:
    repository = (
        KnowledgeGraphRepository(
            [
                concept("known")
            ]
        )
    )

    try:
        ContentConceptMapper(
            knowledge_graph=repository,
            rules=[
                ConceptMappingRule(
                    rule_id="bad",
                    concept_id="missing",
                    category_contains=(
                        "anything",
                    ),
                )
            ],
        )
    except ValueError as error:
        assert "Unknown" in str(
            error
        )
    else:
        raise AssertionError(
            "Expected ValueError."
        )


def test_title_rule_can_map_content() -> None:
    repository = (
        KnowledgeGraphRepository(
            [
                concept("gradient")
            ]
        )
    )

    mapper = ContentConceptMapper(
        knowledge_graph=repository,
        rules=[
            ConceptMappingRule(
                rule_id="gradient-title",
                concept_id="gradient",
                title_contains=(
                    "gradient",
                ),
            )
        ],
    )

    decision = mapper.map_record(
        record(
            category="Geometry",
            title=(
                "Determining gradient "
                "of perpendicular lines"
            ),
        )
    )

    assert decision.concept_id == (
        "gradient"
    )


def test_more_specific_rule_wins_over_broad_rule() -> None:
    repository = (
        KnowledgeGraphRepository(
            [
                concept(
                    "coordinate-graphs"
                ),
                concept(
                    "gradient"
                ),
            ]
        )
    )

    mapper = ContentConceptMapper(
        knowledge_graph=repository,
        rules=[
            ConceptMappingRule(
                rule_id="broad",
                concept_id=(
                    "coordinate-graphs"
                ),
                category_contains=(
                    "coordinates and graphs",
                ),
            ),
            ConceptMappingRule(
                rule_id="specific",
                concept_id="gradient",
                category_contains=(
                    "coordinates and graphs",
                ),
                title_contains=(
                    "gradient",
                ),
            ),
        ],
    )

    decision = mapper.map_record(
        record(
            category=(
                "Grade 9 / "
                "Coordinates and Graphs"
            ),
            title=(
                "Determining gradient "
                "of perpendicular lines"
            ),
        )
    )

    assert decision.is_mapped

    assert decision.concept_id == (
        "gradient"
    )

    assert decision.matched_rule == (
        "specific"
    )
