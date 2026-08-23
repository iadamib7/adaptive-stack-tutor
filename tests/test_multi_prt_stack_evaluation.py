import pytest

from backend.app.integrations.stack_api.adapter import (
    StackEvaluationAdapter,
)
from backend.app.integrations.stack_api.mock_client import (
    MockStackEvaluationClient,
)
from backend.app.integrations.stack_api.models import (
    NormalizedStackResult,
    StackPRTResult,
)


def build_adapter() -> StackEvaluationAdapter:
    return StackEvaluationAdapter(
        client=MockStackEvaluationClient()
    )


def result_with_scores(
    scores: list[float],
) -> NormalizedStackResult:
    return NormalizedStackResult(
        question_id="206819",
        valid=True,
        seed=123,
        prts=[
            StackPRTResult(
                prt_name=f"prt{index}",
                score=score,
                penalty=0.0,
                answer_notes=[
                    (
                        f"prt{index}-1-T"
                        if score == 1.0
                        else f"prt{index}-1-F"
                    )
                ],
                feedback=None,
            )
            for index, score
            in enumerate(
                scores,
                start=1,
            )
        ],
    )


def test_all_correct_prts_produce_full_score() -> None:
    adapter = build_adapter()

    outcome = adapter.to_session_outcome(
        student_id=1,
        concept_id="indices",
        result=result_with_scores(
            [1.0, 1.0, 1.0]
        ),
        target_prt_names=[
            "prt1",
            "prt2",
            "prt3",
        ],
    )

    assert outcome.score == 1.0


def test_mixed_prts_produce_partial_score() -> None:
    adapter = build_adapter()

    outcome = adapter.to_session_outcome(
        student_id=1,
        concept_id="indices",
        result=result_with_scores(
            [1.0, 1.0, 0.0]
        ),
        target_prt_names=[
            "prt1",
            "prt2",
            "prt3",
        ],
    )

    assert outcome.score == pytest.approx(
        2 / 3
    )


def test_all_wrong_prts_produce_zero() -> None:
    adapter = build_adapter()

    outcome = adapter.to_session_outcome(
        student_id=1,
        concept_id="indices",
        result=result_with_scores(
            [0.0, 0.0]
        ),
        target_prt_names=[
            "prt1",
            "prt2",
        ],
    )

    assert outcome.score == 0.0


def test_multi_prt_outcome_contains_all_notes() -> None:
    adapter = build_adapter()

    outcome = adapter.to_session_outcome(
        student_id=1,
        concept_id="indices",
        result=result_with_scores(
            [1.0, 0.0]
        ),
        target_prt_names=[
            "prt1",
            "prt2",
        ],
    )

    assert "prt1-1-T" in (
        outcome.outcome_code
    )

    assert "prt2-1-F" in (
        outcome.outcome_code
    )


def test_only_requested_prts_are_aggregated() -> None:
    adapter = build_adapter()

    outcome = adapter.to_session_outcome(
        student_id=1,
        concept_id="indices",
        result=result_with_scores(
            [1.0, 1.0, 0.0]
        ),
        target_prt_names=[
            "prt1",
            "prt2",
        ],
    )

    assert outcome.score == 1.0


def test_unknown_requested_prt_is_rejected() -> None:
    adapter = build_adapter()

    with pytest.raises(
        ValueError,
        match="prt99",
    ):
        adapter.to_session_outcome(
            student_id=1,
            concept_id="indices",
            result=result_with_scores(
                [1.0, 1.0]
            ),
            target_prt_names=[
                "prt1",
                "prt99",
            ],
        )


def test_singular_and_plural_targets_cannot_mix() -> None:
    adapter = build_adapter()

    with pytest.raises(
        ValueError,
        match="either",
    ):
        adapter.to_session_outcome(
            student_id=1,
            concept_id="indices",
            result=result_with_scores(
                [1.0, 1.0]
            ),
            target_prt_name="prt1",
            target_prt_names=[
                "prt1",
                "prt2",
            ],
        )


def test_existing_single_prt_behavior_still_works() -> None:
    adapter = build_adapter()

    outcome = adapter.to_session_outcome(
        student_id=1,
        concept_id="indices",
        result=result_with_scores(
            [1.0]
        ),
        target_prt_name="prt1",
    )

    assert outcome.score == 1.0
    assert outcome.outcome_code == (
        "prt1-1-T"
    )
