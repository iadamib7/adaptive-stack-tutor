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
from backend.app.learning.adaptive_pathway.policy import (
    AdaptivePathwayPolicy,
    PathwayAction,
)
from backend.app.learning.adaptive_pathway.selector import (
    AdaptiveConceptSelector,
)
from backend.app.learning.adaptive_pathway.session_adapter import (
    AdaptiveLearnerPathwayState,
    AdaptivePathwaySessionAdapter,
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


def build_adapter() -> AdaptivePathwaySessionAdapter:
    graph = KnowledgeGraphRepository(
        [
            concept(
                "number-sense",
                extensions=(
                    "integer-operations",
                ),
            ),
            concept(
                "integer-operations",
                prerequisites=(
                    "number-sense",
                ),
            ),
            concept(
                "fractions",
            ),
            concept(
                "decimals",
            ),
            concept(
                "percentages",
                prerequisites=(
                    "fractions",
                    "decimals",
                ),
                remediation=(
                    "fractions",
                    "decimals",
                ),
            ),
        ]
    )

    content = LearningContentRepository(
        [
            question(
                "numbas:number",
                "number-sense",
            ),
            question(
                "numbas:integer",
                "integer-operations",
            ),
            question(
                "numbas:fraction",
                "fractions",
            ),
            question(
                "numbas:decimal",
                "decimals",
            ),
            question(
                "numbas:percent",
                "percentages",
            ),
        ]
    )

    policy = AdaptivePathwayPolicy(
        concept_selector=(
            AdaptiveConceptSelector(graph)
        ),
        content_selector=(
            AdaptiveContentSelector(content)
        ),
    )

    return AdaptivePathwaySessionAdapter(
        pathway_policy=policy
    )


def test_mastered_student_advances() -> None:
    adapter = build_adapter()

    state = AdaptiveLearnerPathwayState(
        student_id=1,
        current_concept_id="number-sense",
        seen_content_ids={
            "numbas:number",
        },
    )

    result = adapter.decide_next(
        state,
        concept_mastered=True,
    )

    assert (
        result.action
        == PathwayAction.ADVANCE
    )

    assert (
        result.concept_id
        == "integer-operations"
    )

    assert result.question is not None

    assert (
        result.question.content_id
        == "numbas:integer"
    )

    assert (
        "number-sense"
        in state.mastered_concept_ids
    )

    assert (
        state.current_concept_id
        == "integer-operations"
    )


def test_weak_student_remediates() -> None:
    adapter = build_adapter()

    state = AdaptiveLearnerPathwayState(
        student_id=2,
        current_concept_id="percentages",
        mastered_concept_ids={
            "fractions",
        },
        seen_content_ids={
            "numbas:percent",
        },
    )

    result = adapter.decide_next(
        state,
        concept_mastered=False,
    )

    assert (
        result.action
        == PathwayAction.REMEDIATE
    )

    assert (
        result.concept_id
        == "decimals"
    )

    assert result.question is not None

    assert (
        result.question.content_id
        == "numbas:decimal"
    )

    assert (
        state.current_concept_id
        == "decimals"
    )


def test_seen_question_is_recorded() -> None:
    adapter = build_adapter()

    state = AdaptiveLearnerPathwayState(
        student_id=3,
        current_concept_id="number-sense",
    )

    result = adapter.decide_next(
        state,
        concept_mastered=False,
    )

    assert result.question is not None

    assert (
        result.question.content_id
        in state.seen_content_ids
    )