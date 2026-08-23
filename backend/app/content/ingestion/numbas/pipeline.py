from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from backend.app.content.ingestion.concept_mapper import (
    ContentConceptMapper,
)
from backend.app.content.ingestion.numbas.catalog import (
    NumbasCatalog,
)
from backend.app.content.ingestion.numbas.converter import (
    NumbasContentConverter,
    NumbasConversionError,
)
from backend.app.content.ingestion.numbas.importer import (
    NumbasContentImporter,
)
from backend.app.content.ingestion.numbas.metadata_builder import (
    NumbasMetadataBuilder,
)
from backend.app.content.models import (
    LearningContentItem,
)


@dataclass(frozen=True)
class NumbasPipelineIssue:
    question_id: str
    filename: str
    status: str
    reason: str


@dataclass(frozen=True)
class NumbasBulkPipelineResult:
    discovered_count: int
    accepted_count: int
    review_count: int
    rejected_count: int
    unmapped_count: int

    items: tuple[
        LearningContentItem,
        ...
    ]

    issues: tuple[
        NumbasPipelineIssue,
        ...
    ]


class NumbasBulkContentPipeline:
    def __init__(
        self,
        *,
        concept_mapper: ContentConceptMapper,
        converter: NumbasContentConverter,
    ) -> None:
        self.concept_mapper = (
            concept_mapper
        )

        self.converter = converter

        self.importer = (
            NumbasContentImporter()
        )

        self.metadata_builder = (
            NumbasMetadataBuilder()
        )

    def build(
        self,
        *,
        source_directory: Path,
        catalog_path: Path,
    ) -> NumbasBulkPipelineResult:
        catalog = NumbasCatalog.load(
            catalog_path
        )

        files = sorted(
            source_directory.glob(
                "question-*.exam"
            )
        )

        items: list[
            LearningContentItem
        ] = []

        issues: list[
            NumbasPipelineIssue
        ] = []

        review_count = 0
        rejected_count = 0
        unmapped_count = 0

        for path in files:
            try:
                record = (
                    self.importer
                    .import_file(
                        path
                    )
                )
            except Exception as error:
                rejected_count += 1

                issues.append(
                    NumbasPipelineIssue(
                        question_id="unknown",
                        filename=path.name,
                        status="rejected",
                        reason=str(
                            error
                        ),
                    )
                )

                continue

            catalog_entry = catalog.get(
                record.external_id
            )

            if catalog_entry is None:
                review_count += 1

                issues.append(
                    NumbasPipelineIssue(
                        question_id=(
                            record.external_id
                        ),
                        filename=path.name,
                        status=(
                            "review_required"
                        ),
                        reason=(
                            "Question is not present "
                            "in the approved Numbas "
                            "catalogue."
                        ),
                    )
                )

                continue

            mapping = (
                self.concept_mapper
                .map_record(
                    record
                )
            )

            if not mapping.is_mapped:
                if (
                    mapping.status.value
                    == "unmapped"
                ):
                    unmapped_count += 1
                else:
                    review_count += 1

                issues.append(
                    NumbasPipelineIssue(
                        question_id=(
                            record.external_id
                        ),
                        filename=path.name,
                        status=(
                            mapping.status.value
                        ),
                        reason=(
                            mapping.reason
                        ),
                    )
                )

                continue

            metadata = (
                self.metadata_builder
                .build(
                    path=path,
                    catalog_entry=(
                        catalog_entry
                    ),
                )
            )

            try:
                item = (
                    self.converter.convert(
                        record=record,
                        mapping=mapping,
                        metadata=metadata,
                    )
                )
            except NumbasConversionError as error:
                message = str(
                    error
                )

                lowered = (
                    message.lower()
                )

                if (
                    "should not"
                    in lowered
                    or "outside"
                    in lowered
                ):
                    rejected_count += 1
                    status = "rejected"
                else:
                    review_count += 1
                    status = (
                        "review_required"
                    )

                issues.append(
                    NumbasPipelineIssue(
                        question_id=(
                            record.external_id
                        ),
                        filename=path.name,
                        status=status,
                        reason=message,
                    )
                )

                continue

            items.append(
                item
            )

        return NumbasBulkPipelineResult(
            discovered_count=len(
                files
            ),
            accepted_count=len(
                items
            ),
            review_count=review_count,
            rejected_count=(
                rejected_count
            ),
            unmapped_count=(
                unmapped_count
            ),
            items=tuple(
                items
            ),
            issues=tuple(
                issues
            ),
        )
