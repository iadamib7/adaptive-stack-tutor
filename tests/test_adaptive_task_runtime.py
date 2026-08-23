import pytest

from backend.app.learning.adaptive_tasks.runtime import (
    AdaptiveTaskRuntimeError,
    AdaptiveTaskRuntimeService,
)


def make_question(
    paragraphs: str,
    prts: list[
        tuple[str, str]
    ],
) -> str:
    prt_xml = ""

    for (
        prt_name,
        answer_name,
    ) in prts:
        prt_xml += f"""
        <prt>
            <name>{prt_name}</name>
            <node>
                <name>0</name>
                <answertest>
                    AlgEquiv
                </answertest>
                <sans>
                    {answer_name}
                </sans>
                <tans>
                    teacher
                </tans>
            </node>
        </prt>
        """

    return f"""
    <quiz>
        <question type="stack">
            <questiontext>
                <text><![CDATA[
                    {paragraphs}
                ]]></text>
            </questiontext>

            {prt_xml}
        </question>
    </quiz>
    """


def single_task_xml() -> str:
    return make_question(
        """
        <p>
            Express the number in
            index form.
        </p>

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


def four_task_xml() -> str:
    return make_question(
        """
        <p>
            Simplify each expression.
        </p>

        <p>
            (a)
            2^3 * 2^4 =
            [[input:ans1]]
            ^
            [[input:ans2]]
        </p>

        <p>
            (b)
            5^8 / 5^3 =
            [[input:ans3]]
            ^
            [[input:ans4]]
        </p>

        <p>
            (c)
            (3^2)^4 =
            [[input:ans5]]
            ^
            [[input:ans6]]
        </p>

        <p>
            (d)
            7^-3 =
            [[input:ans7]]
            ^
            [[input:ans8]]
        </p>
        """,
        [
            ("prt1", "ans1"),
            ("prt2", "ans2"),
            ("prt3", "ans3"),
            ("prt4", "ans4"),
            ("prt5", "ans5"),
            ("prt6", "ans6"),
            ("prt7", "ans7"),
            ("prt8", "ans8"),
        ],
    )


def test_single_task_starts_at_first_task() -> None:
    runtime = (
        AdaptiveTaskRuntimeService()
    )

    state = runtime.start(
        student_id=1,
        source_question_id="206873",
        question_xml=single_task_xml(),
    )

    assert state.task_count == 1

    assert state.current_task is not None

    assert state.current_task.input_names == [
        "ans1",
        "ans2",
    ]

    assert state.completed is False


def test_multi_part_question_starts_at_part_a() -> None:
    runtime = (
        AdaptiveTaskRuntimeService()
    )

    state = runtime.start(
        student_id=1,
        source_question_id="206946",
        question_xml=four_task_xml(),
    )

    assert state.task_count == 4

    assert state.current_task is not None

    assert state.current_task.task_id == (
        "206946::a"
    )

    assert state.current_task_number == 1


def test_advancing_moves_to_next_task() -> None:
    runtime = (
        AdaptiveTaskRuntimeService()
    )

    runtime.start(
        student_id=1,
        source_question_id="206946",
        question_xml=four_task_xml(),
    )

    state = runtime.advance(
        student_id=1
    )

    assert state.completed is False
    assert state.current_task is not None

    assert state.current_task.task_id == (
        "206946::b"
    )

    assert state.current_task_number == 2


def test_all_four_tasks_complete_source_question() -> None:
    runtime = (
        AdaptiveTaskRuntimeService()
    )

    runtime.start(
        student_id=1,
        source_question_id="206946",
        question_xml=four_task_xml(),
    )

    runtime.advance(1)
    runtime.advance(1)
    runtime.advance(1)

    state = runtime.advance(1)

    assert state.completed is True
    assert state.current_task is None
    assert state.task_count == 4


def test_single_task_completes_after_one_advance() -> None:
    runtime = (
        AdaptiveTaskRuntimeService()
    )

    runtime.start(
        student_id=1,
        source_question_id="206873",
        question_xml=single_task_xml(),
    )

    state = runtime.advance(
        student_id=1
    )

    assert state.completed is True
    assert state.current_task is None


def test_students_have_independent_runtime_state() -> None:
    runtime = (
        AdaptiveTaskRuntimeService()
    )

    runtime.start(
        student_id=1,
        source_question_id="206946",
        question_xml=four_task_xml(),
    )

    runtime.start(
        student_id=2,
        source_question_id="206946",
        question_xml=four_task_xml(),
    )

    runtime.advance(1)

    first = runtime.get_state(1)
    second = runtime.get_state(2)

    assert first is not None
    assert second is not None

    assert first.current_task_index == 1
    assert second.current_task_index == 0


def test_restart_returns_to_first_task() -> None:
    runtime = (
        AdaptiveTaskRuntimeService()
    )

    runtime.start(
        student_id=1,
        source_question_id="206946",
        question_xml=four_task_xml(),
    )

    runtime.advance(1)
    runtime.advance(1)

    state = runtime.restart(1)

    assert state.completed is False
    assert state.current_task_index == 0

    assert state.current_task is not None

    assert state.current_task.task_id == (
        "206946::a"
    )


def test_missing_runtime_is_rejected() -> None:
    runtime = (
        AdaptiveTaskRuntimeService()
    )

    with pytest.raises(
        AdaptiveTaskRuntimeError,
        match="No adaptive task runtime",
    ):
        runtime.get_current_task(
            student_id=999
        )


def test_completed_runtime_cannot_advance_again() -> None:
    runtime = (
        AdaptiveTaskRuntimeService()
    )

    runtime.start(
        student_id=1,
        source_question_id="206873",
        question_xml=single_task_xml(),
    )

    runtime.advance(1)

    with pytest.raises(
        AdaptiveTaskRuntimeError,
        match="already been completed",
    ):
        runtime.advance(1)
