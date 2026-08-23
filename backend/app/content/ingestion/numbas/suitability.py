from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from backend.app.content.ingestion.numbas.models import (
    NumbasQuestionMetadata,
    NumbasQuestionStatus,
)
from backend.app.content.models import (
    LicenseDecision,
)


class EducationalSuitability(
    str,
    Enum,
):
    ACCEPT = "accept"
    REVIEW = "review"
    REJECT = "reject"


@dataclass(frozen=True)
class NumbasSuitabilityDecision:
    decision: EducationalSuitability

    concept_id: str | None
    reason: str

    quality_ready: bool
    license_ready: bool
    concept_ready: bool

    @property
    def can_enter_repository(
        self,
    ) -> bool:
        return (
            self.decision
            == EducationalSuitability.ACCEPT
        )


class NumbasSuitabilityGate:
    """
    Decide whether a Numbas question is suitable for
    the current Grade 9 -> Grade 10 transition bank.

    This gate intentionally separates:
      1. technical/author quality,
      2. licensing,
      3. curriculum relevance.
    """

    def evaluate(
        self,
        *,
        metadata: NumbasQuestionMetadata,
        concept_id: str | None,
        known_transition_concept_ids: set[str],
        license_decision: LicenseDecision,
    ) -> NumbasSuitabilityDecision:
        if metadata.status in {
            NumbasQuestionStatus.DOES_NOT_WORK,
            NumbasQuestionStatus.SHOULD_NOT_USE,
        }:
            return NumbasSuitabilityDecision(
                decision=(
                    EducationalSuitability.REJECT
                ),
                concept_id=concept_id,
                reason=(
                    "Numbas marks this question as "
                    "unsuitable for learner use."
                ),
                quality_ready=False,
                license_ready=(
                    license_decision
                    == LicenseDecision.ALLOWED
                ),
                concept_ready=False,
            )

        if metadata.status != (
            NumbasQuestionStatus.READY
        ):
            return NumbasSuitabilityDecision(
                decision=(
                    EducationalSuitability.REVIEW
                ),
                concept_id=concept_id,
                reason=(
                    "The question is not marked "
                    "'Ready to use' in Numbas."
                ),
                quality_ready=False,
                license_ready=(
                    license_decision
                    == LicenseDecision.ALLOWED
                ),
                concept_ready=(
                    concept_id
                    in known_transition_concept_ids
                    if concept_id
                    else False
                ),
            )

        if (
            license_decision
            != LicenseDecision.ALLOWED
        ):
            return NumbasSuitabilityDecision(
                decision=(
                    EducationalSuitability.REVIEW
                ),
                concept_id=concept_id,
                reason=(
                    "The question's licence has not "
                    "been approved for delivery."
                ),
                quality_ready=True,
                license_ready=False,
                concept_ready=(
                    concept_id
                    in known_transition_concept_ids
                    if concept_id
                    else False
                ),
            )

        if concept_id is None:
            return NumbasSuitabilityDecision(
                decision=(
                    EducationalSuitability.REVIEW
                ),
                concept_id=None,
                reason=(
                    "The question has not yet been "
                    "mapped to a transition concept."
                ),
                quality_ready=True,
                license_ready=True,
                concept_ready=False,
            )

        if (
            concept_id
            not in known_transition_concept_ids
        ):
            return NumbasSuitabilityDecision(
                decision=(
                    EducationalSuitability.REJECT
                ),
                concept_id=concept_id,
                reason=(
                    "The mapped concept is outside "
                    "the current Grade 9 -> Grade 10 "
                    "transition knowledge graph."
                ),
                quality_ready=True,
                license_ready=True,
                concept_ready=False,
            )

        return NumbasSuitabilityDecision(
            decision=(
                EducationalSuitability.ACCEPT
            ),
            concept_id=concept_id,
            reason=(
                "Question is ready, licensed, and "
                "mapped to the transition graph."
            ),
            quality_ready=True,
            license_ready=True,
            concept_ready=True,
        )
