import pytest

from backend.app.integrations.stack_api.adapter import (
    StackEvaluationAdapter,
)
from backend.app.integrations.stack_api.mock_client import (
    MockStackEvaluationClient,
)
from backend.app.integrations.stack_api.models import (
    NormalizedStackResult,
    StackEvaluationRequest,
    StackPRTResult,
)


def build_result(
    question_id: str = "207582",
    score: float = 1.0,
    answer_note: str = "prt1-1-T",
    feedback: str | None = "Correct answer.",
) -> NormalizedStackResult:
    return NormalizedStackResult(
        question_id=question_id,
        valid=True,
        seed=123,
        prts=[
            StackPRTResult(
                prt_name="prt1",
                score=score,
                penalty=0.0,
                answer_notes=[answer_note],
                feedback=feedback,
            )
        ],
    )


def test_correct_result_converts_to_session_outcome() -> None:
    result = build_result()

    client = MockStackEvaluationClient(
        {"207582": result}
    )

    adapter = StackEvaluationAdapter(client)

    outcome = adapter.evaluate_for_session(
        student_id=1,
        concept_id="KE-G9-INTEGER-OPERATIONS",
        question_id="207582",
        question_xml="<quiz></quiz>",
        student_answers={
            "ans1": "25",
        },
    )

    assert outcome.student_id == 1
    assert outcome.question_id == "207582"
    assert outcome.outcome_code == "prt1-1-T"
    assert outcome.score == 1.0
    assert outcome.stack_feedback == (
        "Correct answer."
    )


def test_incorrect_result_is_preserved() -> None:
    result = build_result(
        score=0.0,
        answer_note="prt1-1-F",
        feedback="Review integer addition.",
    )

    adapter = StackEvaluationAdapter(
        MockStackEvaluationClient(
            {"207582": result}
        )
    )

    outcome = adapter.evaluate_for_session(
        student_id=1,
        concept_id="KE-G9-INTEGER-OPERATIONS",
        question_id="207582",
        question_xml="<quiz></quiz>",
        student_answers={
            "ans1": "10",
        },
    )

    assert outcome.score == 0.0
    assert outcome.outcome_code == "prt1-1-F"
    assert "Review" in (
        outcome.stack_feedback or ""
    )


def test_partial_score_is_preserved() -> None:
    result = build_result(
        score=0.5,
        answer_note="prt1-2-T",
        feedback="Partially correct.",
    )

    adapter = StackEvaluationAdapter(
        MockStackEvaluationClient(
            {"207582": result}
        )
    )

    outcome = adapter.evaluate_for_session(
        student_id=1,
        concept_id="KE-G9-INTEGER-OPERATIONS",
        question_id="207582",
        question_xml="<quiz></quiz>",
        student_answers={
            "ans1": "20.5",
        },
    )

    assert outcome.score == 0.5
    assert outcome.outcome_code == "prt1-2-T"


def test_multiple_prts_require_target_name() -> None:
    result = NormalizedStackResult(
        question_id="220747",
        valid=True,
        prts=[
            StackPRTResult(
                prt_name="prt1",
                score=1.0,
                penalty=0.0,
                answer_notes=["prt1-1-T"],
            ),
            StackPRTResult(
                prt_name="prt2",
                score=0.0,
                penalty=0.0,
                answer_notes=["prt2-1-F"],
            ),
        ],
    )

    adapter = StackEvaluationAdapter(
        MockStackEvaluationClient()
    )

    with pytest.raises(
        ValueError,
        match="multiple PRT",
    ):
        adapter.to_session_outcome(
            student_id=1,
            concept_id="TEST-CONCEPT",
            result=result,
        )


def test_named_prt_can_be_selected() -> None:
    result = NormalizedStackResult(
        question_id="220747",
        valid=True,
        raw_feedback="Continue practising.",
        prts=[
            StackPRTResult(
                prt_name="prt1",
                score=1.0,
                penalty=0.0,
                answer_notes=["prt1-1-T"],
            ),
            StackPRTResult(
                prt_name="prt5",
                score=0.25,
                penalty=0.0,
                answer_notes=["prt5-4-T"],
                feedback="Likely rounding mistake.",
            ),
        ],
    )

    adapter = StackEvaluationAdapter(
        MockStackEvaluationClient()
    )

    outcome = adapter.to_session_outcome(
        student_id=1,
        concept_id="KE-G9-GROUPED-DATA",
        result=result,
        target_prt_name="prt5",
    )

    assert outcome.outcome_code == "prt5-4-T"
    assert outcome.score == 0.25
    assert outcome.stack_feedback == (
        "Likely rounding mistake. "
        "Continue practising."
    )


def test_invalid_stack_response_is_rejected() -> None:
    result = NormalizedStackResult(
        question_id="207582",
        valid=False,
        validation_errors=[
            "The answer contains invalid syntax.",
        ],
    )

    adapter = StackEvaluationAdapter(
        MockStackEvaluationClient()
    )

    with pytest.raises(
        ValueError,
        match="invalid syntax",
    ):
        adapter.to_session_outcome(
            student_id=1,
            concept_id="KE-G9-INTEGER-OPERATIONS",
            result=result,
        )


def test_missing_answer_note_is_rejected() -> None:
    result = NormalizedStackResult(
        question_id="207582",
        valid=True,
        prts=[
            StackPRTResult(
                prt_name="prt1",
                score=1.0,
                penalty=0.0,
                answer_notes=[],
            )
        ],
    )

    adapter = StackEvaluationAdapter(
        MockStackEvaluationClient()
    )

    with pytest.raises(
        ValueError,
        match="no answer note",
    ):
        adapter.to_session_outcome(
            student_id=1,
            concept_id="KE-G9-INTEGER-OPERATIONS",
            result=result,
        )


def test_mock_client_records_request() -> None:
    result = build_result()

    client = MockStackEvaluationClient(
        {"207582": result}
    )

    request = StackEvaluationRequest(
        question_id="207582",
        question_xml="<quiz></quiz>",
        student_answers={
            "ans1": "25",
        },
        seed=456,
    )

    returned_result = client.evaluate(request)

    assert returned_result == result
    assert len(client.requests) == 1
    assert client.requests[0].seed == 456


def test_unregistered_mock_question_is_rejected() -> None:
    client = MockStackEvaluationClient()

    with pytest.raises(
        ValueError,
        match="No mock STACK result",
    ):
        client.evaluate(
            StackEvaluationRequest(
                question_id="UNKNOWN",
                question_xml="<quiz></quiz>",
                student_answers={
                    "ans1": "1",
                },
            )
        )
