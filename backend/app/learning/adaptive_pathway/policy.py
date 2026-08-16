from dataclasses import dataclass
from enum import Enum

from backend.app.content.models import (
    LearningContentItem,
)
from backend.app.learning.adaptive_pathway.content_selector import (
    AdaptiveContentSelector,
)
from backend.app.learning.adaptive_pathway.selector import (
    AdaptiveConceptSelector,
)


class PathwayAction(str, Enum):
    PRACTICE = "practice"
    REPEAT = "repeat"
    REMEDIATE = "remediate"
    ADVANCE = "advance"
    NO_CONTENT = "no_content"


@dataclass(frozen=True)
class PathwayDecision:
    action: PathwayAction
    concept_id: str
    question: LearningContentItem | None
    reason: str


class AdaptivePathwayPolicy:
    """
    Combine concept-level and content-level selection.

    The policy is deterministic and keeps curriculum
    progression separate from question retrieval.
    """

    def __init__(
        self,
        concept_selector: AdaptiveConceptSelector,
        content_selector: AdaptiveContentSelector,
    ) -> None:
        self.concept_selector = concept_selector
        self.content_selector = content_selector

    def decide(
        self,
        current_concept_id: str,
        mastered_concept_ids: set[str],
        seen_content_ids: set[str] | None = None,
        *,
        concept_mastered: bool,
    ) -> PathwayDecision:
        seen = set(
            seen_content_ids or set()
        )

        question = (
            self.content_selector.select_question(
                concept_id=current_concept_id,
                seen_content_ids=seen,
            )
        )

        if question is not None:
            return PathwayDecision(
                action=PathwayAction.PRACTICE,
                concept_id=current_concept_id,
                question=question,
                reason=(
                    "Unseen deliverable content remains "
                    "for the current concept."
                ),
            )

        if concept_mastered:
            next_concept = (
                self.concept_selector
                .select_next_concept(
                    current_concept_id=(
                        current_concept_id
                    ),
                    mastered_concept_ids=(
                        mastered_concept_ids
                        | {current_concept_id}
                    ),
                )
            )

            if next_concept is not None:
                next_question = (
                    self.content_selector
                    .select_question(
                        concept_id=(
                            next_concept.concept_id
                        ),
                        seen_content_ids=seen,
                    )
                )

                return PathwayDecision(
                    action=PathwayAction.ADVANCE,
                    concept_id=(
                        next_concept.concept_id
                    ),
                    question=next_question,
                    reason=(
                        "Current concept is mastered "
                        "and its unseen content is "
                        "exhausted."
                    ),
                )

        remediation = (
            self.concept_selector
            .select_remediation_concept(
                current_concept_id=(
                    current_concept_id
                ),
                mastered_concept_ids=(
                    mastered_concept_ids
                ),
            )
        )

        if remediation is not None:
            remediation_question = (
                self.content_selector
                .select_question(
                    concept_id=(
                        remediation.concept_id
                    ),
                    seen_content_ids=seen,
                )
            )

            if remediation_question is not None:
                return PathwayDecision(
                    action=(
                        PathwayAction.REMEDIATE
                    ),
                    concept_id=(
                        remediation.concept_id
                    ),
                    question=(
                        remediation_question
                    ),
                    reason=(
                        "Current concept is not "
                        "mastered and unseen "
                        "remediation content is "
                        "available."
                    ),
                )

        repeat = (
            self.content_selector.select_question(
                concept_id=current_concept_id,
                seen_content_ids=seen,
                allow_repeat=True,
            )
        )

        if repeat is not None:
            return PathwayDecision(
                action=PathwayAction.REPEAT,
                concept_id=current_concept_id,
                question=repeat,
                reason=(
                    "No unseen content or usable "
                    "remediation remains, so a "
                    "repeat is explicitly allowed."
                ),
            )

        return PathwayDecision(
            action=PathwayAction.NO_CONTENT,
            concept_id=current_concept_id,
            question=None,
            reason=(
                "No deliverable content is "
                "available for the pathway."
            ),
        )