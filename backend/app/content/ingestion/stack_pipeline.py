from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from backend.app.content.ingestion.concept_mapper import (
    ContentConceptMapper,
)
from backend.app.content.ingestion.converter import (
    ImportedContentConverter,
)
from backend.app.content.ingestion.stack_importer import (
    StackContentImporter,
)
from backend.app.content.models import (
    LearningContentItem,
)
from backend.app.content.repository import (
    LearningContentRepository,
)
from backend.app.content.validator import (
    LearningContentValidator,
)
from backend.app.learning.knowledge_graph.repository import (
    KnowledgeGraphRepository,
)


@dataclass(frozen=True)
class ContentPipelineResult:
    imported_count: int
    mapped_count: int
    unmapped_count: int
    review_required_count: int
    items: tuple[
        LearningContentItem,
        ...
    ]


class StackContentPipeline:
    def __init__(
        self,
        *,
        knowledge_graph: (
            KnowledgeGraphRepository
        ),
        concept_mapper: (
            ContentConceptMapper
        ),
    ) -> None:
        self.knowledge_graph = (
            knowledge_graph
        )

        self.concept_mapper = (
            concept_mapper
        )

        self.importer = (
            StackContentImporter()
        )

        self.converter = (
            ImportedContentConverter()
        )

        self.validator = (
            LearningContentValidator()
        )

    def build(
        self,
        export_path: Path,
    ) -> ContentPipelineResult:
        records = (
            self.importer.import_file(
                export_path
            )
        )

        mappings = (
            self.concept_mapper
            .map_records(
                records
            )
        )

        items = (
            self.converter.convert_many(
                records=records,
                mappings=mappings,
            )
        )

        known_concept_ids = {
            concept.concept_id
            for concept
            in self.knowledge_graph
            .all_concepts()
        }

        self.validator.require_valid(
            items=items,
            known_concept_ids=(
                known_concept_ids
            ),
        )

        mapped_count = sum(
            1
            for decision in mappings
            if decision.is_mapped
        )

        review_required_count = sum(
            1
            for decision in mappings
            if (
                decision.status.value
                == "review_required"
            )
        )

        return ContentPipelineResult(
            imported_count=len(
                records
            ),
            mapped_count=mapped_count,
            unmapped_count=(
                len(records)
                - mapped_count
                - review_required_count
            ),
            review_required_count=(
                review_required_count
            ),
            items=tuple(
                items
            ),
        )

    def repository(
        self,
        export_path: Path,
    ) -> LearningContentRepository:
        result = self.build(
            export_path
        )

        return LearningContentRepository(
            result.items
        )
