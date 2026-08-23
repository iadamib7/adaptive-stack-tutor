from __future__ import annotations

from dataclasses import dataclass

from backend.app.content.ingestion.models import (
    ImportedContentRecord,
)


@dataclass(frozen=True)
class ConceptMappingRule:
    rule_id: str
    concept_id: str

    category_contains: tuple[str, ...] = ()
    title_contains: tuple[str, ...] = ()

    def matches(
        self,
        record: ImportedContentRecord,
    ) -> bool:
        category = (
            record.category_path.lower()
        )

        title = (
            record.title.lower()
        )

        if self.category_contains:
            if not all(
                phrase.lower()
                in category
                for phrase
                in self.category_contains
            ):
                return False

        if self.title_contains:
            if not all(
                phrase.lower()
                in title
                for phrase
                in self.title_contains
            ):
                return False

        return bool(
            self.category_contains
            or self.title_contains
        )
