from backend.app.learning.adaptive_pathway.policy import (
    PathwayAction,
    PathwayDecision,
)
from backend.app.learning.concept_decision.models import (
    ConceptDecisionAction,
    ConceptLearningDecision,
)
from backend.app.learning.knowledge_graph.repository import (
    KnowledgeGraphRepository,
)


class AdaptivePathwayDecisionAdapter:
    """
    Convert pathway decisions into the decision model used by
    AdaptiveLearningSessionEngine.

    A question may only belong to the current concept.

    Cross-concept decisions such as ADVANCE and REMEDIATE carry
    only next_concept_id. The destination concept starts its own
    session and selects its own question.
    """

    def __init__(
        self,
        knowledge_graph: KnowledgeGraphRepository,
    ) -> None:
        self.knowledge_graph = knowledge_graph

    def adapt(
        self,
        *,
        student_id: int,
        current_concept_id: str,
        pathway_decision: PathwayDecision,
        evidence_score: float,
        concept_mastered: bool,
    ) -> ConceptLearningDecision:
        current = self.knowledge_graph.require(
            current_concept_id
        )

        action = self._map_action(
            pathway_decision.action
        )

        next_question_id = None
        next_question_name = None
        next_concept_id = None

        # A question can only be attached when the learner
        # remains inside the current concept.
        if pathway_decision.action in {
            PathwayAction.PRACTICE,
            PathwayAction.REPEAT,
        }:
            if pathway_decision.question is not None:
                next_question_id = (
                    pathway_decision.question.content_id
                )

                next_question_name = (
                    pathway_decision.question.title
                )

        # Cross-concept transitions contain no question.
        # The new concept starts a fresh session and selects
        # its own first activity.
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
            current_concept_name=current.name,
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
        action: PathwayAction,
    ) -> ConceptDecisionAction:
        if action == PathwayAction.PRACTICE:
            return (
                ConceptDecisionAction.TARGET_PRACTICE
            )

        if action == PathwayAction.REPEAT:
            return (
                ConceptDecisionAction.TARGET_PRACTICE
            )

        if action == PathwayAction.REMEDIATE:
            return (
                ConceptDecisionAction.REMEDIATE_CONCEPT
            )

        if action == PathwayAction.ADVANCE:
            return (
                ConceptDecisionAction.ADVANCE_CONCEPT
            )

        return (
            ConceptDecisionAction.COMPLETE_CONCEPT
        )
