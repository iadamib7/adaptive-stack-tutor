from __future__ import annotations

import re

from backend.app.learning.adaptive_tasks.models import (
    AdaptiveTask,
)


_PARAGRAPH_PATTERN = re.compile(
    r"<p\b[^>]*>.*?</p>",
    flags=(
        re.IGNORECASE
        | re.DOTALL
    ),
)

_INPUT_NAME_PATTERN = re.compile(
    r"""name=["']student-([^"']+)["']""",
    flags=re.IGNORECASE,
)

_TAG_PATTERN = re.compile(
    r"<[^>]+>",
    flags=re.DOTALL,
)

_PART_LABEL_PATTERN = re.compile(
    r"""
    ^\s*
    (?:\\\()?
    \(?
    [a-zA-Z0-9]+
    \)?
    [.)]?
    (?:\\\))?
    \s*$
    """,
    flags=re.VERBOSE,
)


class AdaptiveTaskRenderError(
    ValueError
):
    pass


def render_adaptive_task_html(
    *,
    rendered_html: str,
    task: AdaptiveTask,
) -> str:
    """
    Reduce a fully rendered STACK question to one
    learner-facing adaptive task.

    A task may require one or multiple STACK inputs.

    The renderer preserves:
    - shared introductory context,
    - task-specific visual/context HTML,
    - every answer paragraph required by the task,
    - no unrelated answer inputs.
    """

    html = rendered_html.strip()

    if not html:
        raise AdaptiveTaskRenderError(
            "Rendered STACK HTML is empty."
        )

    paragraph_matches = list(
        _PARAGRAPH_PATTERN.finditer(
            html
        )
    )

    if not paragraph_matches:
        return _validate_task_inputs(
            html=html,
            task=task,
        )

    required_inputs = set(
        task.input_names
    )

    answer_paragraphs: list[
        tuple[
            re.Match[str],
            set[str],
        ]
    ] = []

    for match in paragraph_matches:
        inputs = set(
            _input_names_from_html(
                match.group(0)
            )
        )

        if inputs:
            answer_paragraphs.append(
                (
                    match,
                    inputs,
                )
            )

    if not answer_paragraphs:
        return _validate_task_inputs(
            html=html,
            task=task,
        )

    required_positions: list[int] = []

    for position, (
        _,
        paragraph_inputs,
    ) in enumerate(
        answer_paragraphs
    ):
        if (
            paragraph_inputs
            & required_inputs
        ):
            required_positions.append(
                position
            )

    if not required_positions:
        raise AdaptiveTaskRenderError(
            f"Could not find rendered HTML for "
            f"adaptive task {task.task_id}."
        )

    first_required_position = min(
        required_positions
    )

    last_required_position = max(
        required_positions
    )

    first_required_match = (
        answer_paragraphs[
            first_required_position
        ][0]
    )

    last_required_match = (
        answer_paragraphs[
            last_required_position
        ][0]
    )

    first_answer_match = (
        answer_paragraphs[0][0]
    )

    shared_end = _find_shared_context_end(
        html=html,
        paragraph_matches=paragraph_matches,
        first_answer_match=first_answer_match,
    )

    shared_html = html[
        :shared_end
    ].strip()

    if first_required_position == 0:
        local_start = shared_end
    else:
        previous_answer_match = (
            answer_paragraphs[
                first_required_position - 1
            ][0]
        )

        local_start = (
            previous_answer_match.end()
        )

    local_end = (
        last_required_match.end()
    )

    local_html = html[
        local_start:local_end
    ].strip()

    pieces: list[str] = []

    if shared_html:
        pieces.append(
            shared_html
        )

    if local_html:
        pieces.append(
            local_html
        )

    task_html = "\n".join(
        pieces
    )

    return _validate_task_inputs(
        html=task_html,
        task=task,
    )


def _find_shared_context_end(
    *,
    html: str,
    paragraph_matches: list[
        re.Match[str]
    ],
    first_answer_match: re.Match[str],
) -> int:
    """
    Find where globally shared context ends.

    A standalone part label such as "(a)" begins
    task-specific content.

    If there is no part label, everything before the
    first answer is shared. This preserves graphs and
    diagrams used by multiple inputs in one task.
    """

    for match in paragraph_matches:
        if match.start() >= (
            first_answer_match.start()
        ):
            break

        if _is_part_marker(
            match.group(0)
        ):
            return match.start()

    return first_answer_match.start()


def _is_part_marker(
    paragraph_html: str,
) -> bool:
    text = _TAG_PATTERN.sub(
        "",
        paragraph_html,
    )

    text = (
        text
        .replace("&nbsp;", " ")
        .strip()
    )

    return bool(
        _PART_LABEL_PATTERN.fullmatch(
            text
        )
    )


def _input_names_from_html(
    html: str,
) -> list[str]:
    names: list[str] = []

    for name in (
        _INPUT_NAME_PATTERN.findall(
            html
        )
    ):
        if name not in names:
            names.append(
                name
            )

    return names


def _validate_task_inputs(
    *,
    html: str,
    task: AdaptiveTask,
) -> str:
    rendered_inputs = set(
        _input_names_from_html(
            html
        )
    )

    required_inputs = set(
        task.input_names
    )

    missing = (
        required_inputs
        - rendered_inputs
    )

    if missing:
        missing_text = ", ".join(
            sorted(missing)
        )

        raise AdaptiveTaskRenderError(
            f"Adaptive task {task.task_id} "
            f"is missing rendered inputs: "
            f"{missing_text}."
        )

    unrelated = (
        rendered_inputs
        - required_inputs
    )

    if unrelated:
        unrelated_text = ", ".join(
            sorted(unrelated)
        )

        raise AdaptiveTaskRenderError(
            f"Adaptive task {task.task_id} "
            f"contains unrelated rendered inputs: "
            f"{unrelated_text}."
        )

    return html.strip()
