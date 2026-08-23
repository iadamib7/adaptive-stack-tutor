from backend.app.content.coverage import (
    ContentCoverageAuditor,
)
from backend.app.content.models import (
    ContentKind,
    ContentSource,
    LearningContentItem,
    LicenseDecision,
)
from backend.app.content.repository import (
    LearningContentRepository,
)
from backend.app.learning.knowledge_graph.models import (
    KnowledgeConcept,
)
from backend.app.learning.knowledge_graph.repository import (
    KnowledgeGraphRepository,
)


def concept(
    concept_id: str,
    *,
    target: int,
) -> KnowledgeConcept:
    return KnowledgeConcept(
        concept_id=concept_id,
        name=concept_id.title(),
        domain="Mathematics",
        strand="Test",
        level_id="test",
        recommended_question_count=target,
    )


def question(
    content_id: str,
    concept_id: str,
    *,
    decision: LicenseDecision,
    mastery: bool = False,
) -> LearningContentItem:
    return LearningContentItem(
        content_id=content_id,
        concept_id=concept_id,
        title=content_id,
        kind=ContentKind.QUESTION,
        source=ContentSource.INTERNAL,
        license_code="TEST",
        license_decision=decision,
        is_mastery_evidence=mastery,
    )


def graph(
) -> KnowledgeGraphRepository:
    return KnowledgeGraphRepository(
        [
            concept(
                "fractions",
                target=4,
            ),
            concept(
                "integers",
                target=2,
            ),
            concept(
                "algebra",
                target=3,
            ),
        ]
    )


def repository(
) -> LearningContentRepository:
    return LearningContentRepository(
        [
            question(
                "f1",
                "fractions",
                decision=(
                    LicenseDecision.ALLOWED
                ),
            ),
            question(
                "f2",
                "fractions",
                decision=(
                    LicenseDecision.REVIEW
                ),
            ),
            question(
                "i1",
                "integers",
                decision=(
                    LicenseDecision.ALLOWED
                ),
                mastery=True,
            ),
            question(
                "i2",
                "integers",
                decision=(
                    LicenseDecision.ALLOWED
                ),
            ),
        ]
    )


def rows_by_id():
    rows = ContentCoverageAuditor().audit(
        knowledge_graph=graph(),
        content_repository=repository(),
    )

    return {
        row.concept_id: row
        for row in rows
    }


def test_counts_all_questions() -> None:
    rows = rows_by_id()

    assert (
        rows["fractions"]
        .total_questions
        == 2
    )


def test_counts_deliverable_questions() -> None:
    rows = rows_by_id()

    assert (
        rows["fractions"]
        .deliverable_questions
        == 1
    )


def test_counts_review_questions() -> None:
    rows = rows_by_id()

    assert (
        rows["fractions"]
        .review_questions
        == 1
    )


def test_calculates_question_gap() -> None:
    rows = rows_by_id()

    assert (
        rows["fractions"]
        .question_gap
        == 2
    )


def test_concept_can_meet_target() -> None:
    rows = rows_by_id()

    assert (
        rows["integers"]
        .meets_recommended_count
        is True
    )


def test_detects_concept_without_questions() -> None:
    missing = (
        ContentCoverageAuditor()
        .concepts_without_questions(
            knowledge_graph=graph(),
            content_repository=repository(),
        )
    )

    assert {
        row.concept_id
        for row in missing
    } == {
        "algebra"
    }


def test_content_gaps_are_largest_first() -> None:
    gaps = (
        ContentCoverageAuditor()
        .content_gaps(
            knowledge_graph=graph(),
            content_repository=repository(),
        )
    )

    assert gaps[0].concept_id == (
        "algebra"
    )
