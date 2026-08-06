from dataclasses import dataclass

from backend.app.learning.concept_mastery.models import (
    MasteryStatus,
)


@dataclass(frozen=True)
class ConceptMasteryPolicy:
    """
    Provisional deterministic mastery policy.

    These rules exist for development and testing. They can later
    be replaced by educator-validated thresholds, IRT, Bayesian
    Knowledge Tracing, or another statistical learner model.
    """

    expected_evidence_attempts: int = 5
    learning_attempt_threshold: int = 2
    practice_attempt_threshold: int = 3

    def calculate_confidence(
        self,
        attempts: int,
        mastered: bool,
    ) -> float:
        if attempts <= 0:
            return 0.0

        confidence = min(
            attempts / self.expected_evidence_attempts,
            1.0,
        )

        if mastered:
            confidence = max(confidence, 0.8)

        return confidence

    def determine_status(
        self,
        attempts: int,
        concept_mastered: bool,
        review_required: bool,
        mastery_check_attempted: bool,
    ) -> MasteryStatus:
        if review_required:
            return MasteryStatus.REVIEW_REQUIRED

        if concept_mastered:
            return MasteryStatus.MASTERED

        if attempts == 0:
            return MasteryStatus.NOT_STARTED

        if (
            mastery_check_attempted
            or attempts >= self.practice_attempt_threshold
        ):
            return MasteryStatus.PRACTICING

        if attempts >= self.learning_attempt_threshold:
            return MasteryStatus.LEARNING

        return MasteryStatus.INTRODUCED
