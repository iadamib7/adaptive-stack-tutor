from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET

from backend.app.learning.adaptive_engine.models import (
    AdaptiveQuestion,
)


@dataclass(frozen=True)
class ImportedAdaptiveQuestion:
    """
    One instructor-provided STACK question.

    stack_xml preserves the original question
    definition for later rendering and grading.
    """

    adaptive_question: AdaptiveQuestion
    stack_xml: str


class AdaptiveQuestionBank:
    """
    Generic instructor question bank.

    No curriculum, concept graph, or national
    standard is required.
    """

    def __init__(
        self,
        questions: list[
            ImportedAdaptiveQuestion
        ],
    ) -> None:
        self._questions: dict[
            str,
            ImportedAdaptiveQuestion,
        ] = {}

        for item in questions:
            question_id = (
                item.adaptive_question.question_id
            )

            if question_id in self._questions:
                raise ValueError(
                    "Duplicate question ID: "
                    f"{question_id}"
                )

            self._questions[
                question_id
            ] = item

    @property
    def count(self) -> int:
        return len(
            self._questions
        )

    def adaptive_questions(
        self,
    ) -> list[AdaptiveQuestion]:
        return [
            item.adaptive_question
            for item in self._questions.values()
        ]

    def require(
        self,
        question_id: str,
    ) -> ImportedAdaptiveQuestion:
        item = self._questions.get(
            question_id
        )

        if item is None:
            raise ValueError(
                "Unknown question: "
                f"{question_id}"
            )

        return item


class StackXmlQuestionBankImporter:
    """
    Import instructor-authored STACK questions
    from Moodle quiz XML.

    Category records and non-STACK questions
    are ignored.
    """

    def import_file(
        self,
        file_path: Path,
    ) -> AdaptiveQuestionBank:
        if not file_path.is_file():
            raise FileNotFoundError(
                "Question bank not found: "
                f"{file_path}"
            )

        root = ET.parse(
            file_path
        ).getroot()

        return self._import_root(
            root
        )

    def import_text(
        self,
        xml_text: str,
    ) -> AdaptiveQuestionBank:
        if not xml_text.strip():
            raise ValueError(
                "Question-bank XML "
                "must not be empty."
            )

        root = ET.fromstring(
            xml_text
        )

        return self._import_root(
            root
        )

    def _import_root(
        self,
        root: ET.Element,
    ) -> AdaptiveQuestionBank:
        if root.tag != "quiz":
            raise ValueError(
                "Expected Moodle quiz XML "
                "with a <quiz> root."
            )

        imported: list[
            ImportedAdaptiveQuestion
        ] = []

        for question in root.findall(
            "question"
        ):
            if question.attrib.get(
                "type"
            ) != "stack":
                continue

            imported.append(
                self._import_question(
                    question
                )
            )

        if not imported:
            raise ValueError(
                "No STACK questions found "
                "in uploaded question bank."
            )

        return AdaptiveQuestionBank(
            imported
        )

    def _import_question(
        self,
        question: ET.Element,
    ) -> ImportedAdaptiveQuestion:
        stack_xml = (
            self._wrap_question(
                question
            )
        )

        explicit_id = self._text_at(
            question,
            "idnumber",
        )

        question_id = (
            explicit_id
            if explicit_id
            else self._stable_id(
                stack_xml
            )
        )

        title = self._text_at(
            question,
            "name/text",
        )

        if not title:
            title = question_id

        adaptive_question = (
            AdaptiveQuestion(
                question_id=question_id,
                title=title,
                difficulty=0.0,
            )
        )

        return ImportedAdaptiveQuestion(
            adaptive_question=(
                adaptive_question
            ),
            stack_xml=stack_xml,
        )

    @staticmethod
    def _text_at(
        element: ET.Element,
        path: str,
    ) -> str:
        child = element.find(
            path
        )

        if (
            child is None
            or child.text is None
        ):
            return ""

        return child.text.strip()

    @staticmethod
    def _stable_id(
        xml_text: str,
    ) -> str:
        digest = sha256(
            xml_text.encode(
                "utf-8"
            )
        ).hexdigest()[:16]

        return (
            f"stack-{digest}"
        )

    @staticmethod
    def _wrap_question(
        question: ET.Element,
    ) -> str:
        quiz = ET.Element(
            "quiz"
        )

        copied_question = (
            ET.fromstring(
                ET.tostring(
                    question,
                    encoding="unicode",
                )
            )
        )

        quiz.append(
            copied_question
        )

        return ET.tostring(
            quiz,
            encoding="unicode",
        )
