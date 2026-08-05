from backend.app.learning.concept_decision.models import (
    ConceptDecisionAction,
    ConceptLearningDecision,
)
from backend.app.learning.concept_evidence.models import (
    ConceptEvidenceEvent,
    EvidenceType,
)
from backend.app.learning.concept_evidence.tracker import (
    ConceptEvidenceTracker,
)
from backend.app.learning.curriculum_mapping.models import (
    QuestionEvidence,
)
from backend.app.learning.curriculum_mapping.repository import (
    CurriculumMappingRepository,
)


class ConceptDecisionEngine:
    """
    Select the learner's next concept-level action.

    This is a deterministic development policy. It is intentionally
    explainable and can later be replaced or extended with educator-
    validated rules, learner modelling, statistical difficulty, and
    IRT without changing the surrounding curriculum architecture.
    """

    def __init__(
        self,
        mapping_repository: CurriculumMappingRepository,
        evidence_tracker: ConceptEvidenceTracker,
    ) -> None:
        self.mapping_repository = mapping_repository
        self.evidence_tracker = evidence_tracker

    def decide(
        self,
        student_id: int,
        concept_id: str,
    ) -> ConceptLearningDecision:
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

        ordered_questions = (
            self.mapping_repository
            .get_questions_for_concept(concept_id)
        )

        if not ordered_questions:
            raise ValueError(
                f"Curriculum concept {concept_id} "
                "has no mapped evidence questions."
            )

        if not events:
            question = self._select_first_foundation(
                ordered_questions
            )

            return self._question_decision(
                student_id=student_id,
                concept_id=concept_id,
                concept_name=mapping.concept_name,
                action=(
                    ConceptDecisionAction.START_FOUNDATION
                ),
                question=question,
                evidence_score=summary.evidence_score,
                concept_mastered=False,
                reason=(
                    f"No evidence has yet been collected for "
                    f"{mapping.concept_name}. Begin with "
                    f"{question.question_name}, which is an "
                    "entry-level evidence question for this "
                    "concept."
                ),
            )

        if summary.concept_mastered:
            if mapping.next_concept_ids:
                next_concept_id = (
                    mapping.next_concept_ids[0]
                )

                return ConceptLearningDecision(
                    student_id=student_id,
                    current_concept_id=concept_id,
                    current_concept_name=(
                        mapping.concept_name
                    ),
                    action=(
                        ConceptDecisionAction
                        .ADVANCE_CONCEPT
                    ),
                    next_concept_id=next_concept_id,
                    evidence_score=(
                        summary.evidence_score
                    ),
                    concept_mastered=True,
                    reason=(
                        f"The learner has met the "
                        f"provisional mastery requirements "
                        f"for {mapping.concept_name}. "
                        f"Advance to curriculum concept "
                        f"{next_concept_id}."
                    ),
                )

            return ConceptLearningDecision(
                student_id=student_id,
                current_concept_id=concept_id,
                current_concept_name=mapping.concept_name,
                action=(
                    ConceptDecisionAction.COMPLETE_CONCEPT
                ),
                evidence_score=summary.evidence_score,
                concept_mastered=True,
                reason=(
                    f"The learner has met the provisional "
                    f"mastery requirements for "
                    f"{mapping.concept_name}. No next "
                    "curriculum concept has yet been linked "
                    "in the development mapping."
                ),
            )

        best_scores = self._get_best_question_scores(
            events
        )

        unresolved_regular_questions = [
            question
            for question in ordered_questions
            if (
                not question.required_for_mastery
                and best_scores.get(
                    question.question_id,
                    0.0,
                )
                < 1.0
            )
        ]

        if unresolved_regular_questions:
            question = unresolved_regular_questions[0]
            previous_score = best_scores.get(
                question.question_id
            )

            if previous_score is None:
                reason = (
                    f"Continue collecting evidence for "
                    f"{mapping.concept_name}. "
                    f"{question.question_name} has not yet "
                    "been attempted."
                )
            elif previous_score > 0.0:
                reason = (
                    f"The learner has only partial evidence "
                    f"from {question.question_name}. "
                    "Present another opportunity to "
                    "demonstrate this skill."
                )
            else:
                reason = (
                    f"The learner has not yet demonstrated "
                    f"the skill assessed by "
                    f"{question.question_name}. Continue "
                    "with targeted practice within "
                    f"{mapping.concept_name}."
                )

            return self._question_decision(
                student_id=student_id,
                concept_id=concept_id,
                concept_name=mapping.concept_name,
                action=(
                    ConceptDecisionAction.TARGET_PRACTICE
                ),
                question=question,
                evidence_score=summary.evidence_score,
                concept_mastered=False,
                reason=reason,
            )

        mastery_questions = [
            question
            for question in ordered_questions
            if question.required_for_mastery
        ]

        unresolved_mastery_questions = [
            question
            for question in mastery_questions
            if best_scores.get(
                question.question_id,
                0.0,
            )
            < 1.0
        ]

        if unresolved_mastery_questions:
            question = unresolved_mastery_questions[0]

            return self._question_decision(
                student_id=student_id,
                concept_id=concept_id,
                concept_name=mapping.concept_name,
                action=(
                    ConceptDecisionAction.VERIFY_MASTERY
                ),
                question=question,
                evidence_score=summary.evidence_score,
                concept_mastered=False,
                reason=(
                    f"The learner has demonstrated the "
                    f"component skills for "
                    f"{mapping.concept_name}, but has not "
                    "yet passed the required integrated "
                    f"mastery check: "
                    f"{question.question_name}."
                ),
            )

        # This case can occur when the mastery check has been passed
        # but the overall weighted evidence score is still below the
        # provisional mastery threshold.
        question = self._select_lowest_scoring_question(
            ordered_questions=ordered_questions,
            best_scores=best_scores,
        )

        return self._question_decision(
            student_id=student_id,
            concept_id=concept_id,
            concept_name=mapping.concept_name,
            action=ConceptDecisionAction.TARGET_PRACTICE,
            question=question,
            evidence_score=summary.evidence_score,
            concept_mastered=False,
            reason=(
                f"The required mastery check has been "
                f"passed, but the overall evidence score "
                f"for {mapping.concept_name} remains below "
                "the provisional threshold. Revisit the "
                f"weakest available evidence question: "
                f"{question.question_name}."
            ),
        )

    @staticmethod
    def _get_best_question_scores(
        events: list[ConceptEvidenceEvent],
    ) -> dict[str, float]:
        best_scores: dict[str, float] = {}

        for event in events:
            current_best = best_scores.get(
                event.question_id,
                0.0,
            )

            best_scores[event.question_id] = max(
                current_best,
                event.score,
            )

        return best_scores

    @staticmethod
    def _select_first_foundation(
        questions: list[QuestionEvidence],
    ) -> QuestionEvidence:
        foundation_questions = [
            question
            for question in questions
            if question.role.value == "foundation"
        ]

        if foundation_questions:
            return foundation_questions[0]

        return questions[0]

    @staticmethod
    def _select_lowest_scoring_question(
        ordered_questions: list[QuestionEvidence],
        best_scores: dict[str, float],
    ) -> QuestionEvidence:
        return min(
            ordered_questions,
            key=lambda question: (
                best_scores.get(
                    question.question_id,
                    0.0,
                ),
                question.sequence_order,
            ),
        )

    @staticmethod
    def _question_decision(
        student_id: int,
        concept_id: str,
        concept_name: str,
        action: ConceptDecisionAction,
        question: QuestionEvidence,
        evidence_score: float,
        concept_mastered: bool,
        reason: str,
    ) -> ConceptLearningDecision:
        return ConceptLearningDecision(
            student_id=student_id,
            current_concept_id=concept_id,
            current_concept_name=concept_name,
            action=action,
            next_question_id=question.question_id,
            next_question_name=question.question_name,
            evidence_score=evidence_score,
            concept_mastered=concept_mastered,
            reason=reason,
        )
