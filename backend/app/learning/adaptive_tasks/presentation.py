from __future__ import annotations

from typing import Any

from backend.app.learning.adaptive_tasks.renderer import (
    render_adaptive_task_html,
)
from backend.app.learning.adaptive_tasks.runtime import (
    AdaptiveTaskRuntimeService,
)


class AdaptiveTaskPresentationError(
    ValueError
):
    pass


class AdaptiveTaskPresentationService:
    """
    Convert one fully rendered STACK source question into
    the current learner-facing adaptive task.

    This service owns no grading logic.
    """

    def __init__(
        self,
        runtime_service: AdaptiveTaskRuntimeService,
    ) -> None:
        self.runtime_service = runtime_service

    def present(
        self,
        *,
        student_id: int,
        rendered_question: dict[str, Any],
    ) -> dict[str, Any]:
        question_id = str(
            rendered_question["question_id"]
        )

        question_xml = str(
            rendered_question["question_xml"]
        )

        state = self.runtime_service.get_state(
            student_id
        )

        if (
            state is None
            or state.source_question_id
            != question_id
            or state.completed
        ):
            state = self.runtime_service.start(
                student_id=student_id,
                source_question_id=question_id,
                question_xml=question_xml,
            )

        current_task = state.current_task

        if current_task is None:
            raise AdaptiveTaskPresentationError(
                "The adaptive source question "
                "contains no active learner task."
            )

        full_inputs = rendered_question.get(
            "inputs",
            {},
        )

        if not isinstance(
            full_inputs,
            dict,
        ):
            raise AdaptiveTaskPresentationError(
                "Rendered STACK inputs are invalid."
            )

        task_inputs = {}

        for input_name in (
            current_task.input_names
        ):
            if input_name not in full_inputs:
                raise AdaptiveTaskPresentationError(
                    f"STACK did not render required "
                    f"input {input_name} for "
                    f"{current_task.task_id}."
                )

            task_inputs[input_name] = (
                full_inputs[input_name]
            )

        task_html = render_adaptive_task_html(
            rendered_html=str(
                rendered_question["html"]
            ),
            task=current_task,
        )

        return {
            "question_id": question_id,
            "seed": rendered_question["seed"],
            "html": task_html,
            "inputs": task_inputs,
            "task_id": current_task.task_id,
            "task_input_names": list(
                current_task.input_names
            ),
            "task_prt_names": list(
                current_task.prt_names
            ),
            "task_index": (
                state.current_task_index
            ),
            "task_count": state.task_count,
            "worked_solution": (
                rendered_question.get(
                    "worked_solution",
                    "",
                )
            ),
            "question_note": (
                rendered_question.get(
                    "question_note",
                    "",
                )
            ),
            "available_variants": (
                rendered_question.get(
                    "available_variants",
                    [],
                )
            ),
        }
