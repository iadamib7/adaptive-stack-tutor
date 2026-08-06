from copy import deepcopy
from pathlib import Path
import re
from xml.etree import ElementTree as ET


class StackQuestionNotFoundError(ValueError):
    pass


QUESTION_COMMENT_PATTERN = re.compile(
    r"question\s*:\s*(\S+)",
    re.IGNORECASE,
)


def extract_stack_question(
    export_path: Path,
    question_id: str,
) -> str:
    """
    Extract one STACK question from a Moodle XML export.

    Moodle exports may store the source question ID in a
    comment immediately before the question:

        <!-- question: 207582 -->
        <question type="stack">...</question>

    The returned question is wrapped in a <quiz> root so it
    can be submitted directly to the standalone STACK API.
    """

    if not export_path.is_file():
        raise FileNotFoundError(
            f"STACK export was not found: {export_path}"
        )

    parser = ET.XMLParser(
        target=ET.TreeBuilder(
            insert_comments=True,
        )
    )

    tree = ET.parse(
        export_path,
        parser=parser,
    )

    root = tree.getroot()
    pending_question_id: str | None = None

    for child in root:
        if child.tag is ET.Comment:
            pending_question_id = (
                _read_question_id_from_comment(
                    child.text
                )
            )
            continue

        if child.tag != "question":
            continue

        if child.get("type") != "stack":
            pending_question_id = None
            continue

        if (
            pending_question_id == question_id
            or _question_contains_id(
                question=child,
                question_id=question_id,
            )
        ):
            quiz = ET.Element("quiz")
            quiz.append(deepcopy(child))

            return ET.tostring(
                quiz,
                encoding="unicode",
            )

        pending_question_id = None

    raise StackQuestionNotFoundError(
        f"STACK question {question_id} was not found "
        f"in {export_path}."
    )


def write_stack_question(
    export_path: Path,
    question_id: str,
    output_path: Path,
) -> Path:
    question_xml = extract_stack_question(
        export_path=export_path,
        question_id=question_id,
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        question_xml,
        encoding="utf-8",
    )

    return output_path


def _read_question_id_from_comment(
    comment_text: str | None,
) -> str | None:
    if not comment_text:
        return None

    match = QUESTION_COMMENT_PATTERN.search(
        comment_text
    )

    if match is None:
        return None

    return match.group(1).strip()


def _question_contains_id(
    question: ET.Element,
    question_id: str,
) -> bool:
    """
    Fallback for exports that store the identifier in an
    element such as <idnumber>.
    """

    expected = question_id.strip()

    for element in question.iter():
        if element.text is None:
            continue

        if element.text.strip() == expected:
            return True

    return False
