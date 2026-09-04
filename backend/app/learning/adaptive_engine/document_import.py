from __future__ import annotations

from dataclasses import dataclass
import csv
from html import escape
from io import BytesIO, StringIO
from zipfile import BadZipFile, ZipFile
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

from openpyxl import load_workbook
from pypdf import PdfReader


@dataclass(frozen=True)
class ImportedDocumentQuestion:
    question_id: str
    question: str
    answer: str

    difficulty: float = 0.0

    tags: tuple[str, ...] = ()
    supports: tuple[str, ...] = ()
    diagnoses: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConvertedDocumentBank:
    question_bank_xml: str
    metadata_json: str
    question_count: int


class AdaptiveDocumentImporter:
    """
    Convert structured instructor documents into
    a generic STACK/Moodle question bank.

    Supported source formats:
    - .xlsx
    - .docx
    - .pdf

    This importer does not infer curriculum
    information or fabricate diagnostic PRTs.
    """

    def import_bytes(
        self,
        *,
        filename: str,
        content: bytes,
    ) -> ConvertedDocumentBank:
        suffix = Path(
            filename
        ).suffix.lower()

        if suffix in {
            ".xlsx",
            ".xlsm",
        }:
            questions = (
                self._read_excel(
                    content
                )
            )

        elif suffix == ".csv":
            questions = (
                self._read_csv(
                    content
                )
            )

        elif suffix == ".docx":
            questions = (
                self._read_word(
                    content
                )
            )

        elif suffix == ".pdf":
            questions = (
                self._read_pdf(
                    content
                )
            )

        else:
            raise ValueError(
                "Unsupported question-bank "
                f"format: {suffix}"
            )

        if not questions:
            raise ValueError(
                "No structured questions "
                "were found in the document."
            )

        return ConvertedDocumentBank(
            question_bank_xml=(
                self._build_stack_xml(
                    questions
                )
            ),
            metadata_json=(
                self._build_metadata_json(
                    questions
                )
            ),
            question_count=len(
                questions
            ),
        )

    def _read_excel(
        self,
        content: bytes,
    ) -> list[
        ImportedDocumentQuestion
    ]:
        workbook = load_workbook(
            BytesIO(content),
            data_only=True,
        )

        sheet = workbook.active

        rows = list(
            sheet.iter_rows(
                values_only=True
            )
        )

        if not rows:
            return []

        headers = [
            str(value).strip().lower()
            if value is not None
            else ""
            for value
            in rows[0]
        ]

        required = {
            "question_id",
            "question",
            "answer",
        }

        missing = (
            required
            - set(headers)
        )

        if missing:
            raise ValueError(
                "Excel question bank is "
                "missing required columns: "
                + ", ".join(
                    sorted(missing)
                )
            )

        index = {
            name: position
            for position, name
            in enumerate(headers)
            if name
        }

        questions: list[
            ImportedDocumentQuestion
        ] = []

        for row in rows[1:]:
            question_id = (
                self._cell(
                    row,
                    index.get(
                        "question_id"
                    ),
                )
            )

            question = self._cell(
                row,
                index.get(
                    "question"
                ),
            )

            answer = self._cell(
                row,
                index.get(
                    "answer"
                ),
            )

            if not (
                question_id
                or question
                or answer
            ):
                continue

            if not (
                question_id
                and question
                and answer
            ):
                raise ValueError(
                    "Each Excel question "
                    "must include question_id, "
                    "question, and answer."
                )

            difficulty_text = (
                self._cell(
                    row,
                    index.get(
                        "difficulty"
                    ),
                )
            )

            difficulty = (
                float(
                    difficulty_text
                )
                if difficulty_text
                else 0.0
            )

            questions.append(
                ImportedDocumentQuestion(
                    question_id=(
                        question_id
                    ),
                    question=question,
                    answer=answer,
                    difficulty=(
                        difficulty
                    ),
                    tags=self._csv_tuple(
                        self._cell(
                            row,
                            index.get(
                                "tags"
                            ),
                        )
                    ),
                    supports=(
                        self._csv_tuple(
                            self._cell(
                                row,
                                index.get(
                                    "supports"
                                ),
                            )
                        )
                    ),
                    diagnoses=(
                        self._csv_tuple(
                            self._cell(
                                row,
                                index.get(
                                    "diagnoses"
                                ),
                            )
                        )
                    ),
                )
            )

        return questions

    def _read_csv(
        self,
        content: bytes,
    ) -> list[
        ImportedDocumentQuestion
    ]:
        try:
            text = content.decode(
                "utf-8-sig"
            )
        except UnicodeDecodeError as error:
            raise ValueError(
                "CSV question bank must "
                "be UTF-8 encoded."
            ) from error

        reader = csv.DictReader(
            StringIO(text)
        )

        if reader.fieldnames is None:
            return []

        field_map = {
            name.strip().lower():
                name
            for name
            in reader.fieldnames
            if name is not None
        }

        required = {
            "question_id",
            "question",
            "answer",
        }

        missing = (
            required
            - set(field_map)
        )

        if missing:
            raise ValueError(
                "CSV question bank is "
                "missing required columns: "
                + ", ".join(
                    sorted(missing)
                )
            )

        questions: list[
            ImportedDocumentQuestion
        ] = []

        for row in reader:
            question_id = (
                row.get(
                    field_map[
                        "question_id"
                    ],
                    "",
                )
                or ""
            ).strip()

            question = (
                row.get(
                    field_map[
                        "question"
                    ],
                    "",
                )
                or ""
            ).strip()

            answer = (
                row.get(
                    field_map[
                        "answer"
                    ],
                    "",
                )
                or ""
            ).strip()

            if not (
                question_id
                or question
                or answer
            ):
                continue

            if not (
                question_id
                and question
                and answer
            ):
                raise ValueError(
                    "Each CSV question "
                    "must include question_id, "
                    "question, and answer."
                )

            difficulty_text = ""

            if "difficulty" in field_map:
                difficulty_text = (
                    row.get(
                        field_map[
                            "difficulty"
                        ],
                        "",
                    )
                    or ""
                ).strip()

            difficulty = (
                float(
                    difficulty_text
                )
                if difficulty_text
                else 0.0
            )

            def optional_field(
                name: str,
            ) -> str:
                if name not in field_map:
                    return ""

                return (
                    row.get(
                        field_map[
                            name
                        ],
                        "",
                    )
                    or ""
                ).strip()

            questions.append(
                ImportedDocumentQuestion(
                    question_id=question_id,
                    question=question,
                    answer=answer,
                    difficulty=difficulty,
                    tags=self._csv_tuple(
                        optional_field(
                            "tags"
                        )
                    ),
                    supports=self._csv_tuple(
                        optional_field(
                            "supports"
                        )
                    ),
                    diagnoses=self._csv_tuple(
                        optional_field(
                            "diagnoses"
                        )
                    ),
                )
            )

        return questions

    def _read_word(
        self,
        content: bytes,
    ) -> list[
        ImportedDocumentQuestion
    ]:
        """
        Read text from a .docx package using only
        Python's standard ZIP and XML libraries.

        A DOCX file is a ZIP archive whose main
        document text is stored in:

            word/document.xml
        """

        try:
            with ZipFile(
                BytesIO(content)
            ) as archive:
                try:
                    document_xml = (
                        archive.read(
                            "word/document.xml"
                        )
                    )
                except KeyError as error:
                    raise ValueError(
                        "Word document does not "
                        "contain word/document.xml."
                    ) from error

        except BadZipFile as error:
            raise ValueError(
                "Uploaded Word file is not "
                "a valid .docx document."
            ) from error

        try:
            root = ET.fromstring(
                document_xml
            )
        except ET.ParseError as error:
            raise ValueError(
                "Word document contains "
                "invalid XML."
            ) from error

        namespace = {
            "w": (
                "http://schemas.openxmlformats.org/"
                "wordprocessingml/2006/main"
            )
        }

        paragraphs: list[str] = []

        for paragraph in root.findall(
            ".//w:p",
            namespace,
        ):
            pieces = [
                node.text
                for node
                in paragraph.findall(
                    ".//w:t",
                    namespace,
                )
                if node.text
            ]

            line = "".join(
                pieces
            ).strip()

            if line:
                paragraphs.append(
                    line
                )

        return self._parse_text_bank(
            "\n".join(
                paragraphs
            )
        )

    def _read_pdf(
        self,
        content: bytes,
    ) -> list[
        ImportedDocumentQuestion
    ]:
        reader = PdfReader(
            BytesIO(content)
        )

        pages: list[str] = []

        for page in reader.pages:
            text = (
                page.extract_text()
                or ""
            )

            pages.append(
                text
            )

        return self._parse_text_bank(
            "\n".join(
                pages
            )
        )

    def _parse_text_bank(
        self,
        text: str,
    ) -> list[
        ImportedDocumentQuestion
    ]:
        records: list[
            dict[str, str]
        ] = []

        current: dict[
            str,
            str,
        ] = {}

        supported_fields = {
            "question id":
                "question_id",
            "question":
                "question",
            "answer":
                "answer",
            "difficulty":
                "difficulty",
            "tags":
                "tags",
            "supports":
                "supports",
            "diagnoses":
                "diagnoses",
        }

        for raw_line in text.splitlines():
            line = raw_line.strip()

            if not line:
                if current:
                    records.append(
                        current
                    )

                    current = {}

                continue

            if ":" not in line:
                continue

            key, value = line.split(
                ":",
                1,
            )

            normalized_key = (
                key.strip().lower()
            )

            field = supported_fields.get(
                normalized_key
            )

            if field is None:
                continue

            if (
                field == "question_id"
                and current.get(
                    "question_id"
                )
            ):
                records.append(
                    current
                )

                current = {}

            current[
                field
            ] = value.strip()

        if current:
            records.append(
                current
            )

        questions: list[
            ImportedDocumentQuestion
        ] = []

        for record in records:
            question_id = (
                record.get(
                    "question_id",
                    "",
                ).strip()
            )

            question = (
                record.get(
                    "question",
                    "",
                ).strip()
            )

            answer = (
                record.get(
                    "answer",
                    "",
                ).strip()
            )

            if not (
                question_id
                and question
                and answer
            ):
                continue

            difficulty_text = (
                record.get(
                    "difficulty",
                    "",
                ).strip()
            )

            difficulty = (
                float(
                    difficulty_text
                )
                if difficulty_text
                else 0.0
            )

            questions.append(
                ImportedDocumentQuestion(
                    question_id=(
                        question_id
                    ),
                    question=question,
                    answer=answer,
                    difficulty=(
                        difficulty
                    ),
                    tags=self._csv_tuple(
                        record.get(
                            "tags",
                            "",
                        )
                    ),
                    supports=(
                        self._csv_tuple(
                            record.get(
                                "supports",
                                "",
                            )
                        )
                    ),
                    diagnoses=(
                        self._csv_tuple(
                            record.get(
                                "diagnoses",
                                "",
                            )
                        )
                    ),
                )
            )

        return questions

    def _build_stack_xml(
        self,
        questions: Iterable[
            ImportedDocumentQuestion
        ],
    ) -> str:
        quiz = ET.Element(
            "quiz"
        )

        for question in questions:
            quiz.append(
                self._stack_question(
                    question
                )
            )

        return ET.tostring(
            quiz,
            encoding="unicode",
        )

    def _stack_question(
        self,
        question:
            ImportedDocumentQuestion,
    ) -> ET.Element:
        node = ET.Element(
            "question",
            {
                "type": "stack"
            },
        )

        self._text_element(
            node,
            "name",
            question.question,
            nested=True,
        )

        question_text = (
            ET.SubElement(
                node,
                "questiontext",
                {
                    "format": "html"
                },
            )
        )

        text_node = ET.SubElement(
            question_text,
            "text",
        )

        text_node.text = (
            "<p>"
            + escape(
                question.question
            )
            + "</p>"
            + "<p>"
            + "[[input:ans1]] "
            + "[[validation:ans1]]"
            + "</p>"
        )

        self._text_element(
            node,
            "generalfeedback",
            "",
            nested=True,
        )

        ET.SubElement(
            node,
            "defaultgrade",
        ).text = "1"

        ET.SubElement(
            node,
            "penalty",
        ).text = "0.1"

        ET.SubElement(
            node,
            "hidden",
        ).text = "0"

        ET.SubElement(
            node,
            "idnumber",
        ).text = question.question_id

        stack_version = (
            ET.SubElement(
                node,
                "stackversion",
            )
        )

        ET.SubElement(
            stack_version,
            "text",
        ).text = "2024092500"

        variables = (
            ET.SubElement(
                node,
                "questionvariables",
            )
        )

        variables_text = (
            ET.SubElement(
                variables,
                "text",
            )
        )

        safe_answer = (
            question.answer
            .replace(
                "\\",
                "\\\\",
            )
            .replace(
                '"',
                '\\"',
            )
        )

        variables_text.text = (
            'ta:"'
            + safe_answer
            + '";'
        )

        specific = ET.SubElement(
            node,
            "specificfeedback",
            {
                "format": "html"
            },
        )

        ET.SubElement(
            specific,
            "text",
        ).text = "[[feedback:prt1]]"

        self._text_element(
            node,
            "questionnote",
            "",
            nested=True,
        )

        self._text_element(
            node,
            "questiondescription",
            "Imported instructor question",
            nested=True,
        )

        ET.SubElement(
            node,
            "questionsimplify",
        ).text = "1"

        ET.SubElement(
            node,
            "assumepositive",
        ).text = "0"

        ET.SubElement(
            node,
            "assumereal",
        ).text = "0"

        input_node = ET.SubElement(
            node,
            "input",
        )

        ET.SubElement(
            input_node,
            "name",
        ).text = "ans1"

        ET.SubElement(
            input_node,
            "type",
        ).text = "string"

        ET.SubElement(
            input_node,
            "tans",
        ).text = "ta"

        ET.SubElement(
            input_node,
            "boxsize",
        ).text = "30"

        ET.SubElement(
            input_node,
            "strictsyntax",
        ).text = "1"

        ET.SubElement(
            input_node,
            "insertstars",
        ).text = "0"

        ET.SubElement(
            input_node,
            "syntaxhint",
        ).text = ""

        ET.SubElement(
            input_node,
            "syntaxattribute",
        ).text = "0"

        ET.SubElement(
            input_node,
            "forbidwords",
        ).text = ""

        ET.SubElement(
            input_node,
            "allowwords",
        ).text = ""

        ET.SubElement(
            input_node,
            "forbidfloat",
        ).text = "0"

        ET.SubElement(
            input_node,
            "requirelowestterms",
        ).text = "0"

        ET.SubElement(
            input_node,
            "checkanswertype",
        ).text = "0"

        ET.SubElement(
            input_node,
            "mustverify",
        ).text = "0"

        ET.SubElement(
            input_node,
            "showvalidation",
        ).text = "0"

        ET.SubElement(
            input_node,
            "options",
        ).text = ""

        prt = ET.SubElement(
            node,
            "prt",
        )

        ET.SubElement(
            prt,
            "name",
        ).text = "prt1"

        ET.SubElement(
            prt,
            "value",
        ).text = "1.0000000"

        ET.SubElement(
            prt,
            "autosimplify",
        ).text = "1"

        ET.SubElement(
            prt,
            "feedbackstyle",
        ).text = "1"

        feedback_variables = (
            ET.SubElement(
                prt,
                "feedbackvariables",
            )
        )

        ET.SubElement(
            feedback_variables,
            "text",
        ).text = ""

        prt_node = ET.SubElement(
            prt,
            "node",
        )

        ET.SubElement(
            prt_node,
            "name",
        ).text = "0"

        ET.SubElement(
            prt_node,
            "description",
        ).text = (
            "Checks imported "
            "instructor answer."
        )

        ET.SubElement(
            prt_node,
            "answertest",
        ).text = "AlgEquiv"

        ET.SubElement(
            prt_node,
            "sans",
        ).text = "ans1"

        ET.SubElement(
            prt_node,
            "tans",
        ).text = "ta"

        ET.SubElement(
            prt_node,
            "testoptions",
        ).text = ""

        ET.SubElement(
            prt_node,
            "quiet",
        ).text = "0"

        ET.SubElement(
            prt_node,
            "truescoremode",
        ).text = "="

        ET.SubElement(
            prt_node,
            "truescore",
        ).text = "1"

        ET.SubElement(
            prt_node,
            "truepenalty",
        ).text = ""

        ET.SubElement(
            prt_node,
            "truenextnode",
        ).text = "-1"

        ET.SubElement(
            prt_node,
            "trueanswernote",
        ).text = "prt1-1-T"

        true_feedback = (
            ET.SubElement(
                prt_node,
                "truefeedback",
                {
                    "format": "html"
                },
            )
        )

        ET.SubElement(
            true_feedback,
            "text",
        ).text = "Correct."

        ET.SubElement(
            prt_node,
            "falsescoremode",
        ).text = "="

        ET.SubElement(
            prt_node,
            "falsescore",
        ).text = "0"

        ET.SubElement(
            prt_node,
            "falsepenalty",
        ).text = ""

        ET.SubElement(
            prt_node,
            "falsenextnode",
        ).text = "-1"

        ET.SubElement(
            prt_node,
            "falseanswernote",
        ).text = "prt1-1-F"

        false_feedback = (
            ET.SubElement(
                prt_node,
                "falsefeedback",
                {
                    "format": "html"
                },
            )
        )

        ET.SubElement(
            false_feedback,
            "text",
        ).text = (
            "Review your answer "
            "and try again."
        )

        return node

    def _build_metadata_json(
        self,
        questions: Iterable[
            ImportedDocumentQuestion
        ],
    ) -> str:
        import json

        payload: dict[
            str,
            object,
        ] = {
            "questions": {}
        }

        question_map = payload[
            "questions"
        ]

        assert isinstance(
            question_map,
            dict,
        )

        for question in questions:
            metadata: dict[
                str,
                object,
            ] = {
                "difficulty":
                    question.difficulty,
            }

            if question.tags:
                metadata[
                    "tags"
                ] = list(
                    question.tags
                )

            if question.supports:
                metadata[
                    "supports"
                ] = list(
                    question.supports
                )

            if question.diagnoses:
                metadata[
                    "diagnoses"
                ] = list(
                    question.diagnoses
                )

            question_map[
                question.question_id
            ] = metadata

        return json.dumps(
            payload,
            indent=2,
        )

    @staticmethod
    def _text_element(
        parent: ET.Element,
        name: str,
        value: str,
        *,
        nested: bool = False,
    ) -> ET.Element:
        element = ET.SubElement(
            parent,
            name,
        )

        if nested:
            ET.SubElement(
                element,
                "text",
            ).text = value
        else:
            element.text = value

        return element

    @staticmethod
    def _cell(
        row: tuple[
            object,
            ...,
        ],
        index: int | None,
    ) -> str:
        if index is None:
            return ""

        if index >= len(row):
            return ""

        value = row[
            index
        ]

        if value is None:
            return ""

        return str(
            value
        ).strip()

    @staticmethod
    def _csv_tuple(
        value: str,
    ) -> tuple[str, ...]:
        return tuple(
            item.strip()
            for item
            in value.split(",")
            if item.strip()
        )
