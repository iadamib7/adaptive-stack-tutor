from __future__ import annotations

import re
from xml.etree import ElementTree as ET

from backend.app.learning.adaptive_tasks.models import (
    AdaptiveQuestionTasks,
    AdaptiveTask,
)


_INPUT_PATTERN = re.compile(
    r"\[\[input:([A-Za-z0-9_-]+)\]\]"
)

_PARAGRAPH_PATTERN = re.compile(
    r"<p\b[^>]*>.*?</p>",
    flags=(
        re.IGNORECASE
        | re.DOTALL
    ),
)

_PART_LABEL_PATTERN = re.compile(
    r"<p\b[^>]*>\s*"
    r"\(([A-Za-z0-9]+)\)",
    flags=re.IGNORECASE,
)


class AdaptiveTaskExtractionError(
    ValueError
):
    pass


def extract_adaptive_tasks(
    *,
    question_id: str,
    question_xml: str,
) -> AdaptiveQuestionTasks:
    """
    Convert one STACK source question into learner-facing
    adaptive tasks.

    Important rule:

        One task = one mathematical activity.

    Multiple answer inputs may remain together when they occur
    in the same mathematical prompt.

    Separate question paragraphs containing their own answer
    inputs become separate adaptive tasks.
    """

    question = _get_question_node(
        question_xml
    )

    question_template = (
        _get_question_template(
            question
        )
    )

    prt_by_input = (
        _map_inputs_to_prts(
            question
        )
    )

    blocks = _extract_prompt_blocks(
        question_template
    )

    introduction_blocks: list[str] = []
    task_blocks: list[str] = []

    first_task_seen = False

    for block in blocks:
        inputs = _input_names(
            block
        )

        if inputs:
            first_task_seen = True
            task_blocks.append(
                block
            )
            continue

        if not first_task_seen:
            introduction_blocks.append(
                block
            )

    if not task_blocks:
        inputs = _input_names(
            question_template
        )

        if not inputs:
            raise AdaptiveTaskExtractionError(
                f"Question {question_id} contains "
                "no STACK answer inputs."
            )

        task_blocks = [
            question_template
        ]

        introduction_blocks = []

    # Some interactive STACK questions store related hidden
    # answer inputs in separate paragraph blocks even though
    # they belong to one visible mathematical interaction.
    #
    # Two supported forms are:
    #
    # 1. Every task block is a hidden interactive input.
    #
    # 2. JSXGraph-bound hidden inputs are followed by one
    #    visible answer block which completes the same
    #    mathematical activity, for example constructing two
    #    graphs and then reporting their intersection.
    #
    # Keep this rule narrow so ordinary multipart STACK
    # questions remain separate adaptive tasks.
    hidden_input_blocks = (
        len(task_blocks) > 1
        and all(
            _is_hidden_input_block(block)
            for block in task_blocks
        )
    )

    jsxgraph_inputs = (
        _jsxgraph_bound_input_names(
            question_template
        )
    )

    task_inputs = [
        _input_names(block)
        for block in task_blocks
    ]

    hidden_indexes = [
        index
        for index, block in enumerate(
            task_blocks
        )
        if _is_hidden_input_block(
            block
        )
    ]

    visible_indexes = [
        index
        for index, block in enumerate(
            task_blocks
        )
        if not _is_hidden_input_block(
            block
        )
    ]

    hidden_inputs = {
        input_name
        for index in hidden_indexes
        for input_name in task_inputs[index]
    }

    no_explicit_parts = all(
        _part_label(block) is None
        for block in task_blocks
    )

    jsxgraph_with_visible_followup = (
        bool(jsxgraph_inputs)
        and bool(hidden_indexes)
        and len(visible_indexes) == 1
        and visible_indexes[0]
        > max(hidden_indexes)
        and set(jsxgraph_inputs)
        <= hidden_inputs
        and no_explicit_parts
    )

    if (
        hidden_input_blocks
        or jsxgraph_with_visible_followup
    ):
        # Preserve the complete interactive activity as one
        # adaptive task. Different subsets of the learner
        # inputs may legitimately be graded by different PRTs.
        task_blocks = [
            "\n".join(task_blocks)
        ]

    introduction = "\n".join(
        introduction_blocks
    ).strip()

    tasks: list[AdaptiveTask] = []

    for order, block in enumerate(
        task_blocks,
        start=1,
    ):
        inputs = _input_names(
            block
        )

        prts = _prt_names_for_inputs(
            inputs=inputs,
            prt_by_input=prt_by_input,
        )

        if not prts:
            raise AdaptiveTaskExtractionError(
                f"Question {question_id}, task {order} "
                "contains inputs but no matching PRTs."
            )

        prompt = block.strip()

        if introduction:
            prompt = (
                introduction
                + "\n"
                + prompt
            )

        part_label = (
            _part_label(
                block
            )
        )

        task_suffix = (
            part_label
            if part_label is not None
            else str(order)
        )

        tasks.append(
            AdaptiveTask(
                task_id=(
                    f"{question_id}::"
                    f"{task_suffix}"
                ),
                source_question_id=(
                    question_id
                ),
                display_order=order,
                prompt_template=prompt,
                input_names=inputs,
                prt_names=prts,
                part_label=part_label,
            )
        )

    return AdaptiveQuestionTasks(
        source_question_id=(
            question_id
        ),
        introduction_template=(
            introduction
        ),
        tasks=tasks,
    )


def _get_question_node(
    question_xml: str,
) -> ET.Element:
    try:
        root = ET.fromstring(
            question_xml
        )
    except ET.ParseError as error:
        raise AdaptiveTaskExtractionError(
            "Question XML is invalid."
        ) from error

    if root.tag == "question":
        return root

    question = root.find(
        ".//question"
    )

    if question is None:
        raise AdaptiveTaskExtractionError(
            "Question XML contains no question node."
        )

    return question


def _get_question_template(
    question: ET.Element,
) -> str:
    text_node = question.find(
        "questiontext/text"
    )

    if text_node is None:
        raise AdaptiveTaskExtractionError(
            "STACK question contains no question text."
        )

    template = (
        text_node.text
        or ""
    ).strip()

    if not template:
        raise AdaptiveTaskExtractionError(
            "STACK question text is empty."
        )

    return template


def _extract_prompt_blocks(
    template: str,
) -> list[str]:
    paragraphs = (
        _PARAGRAPH_PATTERN.findall(
            template
        )
    )

    if paragraphs:
        return [
            paragraph.strip()
            for paragraph in paragraphs
            if paragraph.strip()
        ]

    return [
        template.strip()
    ]


def _input_names(
    template: str,
) -> list[str]:
    result: list[str] = []

    for input_name in (
        _INPUT_PATTERN.findall(
            template
        )
    ):
        if input_name not in result:
            result.append(
                input_name
            )

    return result


def _part_label(
    template: str,
) -> str | None:
    match = (
        _PART_LABEL_PATTERN.search(
            template
        )
    )

    if match is None:
        return None

    return match.group(1).lower()


def _prt_names_for_inputs(
    *,
    inputs: list[str],
    prt_by_input: dict[
        str,
        list[str],
    ],
) -> list[str]:
    prts: list[str] = []

    for input_name in inputs:
        for prt_name in (
            prt_by_input.get(
                input_name,
                [],
            )
        ):
            if prt_name not in prts:
                prts.append(
                    prt_name
                )

    return prts


def _jsxgraph_bound_input_names(
    template: str,
) -> list[str]:
    """
    Return STACK inputs explicitly bound to a JSXGraph
    interaction through input-ref-ansN attributes.
    """
    result: list[str] = []

    for input_name in re.findall(
        r"input-ref-(ans\d+)\s*=",
        template,
        flags=re.IGNORECASE,
    ):
        normalized = input_name.lower()

        if normalized not in result:
            result.append(
                normalized
            )

    return result


def _is_hidden_input_block(
    block: str,
) -> bool:
    normalized = re.sub(
        r"\s+",
        "",
        block.lower(),
    )

    return (
        "visibility:hidden"
        in normalized
        and bool(
            _input_names(
                block
            )
        )
    )


def _merge_shared_prt_blocks(
    *,
    task_blocks: list[str],
    prt_by_input: dict[
        str,
        list[str],
    ],
) -> list[str]:
    if not task_blocks:
        return []

    merged: list[str] = []

    current_block = task_blocks[0]

    for next_block in task_blocks[1:]:
        current_inputs = _input_names(
            current_block
        )

        next_inputs = _input_names(
            next_block
        )

        current_prts = (
            _prt_names_for_inputs(
                inputs=current_inputs,
                prt_by_input=prt_by_input,
            )
        )

        next_prts = (
            _prt_names_for_inputs(
                inputs=next_inputs,
                prt_by_input=prt_by_input,
            )
        )

        shares_prt = any(
            prt_name in next_prts
            for prt_name in current_prts
        )

        if shares_prt:
            current_block = (
                current_block.rstrip()
                + "\n"
                + next_block.lstrip()
            )
            continue

        merged.append(
            current_block
        )

        current_block = next_block

    merged.append(
        current_block
    )

    return merged


def _map_inputs_to_prts(
    question: ET.Element,
) -> dict[str, list[str]]:
    mapping: dict[
        str,
        list[str],
    ] = {}

    for prt in question.findall(
        ".//prt"
    ):
        prt_name = (
            prt.findtext("name")
            or ""
        ).strip()

        if not prt_name:
            continue

        input_references: list[str] = []

        # Direct input references used inside PRT nodes.
        for sans in prt.findall(
            ".//sans"
        ):
            text = (
                sans.text
                or ""
            ).strip()

            for input_name in re.findall(
                r"\bans\d+\b",
                text,
            ):
                if (
                    input_name
                    not in input_references
                ):
                    input_references.append(
                        input_name
                    )

        # Some STACK questions define an expression inside
        # feedbackvariables and then reference that expression
        # from <sans>. The actual learner inputs may therefore
        # only occur inside feedbackvariables.
        feedbackvariables = prt.find(
            "feedbackvariables"
        )

        if feedbackvariables is not None:
            feedback_text = (
                feedbackvariables.findtext(
                    "text"
                )
                or ""
            )

            for input_name in re.findall(
                r"\bans\d+\b",
                feedback_text,
            ):
                if (
                    input_name
                    not in input_references
                ):
                    input_references.append(
                        input_name
                    )

        for input_name in input_references:
            mapping.setdefault(
                input_name,
                [],
            )

            if (
                prt_name
                not in mapping[input_name]
            ):
                mapping[
                    input_name
                ].append(
                    prt_name
                )

    return mapping
