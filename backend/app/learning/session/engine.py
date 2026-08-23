from backend.app.learning.adaptive_pathway.adapter import (
    AdaptivePathwayDecisionAdapter,
)
from backend.app.learning.adaptive_pathway.policy import (
    AdaptivePathwayPolicy,
)
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
    Orchestrate one curriculum-aware adaptive learning
    session.

    STACK evaluates mathematics. This engine records the
    resulting evidence and deterministically selects what
    the learner should receive next.
    """

    def __init__(
        self,
        evidence_tracker: ConceptEvidenceTracker,
        decision_engine: ConceptDecisionEngine,
        session_repository: (
            LearningSessionRepository | None
        ) = None,
        pathway_policy: (
            AdaptivePathwayPolicy | None
        ) = None,
        pathway_adapter: (
            AdaptivePathwayDecisionAdapter | None
        ) = None,
    ) -> None:
        self.evidence_tracker = evidence_tracker
        self.decision_engine = decision_engine
        self.pathway_policy = pathway_policy
        self.pathway_adapter = pathway_adapter

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
        previous = self.session_repository.get(
            student_id
        )

        seen_content_ids: set[str] = set()
        mastered_concept_ids: set[str] = set()

        if previous is not None:
            seen_content_ids = set(
                previous.seen_content_ids
            )

            mastered_concept_ids = set(
                previous.mastered_concept_ids
            )

        summary = self.evidence_tracker.summarize(
            student_id=student_id,
            concept_id=concept_id,
        )

        if summary.concept_mastered:
            mastered_concept_ids.add(
                concept_id
            )

        decision = self._decide(
            student_id=student_id,
            concept_id=concept_id,
            summary=summary,
            seen_content_ids=seen_content_ids,
            mastered_concept_ids=(
                mastered_concept_ids
            ),
        )

        state = self._build_state(
            student_id=student_id,
            concept_id=concept_id,
            decision=decision,
            summary=summary,
            feedback=(
                f"Welcome. You are working on "
                f"{summary.concept_name}. "
                f"{decision.reason}"
            ),
            seen_content_ids=seen_content_ids,
            mastered_concept_ids=(
                mastered_concept_ids
            ),
        )

        self.session_repository.save(
            state
        )

        return state

    def submit_outcome(
        self,
        outcome: ScoredStackOutcome,
    ) -> LearningSessionState:
        current_session = (
            self.session_repository.get(
                outcome.student_id
            )
        )

        if current_session is None:
            raise ValueError(
                "No active learning session exists "
                f"for student {outcome.student_id}."
            )

        if (
            current_session.current_concept_id
            != outcome.concept_id
        ):
            raise ValueError(
                "The submitted concept does not match "
                "the student's active learning session."
            )

        if current_session.question is None:
            raise ValueError(
                "The current learning session is not "
                "waiting for a question response."
            )

        if (
            current_session.question.id
            != outcome.question_id
        ):
            raise ValueError(
                "The submitted question does not match "
                "the question currently assigned to "
                "the student."
            )

        seen_content_ids = set(
            current_session.seen_content_ids
        )

        seen_content_ids.add(
            outcome.question_id
        )

        evidence_event = (
            self.evidence_tracker.record_outcome(
                student_id=outcome.student_id,
                question_id=outcome.question_id,
                outcome_code=outcome.outcome_code,
                score=outcome.score,
            )
        )

        summary = self.evidence_tracker.summarize(
            student_id=outcome.student_id,
            concept_id=outcome.concept_id,
        )

        mastered_concept_ids = set(
            current_session.mastered_concept_ids
        )

        if summary.concept_mastered:
            mastered_concept_ids.add(
                outcome.concept_id
            )

        decision = self._decide(
            student_id=outcome.student_id,
            concept_id=outcome.concept_id,
            summary=summary,
            seen_content_ids=seen_content_ids,
            mastered_concept_ids=(
                mastered_concept_ids
            ),
        )

        feedback = self._build_feedback(
            evidence_event=evidence_event,
            stack_feedback=(
                outcome.stack_feedback
            ),
            decision=decision,
        )

        state = self._build_state(
            student_id=outcome.student_id,
            concept_id=outcome.concept_id,
            decision=decision,
            summary=summary,
            feedback=feedback,
            seen_content_ids=seen_content_ids,
            mastered_concept_ids=(
                mastered_concept_ids
            ),
        )

        self.session_repository.save(
            state
        )

        return state

    def get_session(
        self,
        student_id: int,
    ) -> LearningSessionState | None:
        return self.session_repository.get(
            student_id
        )

    def _decide(
        self,
        *,
        student_id: int,
        concept_id: str,
        summary: ConceptEvidenceSummary,
        seen_content_ids: set[str],
        mastered_concept_ids: set[str],
    ) -> ConceptLearningDecision:
        if (
            self.pathway_policy is not None
            and self.pathway_adapter is not None
        ):
            repeat_attempt_counts = (
                self.evidence_tracker
                .evidence_repository
                .get_question_attempt_counts(
                    student_id=student_id,
                    concept_id=concept_id,
                )
            )

            pathway_decision = (
                self.pathway_policy.decide(
                    current_concept_id=concept_id,
                    mastered_concept_ids=(
                        mastered_concept_ids
                    ),
                    seen_content_ids=(
                        seen_content_ids
                    ),
                    concept_mastered=(
                        summary.concept_mastered
                    ),
                    repeat_attempt_counts=(
                        repeat_attempt_counts
                    ),
                )
            )

            return self.pathway_adapter.adapt(
                student_id=student_id,
                current_concept_id=concept_id,
                pathway_decision=(
                    pathway_decision
                ),
                evidence_score=(
                    summary.evidence_score
                ),
                concept_mastered=(
                    summary.concept_mastered
                ),
            )

        return self.decision_engine.decide(
            student_id=student_id,
            concept_id=concept_id,
        )

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
                "Correct. This response provides "
                "positive evidence of your "
                "understanding."
            )

        elif (
            evidence_event.evidence_type
            == EvidenceType.PARTIAL
        ):
            feedback_parts.append(
                "You demonstrated part of the "
                "required understanding, but some "
                "work remains."
            )

        else:
            feedback_parts.append(
                "This response shows that you need "
                "more practice with this part of "
                "the concept."
            )

        feedback_parts.append(
            evidence_event.explanation
        )

        feedback_parts.append(
            decision.reason
        )

        return " ".join(
            feedback_parts
        )

    @staticmethod
    def _build_state(
        student_id: int,
        concept_id: str,
        decision: ConceptLearningDecision,
        summary: ConceptEvidenceSummary,
        feedback: str,
        seen_content_ids: set[str],
        mastered_concept_ids: set[str],
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

        session_complete = (
            decision.action
            in {
                ConceptDecisionAction.REMEDIATE_CONCEPT,
                ConceptDecisionAction.ADVANCE_CONCEPT,
                ConceptDecisionAction.COMPLETE_CONCEPT,
            }
        )

        progress = SessionProgress(
            concept_id=summary.concept_id,
            concept_name=summary.concept_name,
            attempts=summary.attempts,
            evidence_score=(
                summary.evidence_score
            ),
            positive_evidence_count=(
                summary.positive_evidence_count
            ),
            partial_evidence_count=(
                summary.partial_evidence_count
            ),
            negative_evidence_count=(
                summary.negative_evidence_count
            ),
            concept_mastered=(
                summary.concept_mastered
            ),
        )

        return LearningSessionState(
            student_id=student_id,
            current_concept_id=concept_id,
            question=question,
            action=decision.action,
            feedback=feedback,
            decision_reason=decision.reason,
            progress=progress,
            next_concept_id=(
                decision.next_concept_id
            ),
            session_complete=(
                session_complete
            ),
            seen_content_ids=(
                seen_content_ids
            ),
            mastered_concept_ids=(
                mastered_concept_ids
            ),
        )
