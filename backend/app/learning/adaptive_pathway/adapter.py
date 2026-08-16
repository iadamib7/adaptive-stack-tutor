from backend.app.learning.adaptive_pathway.policy import (
    PathwayAction,
    PathwayDecision,
)
from backend.app.learning.concept_decision.models import (
    ConceptDecisionAction,
    ConceptLearningDecision,
)


class PathwayDecisionAdapter:
    """
    Translate pathway decisions into the existing
    session-compatible concept decision model.
    """

    @staticmethod
    def to_concept_decision(
        *,
        student_id: int,
        current_concept_id: str,
        current_concept_name: str,
        pathway_decision: PathwayDecision,
        evidence_score: float,
        concept_mastered: bool,
    ) -> ConceptLearningDecision:
        action = (
            PathwayDecisionAdapter._map_action(
                pathway_decision
            )
        )

        next_question_id = None
        next_question_name = None

        if pathway_decision.question is not None:
            next_question_id = (
                pathway_decision.question.content_id
            )

            next_question_name = (
                pathway_decision.question.title
            )

        next_concept_id = None

        if pathway_decision.action in {
            PathwayAction.ADVANCE,
            PathwayAction.REMEDIATE,
        }:
            next_concept_id = (
                pathway_decision.concept_id
            )

        return ConceptLearningDecision(
            student_id=student_id,
            current_concept_id=current_concept_id,
            current_concept_name=current_concept_name,
            action=action,
            next_question_id=next_question_id,
            next_question_name=next_question_name,
            next_concept_id=next_concept_id,
            evidence_score=evidence_score,
            concept_mastered=concept_mastered,
            reason=pathway_decision.reason,
        )

    @staticmethod
    def _map_action(
        decision: PathwayDecision,
    ) -> ConceptDecisionAction:
        if decision.action in {
            PathwayAction.PRACTICE,
            PathwayAction.REPEAT,
            PathwayAction.REMEDIATE,
        }:
            return (
                ConceptDecisionAction.TARGET_PRACTICE
            )

        if decision.action == PathwayAction.ADVANCE:
            return (
                ConceptDecisionAction.ADVANCE_CONCEPT
            )

        return (
            ConceptDecisionAction.COMPLETE_CONCEPT
        )