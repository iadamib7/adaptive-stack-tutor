from backend.app.content.models import (
    ContentKind,
    ContentSource,
    LearningContentItem,
    LicenseDecision,
)
from backend.app.learning.adaptive_pathway.adapter import (
    AdaptivePathwayDecisionAdapter,
)
from backend.app.learning.adaptive_pathway.policy import (
    PathwayAction,
    PathwayDecision,
)
from backend.app.learning.concept_decision.models import (
    ConceptDecisionAction,
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
    )


def test_practice_adapts_to_target_practice() -> None:
    graph = KnowledgeGraphRepository(
        [
            concept("decimals"),
        ]
    )

    adapter = AdaptivePathwayDecisionAdapter(
        graph
    )

    pathway = PathwayDecision(
        action=PathwayAction.PRACTICE,
        concept_id="decimals",
        question=question(
            "numbas:1",
            "decimals",
        ),
        reason="Practice.",
    )

    decision = adapter.adapt(
        student_id=1,
        current_concept_id="decimals",
        pathway_decision=pathway,
        evidence_score=0.5,
        concept_mastered=False,
    )

    assert (
        decision.action
        == ConceptDecisionAction.TARGET_PRACTICE
    )

    assert (
        decision.next_question_id
        == "numbas:1"
    )


def test_advance_sets_next_concept() -> None:
    graph = KnowledgeGraphRepository(
        [
            concept("number-sense"),
            concept("integer-operations"),
        ]
    )

    adapter = AdaptivePathwayDecisionAdapter(
        graph
    )

    pathway = PathwayDecision(
        action=PathwayAction.ADVANCE,
        concept_id="integer-operations",
        question=question(
            "numbas:2",
            "integer-operations",
        ),
        reason="Advance.",
    )

    decision = adapter.adapt(
        student_id=1,
        current_concept_id="number-sense",
        pathway_decision=pathway,
        evidence_score=1.0,
        concept_mastered=True,
    )

    assert (
        decision.action
        == ConceptDecisionAction.ADVANCE_CONCEPT
    )

    assert (
        decision.next_concept_id
        == "integer-operations"
    )

    assert (
        decision.next_question_id
        is None
    )
def test_remediation_moves_to_support_concept() -> None:
    graph = KnowledgeGraphRepository(
        [
            concept("percentages"),
            concept("decimals"),
        ]
    )

    adapter = AdaptivePathwayDecisionAdapter(
        graph
    )

    pathway = PathwayDecision(
        action=PathwayAction.REMEDIATE,
        concept_id="decimals",
        question=question(
            "numbas:decimal",
            "decimals",
        ),
        reason="Remediate with decimals.",
    )

    decision = adapter.adapt(
        student_id=1,
        current_concept_id="percentages",
        pathway_decision=pathway,
        evidence_score=0.4,
        concept_mastered=False,
    )

    assert (
        decision.action
        == ConceptDecisionAction.REMEDIATE_CONCEPT
    )

    assert (
        decision.next_concept_id
        == "decimals"
    )

    assert (
        decision.next_question_id
        is None
    )

    assert decision.concept_mastered is False


def test_cross_concept_transition_never_carries_question() -> None:
    graph = KnowledgeGraphRepository(
        [
            concept("similarity"),
            concept("trigonometry"),
        ]
    )

    adapter = AdaptivePathwayDecisionAdapter(
        graph
    )

    pathway = PathwayDecision(
        action=PathwayAction.ADVANCE,
        concept_id="trigonometry",
        question=question(
            "221194",
            "trigonometry",
        ),
        reason="Advance to trigonometry.",
    )

    decision = adapter.adapt(
        student_id=1,
        current_concept_id="similarity",
        pathway_decision=pathway,
        evidence_score=1.0,
        concept_mastered=True,
    )

    assert (
        decision.action
        == ConceptDecisionAction.ADVANCE_CONCEPT
    )

    assert (
        decision.next_concept_id
        == "trigonometry"
    )

    assert decision.next_question_id is None
    assert decision.next_question_name is None
