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


def build_policy(
    concepts: list[KnowledgeConcept],
    questions: list[LearningContentItem],
) -> AdaptivePathwayPolicy:
    graph = KnowledgeGraphRepository(
        concepts
    )

    content = LearningContentRepository(
        questions
    )

    return AdaptivePathwayPolicy(
        concept_selector=(
            AdaptiveConceptSelector(graph)
        ),
        content_selector=(
            AdaptiveContentSelector(content)
        ),
    )


def test_uses_unseen_current_content_first() -> None:
    policy = build_policy(
        concepts=[
            concept("decimals"),
        ],
        questions=[
            question(
                "numbas:1",
                "decimals",
            ),
            question(
                "numbas:2",
                "decimals",
            ),
        ],
    )

    decision = policy.decide(
        current_concept_id="decimals",
        mastered_concept_ids=set(),
        seen_content_ids={
            "numbas:1",
        },
        concept_mastered=False,
    )

    assert (
        decision.action
        == PathwayAction.PRACTICE
    )

    assert decision.question is not None

    assert (
        decision.question.content_id
        == "numbas:2"
    )


def test_mastered_student_advances() -> None:
    policy = build_policy(
        concepts=[
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
        ],
        questions=[
            question(
                "numbas:1",
                "number-sense",
            ),
            question(
                "numbas:2",
                "integer-operations",
            ),
        ],
    )

    decision = policy.decide(
        current_concept_id="number-sense",
        mastered_concept_ids=set(),
        seen_content_ids={
            "numbas:1",
        },
        concept_mastered=True,
    )

    assert (
        decision.action
        == PathwayAction.ADVANCE
    )

    assert (
        decision.concept_id
        == "integer-operations"
    )

    assert decision.question is not None

    assert (
        decision.question.content_id
        == "numbas:2"
    )


def test_weak_student_is_remediated() -> None:
    policy = build_policy(
        concepts=[
            concept("fractions"),
            concept(
                "percentages",
                remediation=(
                    "fractions",
                ),
            ),
        ],
        questions=[
            question(
                "numbas:1",
                "percentages",
            ),
            question(
                "numbas:2",
                "fractions",
            ),
        ],
    )

    decision = policy.decide(
        current_concept_id="percentages",
        mastered_concept_ids=set(),
        seen_content_ids={
            "numbas:1",
        },
        concept_mastered=False,
    )

    assert (
        decision.action
        == PathwayAction.REMEDIATE
    )

    assert (
        decision.concept_id
        == "fractions"
    )

    assert decision.question is not None

    assert (
        decision.question.content_id
        == "numbas:2"
    )


def test_repeat_when_no_other_option() -> None:
    policy = build_policy(
        concepts=[
            concept("decimals"),
        ],
        questions=[
            question(
                "numbas:1",
                "decimals",
            ),
        ],
    )

    decision = policy.decide(
        current_concept_id="decimals",
        mastered_concept_ids=set(),
        seen_content_ids={
            "numbas:1",
        },
        concept_mastered=False,
    )

    assert (
        decision.action
        == PathwayAction.REPEAT
    )

    assert decision.question is not None

    assert (
        decision.question.content_id
        == "numbas:1"
    )