from __future__ import annotations

from dataclasses import dataclass

from backend.app.content.models import (
    ContentKind,
    LicenseDecision,
)
from backend.app.content.repository import (
    LearningContentRepository,
)
from backend.app.learning.knowledge_graph.repository import (
    KnowledgeGraphRepository,
)


@dataclass(frozen=True)
class ConceptContentCoverage:
    concept_id: str
    concept_name: str

    total_questions: int
    deliverable_questions: int
    review_questions: int
    blocked_questions: int

    mastery_questions: int

    recommended_question_count: int

    question_gap: int
    deliverable_gap: int

    @property
    def has_content(
        self,
    ) -> bool:
        return self.total_questions > 0

    @property
    def has_deliverable_content(
        self,
    ) -> bool:
        return self.deliverable_questions > 0

    @property
    def meets_recommended_count(
        self,
    ) -> bool:
        return self.question_gap == 0

    @property
    def meets_deliverable_target(
        self,
    ) -> bool:
        return self.deliverable_gap == 0


class ContentCoverageAuditor:
    """
    Compare available learning content with the
    requirements of the knowledge graph.
    """

    def audit(
        self,
        *,
        knowledge_graph: KnowledgeGraphRepository,
        content_repository: LearningContentRepository,
    ) -> list[ConceptContentCoverage]:
        rows: list[
            ConceptContentCoverage
        ] = []

        for concept in (
            knowledge_graph.all_concepts()
        ):
            items = (
                content_repository.for_concept(
                    concept.concept_id,
                    deliverable_only=False,
                )
            )

            questions = [
                item
                for item in items
                if item.kind
                == ContentKind.QUESTION
            ]

            deliverable = [
                item
                for item in questions
                if item.can_be_delivered
            ]

            review = [
                item
                for item in questions
                if item.license_decision
                == LicenseDecision.REVIEW
            ]

            blocked = [
                item
                for item in questions
                if item.license_decision
                == LicenseDecision.BLOCKED
            ]

            mastery = [
                item
                for item in questions
                if item.is_mastery_evidence
            ]

            question_gap = max(
                concept.recommended_question_count
                - len(questions),
                0,
            )

            deliverable_gap = max(
                concept.recommended_question_count
                - len(deliverable),
                0,
            )

            rows.append(
                ConceptContentCoverage(
                    concept_id=(
                        concept.concept_id
                    ),
                    concept_name=(
                        concept.name
                    ),
                    total_questions=len(
                        questions
                    ),
                    deliverable_questions=len(
                        deliverable
                    ),
                    review_questions=len(
                        review
                    ),
                    blocked_questions=len(
                        blocked
                    ),
                    mastery_questions=len(
                        mastery
                    ),
                    recommended_question_count=(
                        concept
                        .recommended_question_count
                    ),
                    question_gap=(
                        question_gap
                    ),
                    deliverable_gap=(
                        deliverable_gap
                    ),
                )
            )

        return rows

    def content_gaps(
        self,
        *,
        knowledge_graph: KnowledgeGraphRepository,
        content_repository: LearningContentRepository,
    ) -> list[ConceptContentCoverage]:
        rows = self.audit(
            knowledge_graph=(
                knowledge_graph
            ),
            content_repository=(
                content_repository
            ),
        )

        return sorted(
            [
                row
                for row in rows
                if row.deliverable_gap > 0
            ],
            key=lambda row: (
                -row.deliverable_gap,
                row.concept_name,
            ),
        )

    def concepts_without_questions(
        self,
        *,
        knowledge_graph: KnowledgeGraphRepository,
        content_repository: LearningContentRepository,
    ) -> list[ConceptContentCoverage]:
        return [
            row
            for row in self.audit(
                knowledge_graph=(
                    knowledge_graph
                ),
                content_repository=(
                    content_repository
                ),
            )
            if not row.has_content
        ]

    def concepts_without_deliverable_questions(
        self,
        *,
        knowledge_graph: KnowledgeGraphRepository,
        content_repository: LearningContentRepository,
    ) -> list[ConceptContentCoverage]:
        return [
            row
            for row in self.audit(
                knowledge_graph=(
                    knowledge_graph
                ),
                content_repository=(
                    content_repository
                ),
            )
            if not row.has_deliverable_content
        ]