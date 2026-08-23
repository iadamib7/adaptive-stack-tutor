import pytest

from backend.app.learning.adaptive_tasks.models import (
    AdaptiveTask,
)
from backend.app.learning.adaptive_tasks.renderer import (
    AdaptiveTaskRenderError,
    render_adaptive_task_html,
)


def task(
    *,
    task_id: str,
    inputs: list[str],
) -> AdaptiveTask:
    return AdaptiveTask(
        task_id=task_id,
        source_question_id=(
            task_id.split("::")[0]
        ),
        display_order=1,
        prompt_template="<p>Task</p>",
        input_names=inputs,
        prt_names=[
            f"prt{index}"
            for index in range(
                1,
                len(inputs) + 1,
            )
        ],
    )


def stack_input(name: str) -> str:
    return (
        f'<input type="text" '
        f'name="student-{name}" '
        f'id="student-{name}">'
    )


def test_single_input_question_is_preserved() -> None:
    html = (
        "<p>Simplify the expression.</p>"
        "<p>"
        "8^5 x 8^0 = "
        + stack_input("ans1")
        + "</p>"
    )

    result = render_adaptive_task_html(
        rendered_html=html,
        task=task(
            task_id="207419::1",
            inputs=["ans1"],
        ),
    )

    assert "Simplify the expression" in result
    assert "student-ans1" in result


def test_three_inputs_in_one_task_stay_together() -> None:
    html = (
        "<p>Write in simplest index form.</p>"
        "<p>"
        "108 = "
        + stack_input("ans1")
        + " x "
        + stack_input("ans2")
        + " ^ "
        + stack_input("ans3")
        + "</p>"
    )

    result = render_adaptive_task_html(
        rendered_html=html,
        task=task(
            task_id="206819::1",
            inputs=[
                "ans1",
                "ans2",
                "ans3",
            ],
        ),
    )

    assert "student-ans1" in result
    assert "student-ans2" in result
    assert "student-ans3" in result


def test_two_inputs_in_one_equation_stay_together() -> None:
    html = (
        "<p>Complete the equation.</p>"
        "<p>"
        "4^"
        + stack_input("ans1")
        + " = 1/4^3 = 4^2 / 4^"
        + stack_input("ans2")
        + "</p>"
    )

    result = render_adaptive_task_html(
        rendered_html=html,
        task=task(
            task_id="207420::1",
            inputs=[
                "ans1",
                "ans2",
            ],
        ),
    )

    assert "student-ans1" in result
    assert "student-ans2" in result


def test_part_a_isolated_from_other_parts() -> None:
    html = (
        "<p>Simplify each expression.</p>"
        "<p>(a) 2^3 x 2^4 = "
        + stack_input("ans1")
        + "^"
        + stack_input("ans2")
        + "</p>"
        "<p>(b) 5^8 / 5^3 = "
        + stack_input("ans3")
        + "^"
        + stack_input("ans4")
        + "</p>"
    )

    result = render_adaptive_task_html(
        rendered_html=html,
        task=task(
            task_id="206946::a",
            inputs=[
                "ans1",
                "ans2",
            ],
        ),
    )

    assert "(a)" in result
    assert "Simplify each expression" in result

    assert "student-ans1" in result
    assert "student-ans2" in result

    assert "(b)" not in result
    assert "student-ans3" not in result
    assert "student-ans4" not in result


def test_part_b_isolated_from_part_a() -> None:
    html = (
        "<p>Simplify each expression.</p>"
        "<p>(a) 2^3 x 2^4 = "
        + stack_input("ans1")
        + "^"
        + stack_input("ans2")
        + "</p>"
        "<p>(b) 5^8 / 5^3 = "
        + stack_input("ans3")
        + "^"
        + stack_input("ans4")
        + "</p>"
    )

    result = render_adaptive_task_html(
        rendered_html=html,
        task=task(
            task_id="206946::b",
            inputs=[
                "ans3",
                "ans4",
            ],
        ),
    )

    assert "(b)" in result
    assert "Simplify each expression" in result

    assert "student-ans3" in result
    assert "student-ans4" in result

    assert "(a)" not in result
    assert "student-ans1" not in result


def test_intro_is_reused_for_later_parts() -> None:
    html = (
        "<p>Leave each answer in index form.</p>"
        "<p>(a) "
        + stack_input("ans1")
        + "</p>"
        "<p>(b) "
        + stack_input("ans2")
        + "</p>"
    )

    result = render_adaptive_task_html(
        rendered_html=html,
        task=task(
            task_id="example::b",
            inputs=["ans2"],
        ),
    )

    assert (
        "Leave each answer in index form"
        in result
    )


def test_missing_required_input_is_rejected() -> None:
    html = (
        "<p>Question</p>"
        "<p>"
        + stack_input("ans1")
        + "</p>"
    )

    with pytest.raises(
        AdaptiveTaskRenderError,
        match="missing rendered inputs",
    ):
        render_adaptive_task_html(
            rendered_html=html,
            task=task(
                task_id="bad::1",
                inputs=[
                    "ans1",
                    "ans2",
                ],
            ),
        )


def test_unrelated_inputs_are_rejected() -> None:
    html = (
        "<p>Question</p>"
        "<p>"
        + stack_input("ans1")
        + stack_input("ans2")
        + "</p>"
    )

    with pytest.raises(
        AdaptiveTaskRenderError,
        match="unrelated rendered inputs",
    ):
        render_adaptive_task_html(
            rendered_html=html,
            task=task(
                task_id="bad::1",
                inputs=["ans1"],
            ),
        )


def test_empty_html_is_rejected() -> None:
    with pytest.raises(
        AdaptiveTaskRenderError,
        match="empty",
    ):
        render_adaptive_task_html(
            rendered_html="",
            task=task(
                task_id="bad::1",
                inputs=["ans1"],
            ),
        )

def test_visual_between_prompt_and_inputs_is_preserved() -> None:
    html = (
        "<p>Read the coordinates from the graph.</p>"
        '<div class="stack-graph">'
        '<svg viewBox="0 0 100 100">'
        '<circle cx="50" cy="50" r="4"></circle>'
        "</svg>"
        "</div>"
        "<p>"
        "A: ("
        + stack_input("ans1")
        + ", "
        + stack_input("ans2")
        + ")"
        "</p>"
    )

    result = render_adaptive_task_html(
        rendered_html=html,
        task=task(
            task_id="graph::1",
            inputs=[
                "ans1",
                "ans2",
            ],
        ),
    )

    assert "Read the coordinates" in result
    assert "stack-graph" in result
    assert "<svg" in result

    assert "student-ans1" in result
    assert "student-ans2" in result
