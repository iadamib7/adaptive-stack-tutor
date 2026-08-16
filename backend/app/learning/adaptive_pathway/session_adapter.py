from dataclasses import dataclass, field

from backend.app.content.models import (
    LearningContentItem,
)
from backend.app.learning.adaptive_pathway.policy import (
    AdaptivePathwayPolicy,
    PathwayAction,
    PathwayDecision,
)


@dataclass
class AdaptiveLearnerPathwayState:
    student_id: int

    current_concept_id: str

    mastered_concept_ids: set[str] = field(
        default_factory=set
    )

    seen_content_ids: set[str] = field(
        default_factory=set
    )


@dataclass(frozen=True)
class AdaptivePathwaySessionResult:
    student_id: int

    action: PathwayAction

    concept_id: str

    question: LearningContentItem | None

    reason: str


class AdaptivePathwaySessionAdapter:
    """
    Apply the adaptive pathway policy to one learner.

    This adapter keeps pathway selection separate from the
    existing STACK scoring and curriculum-evidence engines.
    """

    def __init__(
        self,
        pathway_policy: AdaptivePathwayPolicy,
    ) -> None:
        self.pathway_policy = pathway_policy

    def decide_next(
        self,
        state: AdaptiveLearnerPathwayState,
        *,
        concept_mastered: bool,
    ) -> AdaptivePathwaySessionResult:
        decision = self.pathway_policy.decide(
            current_concept_id=(
                state.current_concept_id
            ),
            mastered_concept_ids=(
                state.mastered_concept_ids
            ),
            seen_content_ids=(
                state.seen_content_ids
            ),
            concept_mastered=concept_mastered,
        )

        self._apply_decision(
            state=state,
            decision=decision,
            concept_mastered=concept_mastered,
        )

        return AdaptivePathwaySessionResult(
            student_id=state.student_id,
            action=decision.action,
            concept_id=decision.concept_id,
            question=decision.question,
            reason=decision.reason,
        )

    @staticmethod
    def _apply_decision(
        state: AdaptiveLearnerPathwayState,
        decision: PathwayDecision,
        concept_mastered: bool,
    ) -> None:
        previous_concept = (
            state.current_concept_id
        )

        if concept_mastered:
            state.mastered_concept_ids.add(
                previous_concept
            )

        state.current_concept_id = (
            decision.concept_id
        )

        if decision.question is not None:
            state.seen_content_ids.add(
                decision.question.content_id
            )