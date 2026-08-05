import re
from pathlib import Path
from xml.etree import ElementTree

from backend.app.integrations.stack_xml.export_models import (
    StackPRTOutcome,
    StackQuestionInventory,
    StackQuestionInventoryItem,
)


QUESTION_COMMENT_PATTERN = re.compile(
    r"question:\s*(\d+)",
    flags=re.IGNORECASE,
)


class StackExportParser:
    """
    Parse a Moodle XML export containing categories and multiple
    STACK questions.

    Category entries are interpreted in document order. Each STACK
    question is associated with the most recently declared category.
    """

    def parse(
        self,
        path: Path,
        profile_id: str,
    ) -> StackQuestionInventory:
        if not path.is_file():
            raise FileNotFoundError(
                f"STACK export was not found: {path}"
            )

        xml_parser = ElementTree.XMLParser(
            target=ElementTree.TreeBuilder(
                insert_comments=True,
            )
        )

        try:
            root = ElementTree.parse(
                path,
                parser=xml_parser,
            ).getroot()
        except ElementTree.ParseError as error:
            raise ValueError(
                f"Invalid STACK export XML: {path}"
            ) from error

        current_category: list[str] = []
        pending_question_id: str | None = None
        questions: list[StackQuestionInventoryItem] = []

        for element in list(root):
            if element.tag is ElementTree.Comment:
                pending_question_id = (
                    self._read_question_id_from_comment(
                        element.text
                    )
                )
                continue

            if element.tag != "question":
                continue

            question_type = element.attrib.get(
                "type",
                "",
            ).casefold()

            if question_type == "category":
                current_category = self._read_category_path(
                    element
                )
                pending_question_id = None
                continue

            if question_type != "stack":
                pending_question_id = None
                continue

            questions.append(
                self._parse_stack_question(
                    element=element,
                    source_file=path.name,
                    source_question_id=pending_question_id,
                    category_path=current_category,
                )
            )

            pending_question_id = None

        return StackQuestionInventory(
            profile_id=profile_id,
            source_file=path.name,
            question_count=len(questions),
            questions=questions,
        )

    def _parse_stack_question(
        self,
        element: ElementTree.Element,
        source_file: str,
        source_question_id: str | None,
        category_path: list[str],
    ) -> StackQuestionInventoryItem:
        question_name = (
            self._read_text(element, "./name/text")
            or "Unnamed STACK question"
        )

        input_names = [
            name
            for input_element in element.findall("./input")
            if (
                name := self._read_text(
                    input_element,
                    "./name",
                )
            )
        ]

        prt_names: list[str] = []
        outcomes: list[StackPRTOutcome] = []
        node_count = 0

        for prt_element in element.findall("./prt"):
            prt_name = (
                self._read_text(prt_element, "./name")
                or "unnamed_prt"
            )

            prt_names.append(prt_name)

            for node_element in prt_element.findall("./node"):
                node_count += 1

                node_name = (
                    self._read_text(
                        node_element,
                        "./name",
                    )
                    or str(node_count - 1)
                )

                answer_test = self._read_text(
                    node_element,
                    "./answertest",
                )

                description = self._read_text(
                    node_element,
                    "./description",
                )

                outcomes.extend(
                    [
                        self._parse_branch(
                            node_element=node_element,
                            prt_name=prt_name,
                            node_name=node_name,
                            branch="T",
                            answer_test=answer_test,
                            description=description,
                        ),
                        self._parse_branch(
                            node_element=node_element,
                            prt_name=prt_name,
                            node_name=node_name,
                            branch="F",
                            answer_test=answer_test,
                            description=description,
                        ),
                    ]
                )

        return StackQuestionInventoryItem(
            source_file=source_file,
            source_question_id=source_question_id,
            question_name=question_name,
            category_path=category_path.copy(),
            input_names=input_names,
            prt_names=prt_names,
            prt_count=len(prt_names),
            node_count=node_count,
            outcomes=outcomes,
            simple_single_prt=(
                len(prt_names) == 1
                and node_count == 1
                and len(input_names) == 1
            ),
        )

    def _parse_branch(
        self,
        node_element: ElementTree.Element,
        prt_name: str,
        node_name: str,
        branch: str,
        answer_test: str | None,
        description: str | None,
    ) -> StackPRTOutcome:
        prefix = "true" if branch == "T" else "false"

        answer_note = self._read_text(
            node_element,
            f"./{prefix}answernote",
        )

        outcome_code = (
            answer_note
            or f"{prt_name}-{node_name}-{branch}"
        )

        next_node_text = self._read_text(
            node_element,
            f"./{prefix}nextnode",
        )

        next_node = self._normalize_next_node(
            next_node_text
        )

        score = self._read_float(
            node_element,
            f"./{prefix}score",
        )

        feedback = self._read_text(
            node_element,
            f"./{prefix}feedback/text",
        )

        return StackPRTOutcome(
            prt_name=prt_name,
            node_name=node_name,
            branch=branch,
            outcome_code=outcome_code,
            answer_test=answer_test,
            description=description,
            score=score,
            next_node=next_node,
            feedback=feedback,
        )

    @staticmethod
    def _read_question_id_from_comment(
        comment: str | None,
    ) -> str | None:
        if not comment:
            return None

        match = QUESTION_COMMENT_PATTERN.search(comment)

        if match is None:
            return None

        question_id = match.group(1)

        if question_id == "0":
            return None

        return question_id

    def _read_category_path(
        self,
        element: ElementTree.Element,
    ) -> list[str]:
        raw_path = self._read_text(
            element,
            "./category/text",
        )

        if not raw_path:
            return []

        normalized = raw_path.replace(
            "$course$/top/",
            "",
        )

        return [
            section.strip()
            for section in normalized.split("/")
            if section.strip()
        ]

    @staticmethod
    def _normalize_next_node(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned = value.strip()

        if cleaned in {"", "-1"}:
            return None

        return cleaned

    @staticmethod
    def _read_float(
        element: ElementTree.Element,
        path: str,
    ) -> float | None:
        value = StackExportParser._read_text(
            element,
            path,
        )

        if value is None:
            return None

        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _read_text(
        element: ElementTree.Element,
        path: str,
    ) -> str | None:
        child = element.find(path)

        if child is None or child.text is None:
            return None

        value = child.text.strip()

        return value or None
