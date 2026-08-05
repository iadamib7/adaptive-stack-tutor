from backend.app.learning.concept_decision.engine import (
    ConceptDecisionEngine,
)
from backend.app.learning.concept_decision.models import (
    ConceptDecisionAction,
    ConceptLearningDecision,
)
from backend.app.learning.concept_evidence.models import (
    ConceptEvidenceEvent,
    ConceptEvidenceSummary,
    EvidenceType,
)
from backend.app.learning.concept_evidence.tracker import (
    ConceptEvidenceTracker,
)
from backend.app.learning.session.models import (
    LearningSessionState,
    ScoredStackOutcome,
    SessionProgress,
    SessionQuestion,
)
from backend.app.learning.session.repository import (
    LearningSessionRepository,
)


class AdaptiveLearningSessionEngine:
    """
    Orchestrate one curriculum-aware adaptive learning session.

    STACK remains responsible for evaluating mathematical responses.
    This engine receives the resulting answer note and score, converts
    them into concept evidence, and selects the next learning action.
    """

    def __init__(
        self,
        evidence_tracker: ConceptEvidenceTracker,
        decision_engine: ConceptDecisionEngine,
        session_repository: (
            LearningSessionRepository | None
        ) = None,
    ) -> None:
        self.evidence_tracker = evidence_tracker
        self.decision_engine = decision_engine

        self.session_repository = (
            session_repository
            if session_repository is not None
            else LearningSessionRepository()
        )

    def start_session(
        self,
        student_id: int,
        concept_id: str,
    ) -> LearningSessionState:
        decision = self.decision_engine.decide(
            student_id=student_id,
            concept_id=concept_id,
        )

        summary = self.evidence_tracker.summarize(
            student_id=student_id,
            concept_id=concept_id,
        )

        state = self._build_state(
            student_id=student_id,
            concept_id=concept_id,
            decision=decision,
            summary=summary,
            feedback=(
                f"Welcome. You are beginning "
                f"{summary.concept_name}. "
                f"{decision.reason}"
            ),
        )

        self.session_repository.save(state)

        return state

    def submit_outcome(
        self,
        outcome: ScoredStackOutcome,
    ) -> LearningSessionState:
        current_session = self.session_repository.get(
            outcome.student_id
        )

        if current_session is None:
            raise ValueError(
                f"No active learning session exists for "
                f"student {outcome.student_id}."
            )

        if (
            current_session.current_concept_id
            != outcome.concept_id
        ):
            raise ValueError(
                "The submitted concept does not match the "
                "student's active learning session."
            )

        if current_session.question is None:
            raise ValueError(
                "The current learning session is not waiting "
                "for a question response."
            )

        if (
            current_session.question.id
            != outcome.question_id
        ):
            raise ValueError(
                "The submitted question does not match the "
                "question currently assigned to the student."
            )

        evidence_event = (
            self.evidence_tracker.record_outcome(
                student_id=outcome.student_id,
                question_id=outcome.question_id,
                outcome_code=outcome.outcome_code,
                score=outcome.score,
            )
        )

        decision = self.decision_engine.decide(
            student_id=outcome.student_id,
            concept_id=outcome.concept_id,
        )

        summary = self.evidence_tracker.summarize(
            student_id=outcome.student_id,
            concept_id=outcome.concept_id,
        )

        feedback = self._build_feedback(
            evidence_event=evidence_event,
            stack_feedback=outcome.stack_feedback,
            decision=decision,
        )

        state = self._build_state(
            student_id=outcome.student_id,
            concept_id=outcome.concept_id,
            decision=decision,
            summary=summary,
            feedback=feedback,
        )

        self.session_repository.save(state)

        return state

    def get_session(
        self,
        student_id: int,
    ) -> LearningSessionState | None:
        return self.session_repository.get(student_id)

    @staticmethod
    def _build_feedback(
        evidence_event: ConceptEvidenceEvent,
        stack_feedback: str | None,
        decision: ConceptLearningDecision,
    ) -> str:
        feedback_parts: list[str] = []

        if stack_feedback:
            feedback_parts.append(
                stack_feedback.strip()
            )
        elif (
            evidence_event.evidence_type
            == EvidenceType.POSITIVE
        ):
            feedback_parts.append(
                "Correct. This response provides positive "
                "evidence of your understanding."
            )
        elif (
            evidence_event.evidence_type
            == EvidenceType.PARTIAL
        ):
            feedback_parts.append(
                "You demonstrated part of the required "
                "understanding, but some work remains."
            )
        else:
            feedback_parts.append(
                "This response shows that you need more "
                "practice with this part of the concept."
            )

        feedback_parts.append(
            evidence_event.explanation
        )

        feedback_parts.append(
            decision.reason
        )

        return " ".join(feedback_parts)

    @staticmethod
    def _build_state(
        student_id: int,
        concept_id: str,
        decision: ConceptLearningDecision,
        summary: ConceptEvidenceSummary,
        feedback: str,
    ) -> LearningSessionState:
        question = None

        if (
            decision.next_question_id is not None
            and decision.next_question_name is not None
        ):
            question = SessionQuestion(
                id=decision.next_question_id,
                name=decision.next_question_name,
            )

        session_complete = decision.action in {
            ConceptDecisionAction.COMPLETE_CONCEPT,
            ConceptDecisionAction.ADVANCE_CONCEPT,
        }

        progress = SessionProgress(
            concept_id=summary.concept_id,
            concept_name=summary.concept_name,
            attempts=summary.attempts,
            evidence_score=summary.evidence_score,
            positive_evidence_count=(
                summary.positive_evidence_count
            ),
            partial_evidence_count=(
                summary.partial_evidence_count
            ),
            negative_evidence_count=(
                summary.negative_evidence_count
            ),
            concept_mastered=summary.concept_mastered,
        )

        return LearningSessionState(
            student_id=student_id,
            current_concept_id=concept_id,
            question=question,
            action=decision.action,
            feedback=feedback,
            decision_reason=decision.reason,
            progress=progress,
            next_concept_id=decision.next_concept_id,
            session_complete=session_complete,
        )
