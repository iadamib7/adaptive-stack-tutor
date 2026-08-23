from __future__ import annotations

import re
from pathlib import Path

from backend.app.content.ingestion.models import (
    ImportedContentRecord,
)
from backend.app.content.ingestion.numbas.parser import (
    NumbasExamParser,
)


class NumbasContentImporter:
    """
    Convert a local Numbas .exam source into the common
    ImportedContentRecord representation.
    """

    def __init__(self) -> None:
        self.parser = NumbasExamParser()

    def import_file(
        self,
        path: Path,
    ) -> ImportedContentRecord:
        question = self.parser.parse(
            path
        )

        external_id = (
            self._external_id_from_filename(
                path
            )
        )

        metadata = [
            (
                "licence",
                question.licence,
            ),
            (
                "contributors",
                ", ".join(
                    question.contributors
                ),
            ),
            (
                "part_count",
                str(
                    len(
                        question.parts
                    )
                ),
            ),
            (
                "variable_count",
                str(
                    len(
                        question.variables
                    )
                ),
            ),
        ]

        for tag in question.tags:
            metadata.append(
                (
                    "tag",
                    tag,
                )
            )

        return ImportedContentRecord(
            source_provider="numbas",
            source_reference=str(
                path
            ),
            external_id=external_id,
            title=question.name,
            question_text=(
                question.statement
            ),
            worked_solution=(
                question.advice
            ),
            question_note=(
                question.description
            ),
            category_path=(
                " / ".join(
                    question.tags
                )
            ),
            input_names=(
                self._synthetic_input_names(
                    question.parts
                )
            ),
            prt_names=(),
            deployed_seeds=(),
            metadata=tuple(
                metadata
            ),
        )

    @staticmethod
    def _external_id_from_filename(
        path: Path,
    ) -> str:
        match = re.search(
            r"question-(\d+)",
            path.name,
            flags=re.IGNORECASE,
        )

        if match is None:
            raise ValueError(
                "Could not determine Numbas "
                "question ID from filename."
            )

        return match.group(1)

    @staticmethod
    def _synthetic_input_names(
        parts: tuple[
            dict,
            ...
        ],
    ) -> tuple[str, ...]:
        names: list[str] = []

        for part_index, part in enumerate(
            parts,
            start=1,
        ):
            gaps = part.get(
                "gaps",
                [],
            )

            if gaps:
                for gap_index, _ in enumerate(
                    gaps,
                    start=1,
                ):
                    names.append(
                        "part"
                        f"{part_index}"
                        "_gap"
                        f"{gap_index}"
                    )
            else:
                names.append(
                    f"part{part_index}"
                )

        return tuple(
            names
        )
