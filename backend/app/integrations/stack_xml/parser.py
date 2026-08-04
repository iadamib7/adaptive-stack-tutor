from pathlib import Path
from xml.etree import ElementTree

from backend.app.integrations.stack_xml.models import (
    PRTBranch,
    PRTNode,
    PRTStructure,
    StackQuestionStructure,
)


class StackXMLParser:
    """
    Parse structural information from an exported STACK question.

    This parser intentionally extracts only the information needed by
    the sequencing framework:

    - question name;
    - PRT names;
    - PRT node numbers;
    - true and false next-node references.

    It does not attempt to grade responses or reproduce STACK itself.
    """

    def parse_file(
        self,
        path: Path,
    ) -> StackQuestionStructure:
        if not path.is_file():
            raise FileNotFoundError(
                f"STACK XML file was not found: {path}"
            )

        try:
            root = ElementTree.parse(path).getroot()
        except ElementTree.ParseError as error:
            raise ValueError(
                f"Invalid XML in STACK question file: {path}"
            ) from error

        question_element = self._find_stack_question(root)

        question_name = self._read_text(
            question_element,
            "./name/text",
        )

        if not question_name:
            question_name = path.stem

        prts = self._parse_prts(question_element)

        return StackQuestionStructure(
            filename=path.name,
            question_name=question_name,
            prts=prts,
        )

    def parse_directory(
        self,
        directory: Path,
    ) -> list[StackQuestionStructure]:
        if not directory.is_dir():
            raise NotADirectoryError(
                f"STACK question directory was not found: "
                f"{directory}"
            )

        return [
            self.parse_file(path)
            for path in sorted(directory.glob("*.xml"))
        ]

    @staticmethod
    def _find_stack_question(
        root: ElementTree.Element,
    ) -> ElementTree.Element:
        if root.tag == "question":
            question_elements = [root]
        else:
            question_elements = root.findall(".//question")

        for question in question_elements:
            question_type = question.attrib.get(
                "type",
                "",
            ).casefold()

            if question_type == "stack":
                return question

        if len(question_elements) == 1:
            return question_elements[0]

        raise ValueError(
            "No STACK question element was found in the XML."
        )

    def _parse_prts(
        self,
        question: ElementTree.Element,
    ) -> list[PRTStructure]:
        prt_elements = question.findall(".//prt")

        return [
            self._parse_prt(prt_element)
            for prt_element in prt_elements
        ]

    def _parse_prt(
        self,
        prt_element: ElementTree.Element,
    ) -> PRTStructure:
        name = (
            prt_element.attrib.get("name")
            or self._read_text(prt_element, "./name")
            or self._read_text(prt_element, "./name/text")
        )

        if not name:
            raise ValueError(
                "A PRT element is missing its name."
            )

        node_elements = prt_element.findall("./node")

        if not node_elements:
            node_elements = prt_element.findall(
                "./nodes/node"
            )

        nodes = [
            self._parse_node(node_element)
            for node_element in node_elements
        ]

        return PRTStructure(
            name=name,
            nodes=nodes,
        )

    def _parse_node(
        self,
        node_element: ElementTree.Element,
    ) -> PRTNode:
        number_text = (
            node_element.attrib.get("number")
            or self._read_text(node_element, "./number")
        )

        if not number_text:
            raise ValueError(
                "A PRT node is missing its number."
            )

        try:
            number = int(number_text)
        except ValueError as error:
            raise ValueError(
                f"Invalid PRT node number: {number_text}"
            ) from error

        true_next = self._read_next_node(
            node_element=node_element,
            branch_name="true",
        )

        false_next = self._read_next_node(
            node_element=node_element,
            branch_name="false",
        )

        return PRTNode(
            number=number,
            true_branch=PRTBranch(
                branch="T",
                next_node=true_next,
            ),
            false_branch=PRTBranch(
                branch="F",
                next_node=false_next,
            ),
        )

    def _read_next_node(
        self,
        node_element: ElementTree.Element,
        branch_name: str,
    ) -> int | None:
        possible_paths = [
            f"./{branch_name}/next",
            f"./{branch_name}/nextnode",
            f"./{branch_name}/nextnode/text",
            f"./{branch_name}next",
            f"./{branch_name}next/text",
        ]

        value: str | None = None

        for path in possible_paths:
            value = self._read_text(
                node_element,
                path,
            )

            if value is not None:
                break

        if value is None:
            return None

        cleaned = value.strip()

        if cleaned in {"", "0", "-1"}:
            return None

        try:
            return int(cleaned)
        except ValueError as error:
            raise ValueError(
                f"Invalid next-node value: {value}"
            ) from error

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
