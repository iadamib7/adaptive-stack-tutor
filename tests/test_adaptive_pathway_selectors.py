from backend.app.content.models import (
    ContentKind,
    ContentSource,
    LearningContentItem,
    LicenseDecision,
)
from backend.app.content.repository import (
    LearningContentRepository,
)
from backend.app.learning.adaptive_pathway.content_selector import (
    AdaptiveContentSelector,
)
from backend.app.learning.adaptive_pathway.selector import (
    AdaptiveConceptSelector,
)
from backend.app.learning.knowledge_graph.models import (
    ConceptDifficultyBand,
    KnowledgeConcept,
)
from backend.app.learning.knowledge_graph.repository import (
    KnowledgeGraphRepository,
)


def concept(
    concept_id: str,
    *,
    prerequisites: tuple[str, ...] = (),
    remediation: tuple[str, ...] = (),
    extensions: tuple[str, ...] = (),
) -> KnowledgeConcept:
    return KnowledgeConcept(
        concept_id=concept_id,
        name=concept_id,
        domain="Mathematics",
        strand="Test",
        level_id="G9-G10",
        difficulty_band=(
            ConceptDifficultyBand.FOUNDATION
        ),
        prerequisite_concept_ids=prerequisites,
        remediation_concept_ids=remediation,
        extension_concept_ids=extensions,
        mastery_threshold=0.8,
        recommended_question_count=1,
    )


def question(
    content_id: str,
    concept_id: str,
) -> LearningContentItem:
    return LearningContentItem(
        content_id=content_id,
        concept_id=concept_id,
        title=content_id,
        kind=ContentKind.QUESTION,
        source=ContentSource.OER,
        source_reference=content_id,
        license_code="CC-BY-4.0",
        license_decision=(
            LicenseDecision.ALLOWED
        ),
        active=True,
    )


def test_starting_concept_uses_eligible_foundation() -> None:
    graph = KnowledgeGraphRepository(
        [
            concept(
                "number-sense",
                extensions=("integers",),
            ),
            concept(
                "integers",
                prerequisites=(
                    "number-sense",
                ),
            ),
        ]
    )

    selector = AdaptiveConceptSelector(
        graph
    )

    selected = (
        selector.select_starting_concept(
            set()
        )
    )

    assert selected is not None

    assert (
        selected.concept_id
        == "number-sense"
    )


def test_next_concept_uses_eligible_extension() -> None:
    graph = KnowledgeGraphRepository(
        [
            concept(
                "number-sense",
                extensions=("integers",),
            ),
            concept(
                "integers",
                prerequisites=(
                    "number-sense",
                ),
            ),
        ]
    )

    selector = AdaptiveConceptSelector(
        graph
    )

    selected = (
        selector.select_next_concept(
            current_concept_id=(
                "number-sense"
            ),
            mastered_concept_ids={
                "number-sense",
            },
        )
    )

    assert selected is not None

    assert (
        selected.concept_id
        == "integers"
    )


def test_remediation_skips_mastered_concepts() -> None:
    graph = KnowledgeGraphRepository(
        [
            concept(
                "fractions"
            ),
            concept(
                "decimals"
            ),
            concept(
                "percentages",
                remediation=(
                    "fractions",
                    "decimals",
                ),
            ),
        ]
    )

    selector = AdaptiveConceptSelector(
        graph
    )

    selected = (
        selector.select_remediation_concept(
            current_concept_id=(
                "percentages"
            ),
            mastered_concept_ids={
                "fractions",
            },
        )
    )

    assert selected is not None

    assert (
        selected.concept_id
        == "decimals"
    )


def test_content_selector_prefers_unseen_question() -> None:
    repository = (
        LearningContentRepository(
            [
                question(
                    "numbas:1",
                    "decimals",
                ),
                question(
                    "numbas:2",
                    "decimals",
                ),
            ]
        )
    )

    selector = AdaptiveContentSelector(
        repository
    )

    selected = (
        selector.select_question(
            concept_id="decimals",
            seen_content_ids={
                "numbas:1",
            },
        )
    )

    assert selected is not None

    assert (
        selected.content_id
        == "numbas:2"
    )


def test_content_selector_returns_none_when_exhausted() -> None:
    repository = (
        LearningContentRepository(
            [
                question(
                    "numbas:1",
                    "decimals",
                ),
            ]
        )
    )

    selector = AdaptiveContentSelector(
        repository
    )

    selected = (
        selector.select_question(
            concept_id="decimals",
            seen_content_ids={
                "numbas:1",
            },
        )
    )

    assert selected is None


def test_content_selector_can_repeat_when_allowed() -> None:
    repository = (
        LearningContentRepository(
            [
                question(
                    "numbas:1",
                    "decimals",
                ),
            ]
        )
    )

    selector = AdaptiveContentSelector(
        repository
    )

    selected = (
        selector.select_question(
            concept_id="decimals",
            seen_content_ids={
                "numbas:1",
            },
            allow_repeat=True,
        )
    )

    assert selected is not None

    assert (
        selected.content_id
        == "numbas:1"
    )