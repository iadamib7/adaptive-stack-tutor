from __future__ import annotations

from backend.app.content.ingestion.concept_mapping_models import (
    ConceptMappingDecision,
)
from backend.app.content.ingestion.models import (
    ImportedContentRecord,
)
from backend.app.content.ingestion.numbas.models import (
    NumbasQuestionMetadata,
    NumbasQuestionStatus,
)
from backend.app.content.ingestion.numbas.suitability import (
    EducationalSuitability,
    NumbasSuitabilityGate,
)
from backend.app.content.models import (
    ContentDifficulty,
    ContentKind,
    ContentSource,
    LearningContentItem,
)
from backend.app.content.sources.license_gate import (
    ContentLicenseGate,
)
from backend.app.content.sources.registry import (
    ContentSourceRegistry,
)


class NumbasConversionError(
    ValueError
):
    pass


class NumbasContentConverter:
    """
    Convert an imported Numbas record into an approved
    LearningContentItem only after concept, license, and
    educational suitability checks pass.
    """

    def __init__(
        self,
        *,
        source_registry: ContentSourceRegistry,
        known_transition_concept_ids: set[str],
    ) -> None:
        self.source_registry = (
            source_registry
        )

        self.known_transition_concept_ids = (
            known_transition_concept_ids
        )

        self.license_gate = (
            ContentLicenseGate()
        )

        self.suitability_gate = (
            NumbasSuitabilityGate()
        )

    def convert(
        self,
        *,
        record: ImportedContentRecord,
        mapping: ConceptMappingDecision,
        metadata: NumbasQuestionMetadata,
        source_id: str = "numbas-cc-by",
    ) -> LearningContentItem:
        if (
            record.external_id
            != mapping.external_id
        ):
            raise NumbasConversionError(
                "Imported record and mapping decision "
                "refer to different question IDs."
            )

        if (
            record.external_id
            != metadata.question_id
        ):
            raise NumbasConversionError(
                "Imported record and Numbas metadata "
                "refer to different question IDs."
            )

        source = self.source_registry.require(
            source_id
        )

        license_result = (
            self.license_gate.evaluate(
                source=source,
                item_license_code=(
                    metadata.license_code
                ),
                item_license_url=(
                    metadata.license_url
                ),
            )
        )

        suitability = (
            self.suitability_gate.evaluate(
                metadata=metadata,
                concept_id=(
                    mapping.concept_id
                ),
                known_transition_concept_ids=(
                    self
                    .known_transition_concept_ids
                ),
                license_decision=(
                    license_result.decision
                ),
            )
        )

        if (
            suitability.decision
            != EducationalSuitability.ACCEPT
        ):
            raise NumbasConversionError(
                "Numbas content is not approved for "
                "learner delivery: "
                f"{suitability.reason}"
            )

        if mapping.concept_id is None:
            raise NumbasConversionError(
                "Approved Numbas content is missing "
                "a concept mapping."
            )

        attribution = (
            ", ".join(
                metadata.author_names
            )
        )

        return LearningContentItem(
            content_id=(
                "numbas:"
                f"{record.external_id}"
            ),
            concept_id=(
                mapping.concept_id
            ),
            title=record.title,
            kind=ContentKind.QUESTION,
            source=ContentSource.OER,
            source_reference=(
                metadata.source_url
            ),
            difficulty=(
                ContentDifficulty.MEDIUM
            ),
            skill_tags=(
                mapping.concept_id,
            ),
            license_code=(
                license_result.license_code
            ),
            license_url=(
                license_result.license_url
            ),
            attribution=attribution,
            license_decision=(
                license_result.decision
            ),
            variant_group_id=(
                "numbas:"
                f"{record.external_id}"
            ),
            active=True,
            metadata=(
                (
                    "provider",
                    "numbas",
                ),
                (
                    "project",
                    metadata.project_name,
                ),
                (
                    "mapping_rule",
                    mapping.matched_rule
                    or "",
                ),
                (
                    "question_status",
                    metadata.status.value,
                ),
                (
                    "part_count",
                    dict(
                        record.metadata
                    ).get(
                        "part_count",
                        "",
                    ),
                ),
            ),
        )
