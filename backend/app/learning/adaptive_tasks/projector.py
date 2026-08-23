from __future__ import annotations

from copy import deepcopy
from xml.etree import ElementTree as ET

from backend.app.learning.adaptive_tasks.models import (
    AdaptiveTask,
)


class AdaptiveTaskProjectionError(
    ValueError
):
    pass


def project_question_xml_for_task(
    *,
    question_xml: str,
    task: AdaptiveTask,
) -> str:
    """
    Create a standalone STACK question containing only
    the inputs and PRTs required by one adaptive task.

    Question variables and other STACK configuration are
    preserved so the projected task uses the exact same
    generated mathematics as its source question.
    """

    try:
        root = ET.fromstring(
            question_xml
        )
    except ET.ParseError as error:
        raise AdaptiveTaskProjectionError(
            "Question XML is invalid."
        ) from error

    projected_root = deepcopy(
        root
    )

    question = _find_question(
        projected_root
    )

    _replace_question_text(
        question=question,
        prompt_template=(
            task.prompt_template
        ),
    )

    _keep_named_children(
        question=question,
        tag_name="input",
        allowed_names=set(
            task.input_names
        ),
    )

    _keep_named_children(
        question=question,
        tag_name="prt",
        allowed_names=set(
            task.prt_names
        ),
    )

    _remove_qtests(
        question
    )

    remaining_inputs = (
        _named_children(
            question,
            "input",
        )
    )

    remaining_prts = (
        _named_children(
            question,
            "prt",
        )
    )

    if set(remaining_inputs) != set(
        task.input_names
    ):
        raise AdaptiveTaskProjectionError(
            f"Projected task {task.task_id} "
            "does not contain exactly the required "
            "STACK inputs."
        )

    if set(remaining_prts) != set(
        task.prt_names
    ):
        raise AdaptiveTaskProjectionError(
            f"Projected task {task.task_id} "
            "does not contain exactly the required "
            "STACK PRTs."
        )

    return ET.tostring(
        projected_root,
        encoding="unicode",
    )


def _find_question(
    root: ET.Element,
) -> ET.Element:
    if root.tag == "question":
        return root

    question = root.find(
        ".//question"
    )

    if question is None:
        raise AdaptiveTaskProjectionError(
            "Question XML contains no question node."
        )

    return question


def _replace_question_text(
    *,
    question: ET.Element,
    prompt_template: str,
) -> None:
    text_node = question.find(
        "questiontext/text"
    )

    if text_node is None:
        raise AdaptiveTaskProjectionError(
            "STACK question contains no question text."
        )

    text_node.text = (
        prompt_template
    )


def _keep_named_children(
    *,
    question: ET.Element,
    tag_name: str,
    allowed_names: set[str],
) -> None:
    for parent in question.iter():
        for child in list(
            parent
        ):
            if child.tag != tag_name:
                continue

            name = (
                child.findtext("name")
                or ""
            ).strip()

            if name not in allowed_names:
                parent.remove(
                    child
                )


def _remove_qtests(
    question: ET.Element,
) -> None:
    for parent in question.iter():
        for child in list(
            parent
        ):
            if child.tag == "qtest":
                parent.remove(
                    child
                )


def _named_children(
    question: ET.Element,
    tag_name: str,
) -> list[str]:
    names: list[str] = []

    for element in question.findall(
        f".//{tag_name}"
    ):
        name = (
            element.findtext("name")
            or ""
        ).strip()

        if name:
            names.append(
                name
            )

    return names
