from __future__ import annotations

from pathlib import Path

from backend.app.content.ingestion.numbas.catalog import (
    NumbasCatalogEntry,
)
from backend.app.content.ingestion.numbas.models import (
    NumbasQuestionMetadata,
)
from backend.app.content.ingestion.numbas.parser import (
    NumbasExamParser,
)


class NumbasMetadataBuilder:
    def __init__(self) -> None:
        self.parser = NumbasExamParser()

    def build(
        self,
        *,
        path: Path,
        catalog_entry: NumbasCatalogEntry,
    ) -> NumbasQuestionMetadata:
        question = self.parser.parse(
            path
        )

        license_code, license_url = (
            self._normalize_license(
                question.licence
            )
        )

        return NumbasQuestionMetadata(
            question_id=(
                catalog_entry.question_id
            ),
            title=question.name,
            source_url=(
                catalog_entry.source_url
            ),
            project_name=(
                catalog_entry.project_name
            ),
            description=(
                question.description
            ),
            status=(
                catalog_entry.status
            ),
            license_code=license_code,
            license_url=license_url,
            tags=question.tags,
            author_names=(
                question.contributors
            ),
        )

    @staticmethod
    def _normalize_license(
        licence: str,
    ) -> tuple[str, str]:
        normalized = (
            licence.strip().lower()
        )

        if (
            "creative commons attribution "
            "4.0 international"
            in normalized
        ):
            return (
                "CC-BY-4.0",
                (
                    "https://creativecommons.org/"
                    "licenses/by/4.0/"
                ),
            )

        if (
            "cc by 4.0"
            in normalized
            or "cc-by-4.0"
            in normalized
        ):
            return (
                "CC-BY-4.0",
                (
                    "https://creativecommons.org/"
                    "licenses/by/4.0/"
                ),
            )

        return (
            "",
            "",
        )
