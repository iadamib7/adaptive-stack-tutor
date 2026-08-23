from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree as ET

from backend.app.content.ingestion.models import (
    ImportedContentRecord,
)


_QUESTION_BLOCK_PATTERN = re.compile(
    r"<!--\s*question:\s*(\d+)\s*-->\s*"
    r"(<question\b.*?</question>)",
    flags=(
        re.IGNORECASE
        | re.DOTALL
    ),
)


class StackContentImporter:
    """
    Import STACK questions from Moodle XML.

    Moodle's export stores source question IDs in comments,
    so the importer intentionally preserves those IDs rather
    than relying on the often-empty idnumber element.
    """

    def import_file(
        self,
        path: Path,
    ) -> list[ImportedContentRecord]:
        xml_text = path.read_text(
            encoding="utf-8-sig"
        )

        records: list[
            ImportedContentRecord
        ] = []

        current_category = ""

        for match in (
            _QUESTION_BLOCK_PATTERN.finditer(
                xml_text
            )
        ):
            external_id = (
                match.group(1)
            )

            block = (
                match.group(2)
            )

            question = ET.fromstring(
                block
            )

            question_type = (
                question.get(
                    "type",
                    "",
                )
                or ""
            ).strip()

            if question_type == "category":
                current_category = (
                    self._category_path(
                        question
                    )
                )

                continue

            if question_type != "stack":
                continue

            if external_id == "0":
                continue

            records.append(
                self._record_from_question(
                    question=question,
                    external_id=external_id,
                    category_path=current_category,
                    source_reference=str(
                        path
                    ),
                )
            )

        return records

    def _record_from_question(
        self,
        *,
        question: ET.Element,
        external_id: str,
        category_path: str,
        source_reference: str,
    ) -> ImportedContentRecord:
        title = (
            question.findtext(
                "name/text"
            )
            or external_id
        ).strip()

        question_text = (
            question.findtext(
                "questiontext/text"
            )
            or ""
        ).strip()

        worked_solution = (
            question.findtext(
                "generalfeedback/text"
            )
            or ""
        ).strip()

        question_note = (
            question.findtext(
                "questionnote/text"
            )
            or ""
        ).strip()

        return ImportedContentRecord(
            source_provider="stack",
            source_reference=source_reference,
            external_id=external_id,
            title=title,
            question_text=question_text,
            worked_solution=worked_solution,
            question_note=question_note,
            category_path=category_path,
            input_names=tuple(
                self._named_children(
                    question,
                    "input",
                )
            ),
            prt_names=tuple(
                self._named_children(
                    question,
                    "prt",
                )
            ),
            deployed_seeds=tuple(
                self._deployed_seeds(
                    question
                )
            ),
        )

    @staticmethod
    def _category_path(
        question: ET.Element,
    ) -> str:
        return (
            question.findtext(
                "category/text"
            )
            or ""
        ).strip()

    @staticmethod
    def _named_children(
        question: ET.Element,
        tag_name: str,
    ) -> list[str]:
        names: list[str] = []

        for element in question.findall(
            tag_name
        ):
            name = (
                element.findtext(
                    "name"
                )
                or ""
            ).strip()

            if (
                name
                and name not in names
            ):
                names.append(
                    name
                )

        return names

    @staticmethod
    def _deployed_seeds(
        question: ET.Element,
    ) -> list[int]:
        seeds: list[int] = []

        for element in question.findall(
            "deployedseed"
        ):
            text = (
                element.text
                or ""
            ).strip()

            if not text:
                continue

            try:
                seed = int(
                    text
                )
            except ValueError:
                continue

            if seed not in seeds:
                seeds.append(
                    seed
                )

        return seeds
