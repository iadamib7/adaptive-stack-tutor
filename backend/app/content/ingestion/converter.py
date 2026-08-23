from __future__ import annotations

from backend.app.content.ingestion.concept_mapping_models import (
    ConceptMappingDecision,
)
from backend.app.content.ingestion.models import (
    ImportedContentRecord,
)
from backend.app.content.models import (
    ContentDifficulty,
    ContentKind,
    ContentSource,
    LearningContentItem,
    LicenseDecision,
)


class ContentConversionError(
    ValueError
):
    pass


class ImportedContentConverter:
    """
    Convert mapped provider records into the common
    LearningContentItem representation.

    Only confidently mapped content may enter the
    deliverable content repository.
    """

    def convert(
        self,
        *,
        record: ImportedContentRecord,
        mapping: ConceptMappingDecision,
    ) -> LearningContentItem:
        if (
            record.external_id
            != mapping.external_id
        ):
            raise ContentConversionError(
                "Imported record and mapping decision "
                "refer to different external IDs."
            )

        if not mapping.is_mapped:
            raise ContentConversionError(
                "Content cannot be converted because "
                "it does not have an approved concept "
                "mapping."
            )

        if mapping.concept_id is None:
            raise ContentConversionError(
                "Mapped content is missing concept_id."
            )

        source = self._content_source(
            record.source_provider
        )

        return LearningContentItem(
            content_id=self._content_id(
                record
            ),
            concept_id=mapping.concept_id,
            title=record.title,
            kind=ContentKind.QUESTION,
            source=source,
            source_reference=(
                record.source_reference
            ),
            difficulty=(
                ContentDifficulty.MEDIUM
            ),
            skill_tags=(
                mapping.concept_id,
            ),
            license_code=(
                self._license_code(
                    source
                )
            ),
            attribution=(
                self._attribution(
                    source
                )
            ),
            license_decision=(
                self._license_decision(
                    source
                )
            ),
            variant_group_id=(
                self._variant_group_id(
                    record
                )
            ),
            metadata=(
                (
                    "external_id",
                    record.external_id,
                ),
                (
                    "category_path",
                    record.category_path,
                ),
                (
                    "input_count",
                    str(
                        len(
                            record.input_names
                        )
                    ),
                ),
                (
                    "prt_count",
                    str(
                        len(
                            record.prt_names
                        )
                    ),
                ),
                (
                    "mapping_rule",
                    mapping.matched_rule
                    or "",
                ),
                (
                    "mapping_confidence",
                    mapping.confidence.value,
                ),
            ),
        )

    def convert_many(
        self,
        *,
        records: list[
            ImportedContentRecord
        ],
        mappings: list[
            ConceptMappingDecision
        ],
    ) -> list[
        LearningContentItem
    ]:
        mapping_by_id = {
            mapping.external_id: mapping
            for mapping in mappings
        }

        items: list[
            LearningContentItem
        ] = []

        for record in records:
            mapping = mapping_by_id.get(
                record.external_id
            )

            if (
                mapping is None
                or not mapping.is_mapped
            ):
                continue

            items.append(
                self.convert(
                    record=record,
                    mapping=mapping,
                )
            )

        return items

    @staticmethod
    def _content_id(
        record: ImportedContentRecord,
    ) -> str:
        provider = (
            record.source_provider
            .strip()
            .lower()
            .replace(" ", "-")
        )

        return (
            f"{provider}:"
            f"{record.external_id}"
        )

    @staticmethod
    def _variant_group_id(
        record: ImportedContentRecord,
    ) -> str | None:
        if record.deployed_seeds:
            return (
                "stack:"
                f"{record.external_id}"
            )

        return None

    @staticmethod
    def _content_source(
        provider: str,
    ) -> ContentSource:
        normalized = (
            provider.strip().lower()
        )

        mapping = {
            "stack": ContentSource.STACK,
            "openstax": (
                ContentSource.OPENSTAX
            ),
            "oer": ContentSource.OER,
            "teacher": (
                ContentSource.TEACHER
            ),
            "generated": (
                ContentSource.GENERATED
            ),
            "internal": (
                ContentSource.INTERNAL
            ),
        }

        try:
            return mapping[
                normalized
            ]
        except KeyError as error:
            raise ContentConversionError(
                "Unsupported content provider: "
                f"{provider}"
            ) from error

    @staticmethod
    def _license_decision(
        source: ContentSource,
    ) -> LicenseDecision:
        if source in {
            ContentSource.INTERNAL,
            ContentSource.GENERATED,
        }:
            return (
                LicenseDecision.ALLOWED
            )

        # Imported external content is not made
        # deliverable merely because parsing succeeded.
        return LicenseDecision.REVIEW

    @staticmethod
    def _license_code(
        source: ContentSource,
    ) -> str:
        if source == ContentSource.INTERNAL:
            return "INTERNAL"

        if source == ContentSource.GENERATED:
            return "INTERNAL-GENERATED"

        return ""

    @staticmethod
    def _attribution(
        source: ContentSource,
    ) -> str:
        if source == ContentSource.STACK:
            return (
                "Imported from STACK source content; "
                "license review required."
            )

        return ""
