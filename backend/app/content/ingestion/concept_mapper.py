from __future__ import annotations

from backend.app.content.ingestion.concept_mapping_models import (
    ConceptMappingDecision,
    MappingConfidence,
    MappingStatus,
)
from backend.app.content.ingestion.concept_mapping_rules import (
    ConceptMappingRule,
)
from backend.app.content.ingestion.models import (
    ImportedContentRecord,
)
from backend.app.learning.knowledge_graph.repository import (
    KnowledgeGraphRepository,
)


class ContentConceptMapper:
    """
    Deterministically map imported educational content
    onto knowledge-graph concepts.

    More-specific rules win over broader rules.
    Equally specific conflicting rules require review.
    """

    def __init__(
        self,
        *,
        knowledge_graph: KnowledgeGraphRepository,
        rules: list[
            ConceptMappingRule
        ],
    ) -> None:
        self.knowledge_graph = (
            knowledge_graph
        )

        self.rules = rules

        self._validate_rules()

    def map_record(
        self,
        record: ImportedContentRecord,
    ) -> ConceptMappingDecision:
        matches = [
            rule
            for rule in self.rules
            if rule.matches(
                record
            )
        ]

        if not matches:
            return ConceptMappingDecision(
                external_id=(
                    record.external_id
                ),
                concept_id=None,
                status=(
                    MappingStatus.UNMAPPED
                ),
                confidence=(
                    MappingConfidence.LOW
                ),
                reason=(
                    "No concept mapping rule "
                    "matched this content."
                ),
            )

        selected_matches = (
            self._most_specific_rules(
                matches
            )
        )

        concept_ids = {
            rule.concept_id
            for rule in selected_matches
        }

        if len(
            concept_ids
        ) > 1:
            return ConceptMappingDecision(
                external_id=(
                    record.external_id
                ),
                concept_id=None,
                status=(
                    MappingStatus
                    .REVIEW_REQUIRED
                ),
                confidence=(
                    MappingConfidence.LOW
                ),
                reason=(
                    "Multiple equally specific "
                    "concept mapping rules matched "
                    "different concepts."
                ),
                matched_rule=(
                    ",".join(
                        rule.rule_id
                        for rule
                        in selected_matches
                    )
                ),
            )

        selected = (
            selected_matches[0]
        )

        return ConceptMappingDecision(
            external_id=(
                record.external_id
            ),
            concept_id=(
                selected.concept_id
            ),
            status=(
                MappingStatus.MAPPED
            ),
            confidence=(
                MappingConfidence.HIGH
            ),
            reason=(
                "Matched the most specific "
                "deterministic curriculum rule."
            ),
            matched_rule=(
                selected.rule_id
            ),
        )

    def map_records(
        self,
        records: list[
            ImportedContentRecord
        ],
    ) -> list[
        ConceptMappingDecision
    ]:
        return [
            self.map_record(
                record
            )
            for record in records
        ]

    @staticmethod
    def _rule_specificity(
        rule: ConceptMappingRule,
    ) -> int:
        return (
            len(
                rule.category_contains
            )
            + len(
                rule.title_contains
            )
        )

    @classmethod
    def _most_specific_rules(
        cls,
        rules: list[
            ConceptMappingRule
        ],
    ) -> list[
        ConceptMappingRule
    ]:
        highest_specificity = max(
            cls._rule_specificity(
                rule
            )
            for rule in rules
        )

        return [
            rule
            for rule in rules
            if cls._rule_specificity(
                rule
            )
            == highest_specificity
        ]

    def _validate_rules(
        self,
    ) -> None:
        seen_rule_ids: set[str] = set()

        for rule in self.rules:
            if (
                rule.rule_id
                in seen_rule_ids
            ):
                raise ValueError(
                    "Duplicate concept mapping "
                    f"rule ID: {rule.rule_id}"
                )

            seen_rule_ids.add(
                rule.rule_id
            )

            self.knowledge_graph.require(
                rule.concept_id
            )
