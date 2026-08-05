from backend.app.learning.concept_evidence.models import (
    ConceptEvidenceEvent,
    ConceptEvidenceSummary,
    EvidenceType,
)
from backend.app.learning.concept_evidence.policy import (
    ConceptEvidencePolicy,
)
from backend.app.learning.concept_evidence.repository import (
    ConceptEvidenceRepository,
)
from backend.app.learning.curriculum_mapping.repository import (
    CurriculumMappingRepository,
)


class ConceptEvidenceTracker:
    def __init__(
        self,
        mapping_repository: CurriculumMappingRepository,
        evidence_repository: (
            ConceptEvidenceRepository | None
        ) = None,
        policy: ConceptEvidencePolicy | None = None,
    ) -> None:
        self.mapping_repository = mapping_repository

        self.evidence_repository = (
            evidence_repository
            if evidence_repository is not None
            else ConceptEvidenceRepository()
        )

        self.policy = (
            policy
            if policy is not None
            else ConceptEvidencePolicy()
        )

    def record_outcome(
        self,
        student_id: int,
        question_id: str,
        outcome_code: str,
        score: float,
    ) -> ConceptEvidenceEvent:
        mapping = (
            self.mapping_repository
            .get_concept_for_question(question_id)
        )

        if mapping is None:
            raise ValueError(
                f"Question {question_id} is not mapped "
                "to a curriculum concept."
            )

        question = next(
            (
                item
                for item in mapping.questions
                if item.question_id == question_id
            ),
            None,
        )

        if question is None:
            raise ValueError(
                f"Question metadata was not found for "
                f"{question_id}."
            )

        evidence_type = self.policy.classify_score(
            score
        )

        evidence_weight = self.policy.get_weight(
            question.required_for_mastery
        )

        explanation = self._build_explanation(
            concept_name=mapping.concept_name,
            question_name=question.question_name,
            evidence_type=evidence_type,
            required_for_mastery=(
                question.required_for_mastery
            ),
        )

        event = ConceptEvidenceEvent(
            student_id=student_id,
            concept_id=mapping.concept_id,
            question_id=question.question_id,
            question_name=question.question_name,
            outcome_code=outcome_code,
            score=score,
            evidence_type=evidence_type,
            evidence_weight=evidence_weight,
            required_for_mastery=(
                question.required_for_mastery
            ),
            explanation=explanation,
        )

        self.evidence_repository.save(event)

        return event

    def summarize(
        self,
        student_id: int,
        concept_id: str,
    ) -> ConceptEvidenceSummary:
        mapping = self.mapping_repository.get_mapping(
            concept_id
        )

        if mapping is None:
            raise ValueError(
                f"Curriculum concept {concept_id} "
                "does not exist."
            )

        events = self.evidence_repository.get_events(
            student_id=student_id,
            concept_id=concept_id,
        )

        positive_count = sum(
            event.evidence_type
            == EvidenceType.POSITIVE
            for event in events
        )

        partial_count = sum(
            event.evidence_type
            == EvidenceType.PARTIAL
            for event in events
        )

        negative_count = sum(
            event.evidence_type
            == EvidenceType.NEGATIVE
            for event in events
        )

        possible_weight = sum(
            event.evidence_weight
            for event in events
        )

        earned_weight = sum(
            event.score * event.evidence_weight
            for event in events
        )

        evidence_score = (
            earned_weight / possible_weight
            if possible_weight > 0.0
            else 0.0
        )

        required_mastery_question_ids = [
            question.question_id
            for question in mapping.questions
            if question.required_for_mastery
        ]

        passed_mastery_question_ids = sorted(
            {
                event.question_id
                for event in events
                if (
                    event.required_for_mastery
                    and event.evidence_type
                    == EvidenceType.POSITIVE
                )
            }
        )

        mastery_requirements_met = (
            set(required_mastery_question_ids)
            <= set(passed_mastery_question_ids)
        )

        concept_mastered = (
            bool(events)
            and evidence_score
            >= self.policy.mastery_threshold
            and mastery_requirements_met
        )

        recommendation = (
            self._build_recommendation(
                concept_name=mapping.concept_name,
                events=events,
                evidence_score=evidence_score,
                required_mastery_question_ids=(
                    required_mastery_question_ids
                ),
                passed_mastery_question_ids=(
                    passed_mastery_question_ids
                ),
                concept_mastered=concept_mastered,
            )
        )

        return ConceptEvidenceSummary(
            student_id=student_id,
            concept_id=mapping.concept_id,
            concept_name=mapping.concept_name,
            attempts=len(events),
            positive_evidence_count=positive_count,
            partial_evidence_count=partial_count,
            negative_evidence_count=negative_count,
            earned_weight=earned_weight,
            possible_weight=possible_weight,
            evidence_score=evidence_score,
            required_mastery_question_ids=(
                required_mastery_question_ids
            ),
            passed_mastery_question_ids=(
                passed_mastery_question_ids
            ),
            concept_mastered=concept_mastered,
            recommendation=recommendation,
        )

    @staticmethod
    def _build_explanation(
        concept_name: str,
        question_name: str,
        evidence_type: EvidenceType,
        required_for_mastery: bool,
    ) -> str:
        if evidence_type == EvidenceType.POSITIVE:
            message = (
                f"The response provides positive evidence "
                f"for {concept_name} through "
                f"{question_name}."
            )
        elif evidence_type == EvidenceType.PARTIAL:
            message = (
                f"The response provides partial evidence "
                f"for {concept_name} through "
                f"{question_name}."
            )
        else:
            message = (
                f"The response indicates that the learner "
                f"still needs support with {concept_name}, "
                f"based on {question_name}."
            )

        if required_for_mastery:
            message += (
                " This question is designated as a "
                "concept-level mastery check."
            )

        return message

    def _build_recommendation(
        self,
        concept_name: str,
        events: list[ConceptEvidenceEvent],
        evidence_score: float,
        required_mastery_question_ids: list[str],
        passed_mastery_question_ids: list[str],
        concept_mastered: bool,
    ) -> str:
        if not events:
            return (
                f"No evidence has yet been collected for "
                f"{concept_name}. Begin with a foundation "
                "question."
            )

        if concept_mastered:
            return (
                f"The learner has met the provisional "
                f"evidence requirements for {concept_name}. "
                "The sequencing engine may consider the "
                "next curriculum concept."
            )

        missing_mastery_questions = sorted(
            set(required_mastery_question_ids)
            - set(passed_mastery_question_ids)
        )

        if missing_mastery_questions:
            return (
                f"Continue working on {concept_name}. "
                "The required mastery-check question has "
                "not yet been passed."
            )

        return (
            f"Continue collecting evidence for "
            f"{concept_name}. The current evidence score "
            f"is {evidence_score:.2f}, below the provisional "
            f"threshold of "
            f"{self.policy.mastery_threshold:.2f}."
        )
