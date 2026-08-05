from dataclasses import dataclass

from backend.app.learning.concept_evidence.models import (
    EvidenceType,
)


@dataclass(frozen=True)
class ConceptEvidencePolicy:
    """
    Provisional development policy.

    This deterministic policy exists so the concept-evidence
    architecture can be tested before educator validation,
    empirical calibration, and future IRT integration.
    """

    mastery_threshold: float = 0.75

    standard_question_weight: float = 1.0
    mastery_question_weight: float = 2.0

    def classify_score(
        self,
        score: float,
    ) -> EvidenceType:
        if score >= 1.0:
            return EvidenceType.POSITIVE

        if score > 0.0:
            return EvidenceType.PARTIAL

        return EvidenceType.NEGATIVE

    def get_weight(
        self,
        required_for_mastery: bool,
    ) -> float:
        if required_for_mastery:
            return self.mastery_question_weight

        return self.standard_question_weight
