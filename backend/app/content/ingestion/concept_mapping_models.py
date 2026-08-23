from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MappingConfidence(
    str,
    Enum,
):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MappingStatus(
    str,
    Enum,
):
    MAPPED = "mapped"
    REVIEW_REQUIRED = "review_required"
    UNMAPPED = "unmapped"


@dataclass(frozen=True)
class ConceptMappingDecision:
    external_id: str
    concept_id: str | None
    status: MappingStatus
    confidence: MappingConfidence
    reason: str
    matched_rule: str | None = None

    @property
    def is_mapped(
        self,
    ) -> bool:
        return (
            self.status
            == MappingStatus.MAPPED
            and self.concept_id
            is not None
        )
