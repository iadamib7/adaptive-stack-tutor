from datetime import datetime, timezone

from backend.app.learning.concept_evidence.models import (
    ConceptEvidenceEvent,
    EvidenceType,
)
from backend.app.learning.concept_evidence.tracker import (
    ConceptEvidenceTracker,
)
from backend.app.learning.concept_mastery.models import (
    ConceptMasteryState,
    MasteryStatus,
)
from backend.app.learning.concept_mastery.policy import (
    ConceptMasteryPolicy,
)
from backend.app.learning.concept_mastery.repository import (
    ConceptMasteryRepository,
)
from backend.app.learning.curriculum_mapping.repository import (
    CurriculumMappingRepository,
)


class ConceptMasteryEngine:
    def __init__(
        self,
        mapping_repository: CurriculumMappingRepository,
        evidence_tracker: ConceptEvidenceTracker,
        mastery_repository: (
            ConceptMasteryRepository | None
        ) = None,
        policy: ConceptMasteryPolicy | None = None,
    ) -> None:
        self.mapping_repository = mapping_repository
        self.evidence_tracker = evidence_tracker

        self.mastery_repository = (
            mastery_repository
            if mastery_repository is not None
            else ConceptMasteryRepository()
        )

        self.policy = (
            policy
            if policy is not None
            else ConceptMasteryPolicy()
        )

    def evaluate(
        self,
        student_id: int,
        concept_id: str,
    ) -> ConceptMasteryState:
        mapping = self.mapping_repository.get_mapping(
            concept_id
        )

        if mapping is None:
            raise ValueError(
                f"Curriculum concept {concept_id} "
                "does not exist."
            )

        summary = self.evidence_tracker.summarize(
            student_id=student_id,
            concept_id=concept_id,
        )

        events = (
            self.evidence_tracker
            .evidence_repository
            .get_events(
                student_id=student_id,
                concept_id=concept_id,
            )
        )

        mastery_events = [
            event
            for event in events
            if event.required_for_mastery
        ]

        review_required = (
            self._requires_review(mastery_events)
        )

        status = self.policy.determine_status(
            attempts=summary.attempts,
            concept_mastered=summary.concept_mastered,
            review_required=review_required,
            mastery_check_attempted=bool(
                mastery_events
            ),
        )

        confidence = self.policy.calculate_confidence(
            attempts=summary.attempts,
            mastered=(
                status == MasteryStatus.MASTERED
            ),
        )

        explanation = self._build_explanation(
            concept_name=summary.concept_name,
            status=status,
            mastery_score=summary.evidence_score,
            attempts=summary.attempts,
        )

        state = ConceptMasteryState(
            student_id=student_id,
            concept_id=summary.concept_id,
            concept_name=summary.concept_name,
            mastery_score=summary.evidence_score,
            confidence=confidence,
            attempts=summary.attempts,
            positive_evidence_count=(
                summary.positive_evidence_count
            ),
            partial_evidence_count=(
                summary.partial_evidence_count
            ),
            negative_evidence_count=(
                summary.negative_evidence_count
            ),
            required_mastery_checks=len(
                summary.required_mastery_question_ids
            ),
            passed_mastery_checks=len(
                summary.passed_mastery_question_ids
            ),
            status=status,
            explanation=explanation,
            last_updated=datetime.now(timezone.utc),
        )

        self.mastery_repository.save(state)

        return state

    def get_state(
        self,
        student_id: int,
        concept_id: str,
    ) -> ConceptMasteryState | None:
        return self.mastery_repository.get(
            student_id=student_id,
            concept_id=concept_id,
        )

    @staticmethod
    def _requires_review(
        mastery_events: list[ConceptEvidenceEvent],
    ) -> bool:
        events_by_question: dict[
            str,
            list[ConceptEvidenceEvent],
        ] = {}

        for event in mastery_events:
            events_by_question.setdefault(
                event.question_id,
                [],
            ).append(event)

        for question_events in events_by_question.values():
            previously_passed = False

            for event in question_events:
                if (
                    event.evidence_type
                    == EvidenceType.POSITIVE
                ):
                    previously_passed = True
                    continue

                if (
                    previously_passed
                    and event.evidence_type
                    == EvidenceType.NEGATIVE
                ):
                    return True

        return False

    @staticmethod
    def _build_explanation(
        concept_name: str,
        status: MasteryStatus,
        mastery_score: float,
        attempts: int,
    ) -> str:
        if status == MasteryStatus.NOT_STARTED:
            return (
                f"No learner evidence has been collected "
                f"for {concept_name}."
            )

        if status == MasteryStatus.INTRODUCED:
            return (
                f"The learner has started working on "
                f"{concept_name}. More evidence is needed."
            )

        if status == MasteryStatus.LEARNING:
            return (
                f"The learner is developing understanding "
                f"of {concept_name} across multiple "
                "evidence questions."
            )

        if status == MasteryStatus.PRACTICING:
            return (
                f"The learner is actively practising "
                f"{concept_name}. The current mastery score "
                f"is {mastery_score:.2f}."
            )

        if status == MasteryStatus.MASTERED:
            return (
                f"The learner has met the provisional "
                f"mastery requirements for {concept_name}."
            )

        return (
            f"Previously demonstrated understanding of "
            f"{concept_name} may no longer be secure. "
            "Additional review is recommended."
        )
