import pytest

from backend.app.learning.adaptive_tasks.presentation import (
    AdaptiveTaskPresentationError,
    AdaptiveTaskPresentationService,
)
from backend.app.learning.adaptive_tasks.runtime import (
    AdaptiveTaskRuntimeService,
)


def make_question(
    body: str,
    prts: list[
        tuple[str, str]
    ],
) -> str:
    prt_xml = ""

    for prt_name, answer_name in prts:
        prt_xml += f"""
        <prt>
            <name>{prt_name}</name>
            <node>
                <name>0</name>
                <answertest>
                    AlgEquiv
                </answertest>
                <sans>{answer_name}</sans>
                <tans>teacher</tans>
            </node>
        </prt>
        """

    return f"""
    <quiz>
        <question type="stack">
            <questiontext>
                <text><![CDATA[
                    {body}
                ]]></text>
            </questiontext>

            {prt_xml}
        </question>
    </quiz>
    """


def input_html(name: str) -> str:
    return (
        f'<input type="text" '
        f'name="student-{name}" '
        f'id="student-{name}">'
    )


def test_multi_input_task_is_presented_together() -> None:
    xml = make_question(
        """
        <p>Express in index form.</p>
        <p>
            64 =
            [[input:ans1]]
            ^
            [[input:ans2]]
        </p>
        """,
        [
            ("prt1", "ans1"),
            ("prt2", "ans2"),
        ],
    )

    rendered = {
        "question_id": "206873",
        "question_xml": xml,
        "seed": 123,
        "html": (
            "<p>Express in index form.</p>"
            "<p>64 = "
            + input_html("ans1")
            + "^"
            + input_html("ans2")
            + "</p>"
        ),
        "inputs": {
            "ans1": {},
            "ans2": {},
        },
        "worked_solution": "",
        "question_note": "",
        "available_variants": [123],
    }

    service = AdaptiveTaskPresentationService(
        runtime_service=(
            AdaptiveTaskRuntimeService()
        )
    )

    result = service.present(
        student_id=1,
        rendered_question=rendered,
    )

    assert result["task_count"] == 1

    assert result[
        "task_input_names"
    ] == [
        "ans1",
        "ans2",
    ]

    assert result[
        "task_prt_names"
    ] == [
        "prt1",
        "prt2",
    ]

    assert set(
        result["inputs"]
    ) == {
        "ans1",
        "ans2",
    }


def test_multi_part_question_presents_part_a_only() -> None:
    xml = make_question(
        """
        <p>Simplify each expression.</p>

        <p>
            (a)
            [[input:ans1]]
            ^
            [[input:ans2]]
        </p>

        <p>
            (b)
            [[input:ans3]]
            ^
            [[input:ans4]]
        </p>
        """,
        [
            ("prt1", "ans1"),
            ("prt2", "ans2"),
            ("prt3", "ans3"),
            ("prt4", "ans4"),
        ],
    )

    rendered = {
        "question_id": "206946",
        "question_xml": xml,
        "seed": 456,
        "html": (
            "<p>Simplify each expression.</p>"
            "<p>(a)"
            + input_html("ans1")
            + "^"
            + input_html("ans2")
            + "</p>"
            "<p>(b)"
            + input_html("ans3")
            + "^"
            + input_html("ans4")
            + "</p>"
        ),
        "inputs": {
            "ans1": {},
            "ans2": {},
            "ans3": {},
            "ans4": {},
        },
        "worked_solution": "",
        "question_note": "",
        "available_variants": [456],
    }

    service = AdaptiveTaskPresentationService(
        runtime_service=(
            AdaptiveTaskRuntimeService()
        )
    )

    result = service.present(
        student_id=1,
        rendered_question=rendered,
    )

    assert result["task_count"] == 2
    assert result["task_index"] == 0
    assert result["task_id"] == "206946::a"

    assert "student-ans1" in result["html"]
    assert "student-ans2" in result["html"]

    assert "student-ans3" not in result["html"]
    assert "student-ans4" not in result["html"]


def test_runtime_position_is_preserved() -> None:
    xml = make_question(
        """
        <p>Work these out.</p>

        <p>
            (a)
            [[input:ans1]]
        </p>

        <p>
            (b)
            [[input:ans2]]
        </p>
        """,
        [
            ("prt1", "ans1"),
            ("prt2", "ans2"),
        ],
    )

    rendered = {
        "question_id": "multi",
        "question_xml": xml,
        "seed": 789,
        "html": (
            "<p>Work these out.</p>"
            "<p>(a)"
            + input_html("ans1")
            + "</p>"
            "<p>(b)"
            + input_html("ans2")
            + "</p>"
        ),
        "inputs": {
            "ans1": {},
            "ans2": {},
        },
        "worked_solution": "",
        "question_note": "",
        "available_variants": [789],
    }

    runtime = AdaptiveTaskRuntimeService()

    service = AdaptiveTaskPresentationService(
        runtime_service=runtime
    )

    first = service.present(
        student_id=1,
        rendered_question=rendered,
    )

    assert first["task_id"] == "multi::a"

    runtime.advance(1)

    second = service.present(
        student_id=1,
        rendered_question=rendered,
    )

    assert second["task_id"] == "multi::b"
    assert second["task_index"] == 1

    assert "student-ans2" in second["html"]
    assert "student-ans1" not in second["html"]


def test_students_have_independent_presentations() -> None:
    xml = make_question(
        """
        <p>Tasks.</p>
        <p>(a)[[input:ans1]]</p>
        <p>(b)[[input:ans2]]</p>
        """,
        [
            ("prt1", "ans1"),
            ("prt2", "ans2"),
        ],
    )

    rendered = {
        "question_id": "multi",
        "question_xml": xml,
        "seed": 100,
        "html": (
            "<p>Tasks.</p>"
            "<p>(a)"
            + input_html("ans1")
            + "</p>"
            "<p>(b)"
            + input_html("ans2")
            + "</p>"
        ),
        "inputs": {
            "ans1": {},
            "ans2": {},
        },
        "worked_solution": "",
        "question_note": "",
        "available_variants": [100],
    }

    runtime = AdaptiveTaskRuntimeService()

    service = AdaptiveTaskPresentationService(
        runtime_service=runtime
    )

    service.present(
        student_id=1,
        rendered_question=rendered,
    )

    service.present(
        student_id=2,
        rendered_question=rendered,
    )

    runtime.advance(1)

    student_one = service.present(
        student_id=1,
        rendered_question=rendered,
    )

    student_two = service.present(
        student_id=2,
        rendered_question=rendered,
    )

    assert student_one["task_id"] == (
        "multi::b"
    )

    assert student_two["task_id"] == (
        "multi::a"
    )


def test_missing_rendered_task_input_is_rejected() -> None:
    xml = make_question(
        """
        <p>
            [[input:ans1]]
            [[input:ans2]]
        </p>
        """,
        [
            ("prt1", "ans1"),
            ("prt2", "ans2"),
        ],
    )

    rendered = {
        "question_id": "broken",
        "question_xml": xml,
        "seed": 1,
        "html": (
            "<p>"
            + input_html("ans1")
            + "</p>"
        ),
        "inputs": {
            "ans1": {},
        },
        "worked_solution": "",
        "question_note": "",
        "available_variants": [1],
    }

    service = AdaptiveTaskPresentationService(
        runtime_service=(
            AdaptiveTaskRuntimeService()
        )
    )

    with pytest.raises(
        AdaptiveTaskPresentationError,
        match="required input ans2",
    ):
        service.present(
            student_id=1,
            rendered_question=rendered,
        )
