import pytest

from backend.app.integrations.stack_api.models import (
    NormalizedStackResult,
    StackPRTResult,
)

from backend.app.learning.adaptive_engine import (
    AdaptiveQuestion,
    CurriculumIndependentAdaptiveEngine,
)

from backend.app.learning.adaptive_engine.stack_evidence import (
    StackEvidenceAdapter,
)


def test_extracts_score_and_raw_prt_path() -> None:
    adapter = StackEvidenceAdapter()

    evidence = (
        adapter.to_response_evidence(
            question_id="Q1",
            grade_payload={
                "score": 0.0,
                "prtresults": {
                    "prt1": {
                        "score": 0.0,
                        "answernotes": [
                            "prt1-1-F",
                            "prt1-2-T",
                        ],
                    }
                },
            },
        )
    )

    assert evidence.score == 0.0

    assert evidence.prt_outcome == (
        "prt1:prt1-1-F|prt1-2-T"
    )


def test_maps_raw_prt_path_to_semantic_outcome() -> None:
    adapter = StackEvidenceAdapter()

    raw_path = (
        "prt1:prt1-1-F|prt1-2-T"
    )

    evidence = (
        adapter.to_response_evidence(
            question_id="Q1",
            grade_payload={
                "score": 0.0,
                "prtresults": {
                    "prt1": {
                        "answernotes": (
                            "prt1-1-F | "
                            "prt1-2-T"
                        ),
                    }
                },
            },
            outcome_aliases={
                raw_path: "sign_error",
            },
        )
    )

    assert (
        evidence.prt_outcome
        == "sign_error"
    )


def test_full_score_without_prt_note_is_correct() -> None:
    adapter = StackEvidenceAdapter()

    evidence = (
        adapter.to_response_evidence(
            question_id="Q1",
            grade_payload={
                "score": 1.0,
                "prtresults": {},
            },
        )
    )

    assert evidence.score == 1.0

    assert (
        evidence.prt_outcome
        == "correct"
    )


def test_partial_score_without_note_is_partial() -> None:
    adapter = StackEvidenceAdapter()

    evidence = (
        adapter.to_response_evidence(
            question_id="Q1",
            grade_payload={
                "score": 0.5,
            },
        )
    )

    assert (
        evidence.prt_outcome
        == "partial"
    )


def test_invalid_stack_score_is_rejected() -> None:
    adapter = StackEvidenceAdapter()

    with pytest.raises(
        ValueError,
    ):
        adapter.to_response_evidence(
            question_id="Q1",
            grade_payload={
                "score": "bad",
            },
        )


def test_real_prt_evidence_drives_branch() -> None:
    questions = [
        AdaptiveQuestion(
            question_id="Q1",
            title="Entry question",
            difficulty=0.0,
        ),
        AdaptiveQuestion(
            question_id="Q2",
            title=(
                "Sign-error remediation"
            ),
            difficulty=-0.4,
            supports=(
                "sign_error",
            ),
        ),
        AdaptiveQuestion(
            question_id="Q3",
            title="General practice",
            difficulty=0.4,
        ),
    ]

    engine = (
        CurriculumIndependentAdaptiveEngine(
            questions
        )
    )

    first = engine.start(
        learner_id=500
    )

    assert first is not None
    assert (
        first.question.question_id
        == "Q1"
    )

    adapter = StackEvidenceAdapter()

    raw_path = (
        "prt1:prt1-1-F|prt1-2-T"
    )

    evidence = (
        adapter.to_response_evidence(
            question_id="Q1",
            grade_payload={
                "score": 0.0,
                "prtresults": {
                    "prt1": {
                        "score": 0.0,
                        "answernotes": [
                            "prt1-1-F",
                            "prt1-2-T",
                        ],
                    }
                },
            },
            outcome_aliases={
                raw_path: "sign_error",
            },
        )
    )

    decision = engine.submit(
        learner_id=500,
        evidence=evidence,
    )

    assert decision is not None

    assert (
        decision.question.question_id
        == "Q2"
    )



def test_ignores_unscored_prts() -> None:
    adapter = StackEvidenceAdapter()

    result = NormalizedStackResult(
        question_id="Q1",
        valid=True,
        overall_score=0.5,
        prts=[
            StackPRTResult(
                prt_name="prt1",
                score=None,
                penalty=None,
            ),
            StackPRTResult(
                prt_name="prt2",
                score=1.0,
                penalty=0.0,
            ),
        ],
    )

    evidence = (
        adapter.from_normalized_result(
            result=result
        )
    )

    assert evidence.score == 1.0


def test_averages_only_numeric_prt_scores(
) -> None:
    adapter = StackEvidenceAdapter()

    result = NormalizedStackResult(
        question_id="Q1",
        valid=True,
        overall_score=0.6,
        prts=[
            StackPRTResult(
                prt_name="prt1",
                score=None,
                penalty=None,
            ),
            StackPRTResult(
                prt_name="prt2",
                score=0.5,
                penalty=0.0,
            ),
            StackPRTResult(
                prt_name="prt3",
                score=1.0,
                penalty=0.0,
            ),
        ],
    )

    evidence = (
        adapter.from_normalized_result(
            result=result
        )
    )

    assert evidence.score == 0.75


def test_falls_back_to_overall_score_when_prts_unscored(
) -> None:
    adapter = StackEvidenceAdapter()

    result = NormalizedStackResult(
        question_id="Q1",
        valid=True,
        overall_score=0.5,
        prts=[
            StackPRTResult(
                prt_name="prt1",
                score=None,
                penalty=None,
            ),
        ],
    )

    evidence = (
        adapter.from_normalized_result(
            result=result
        )
    )

    assert evidence.score == 0.5


def test_rejects_result_without_numeric_score_evidence(
) -> None:
    adapter = StackEvidenceAdapter()

    result = NormalizedStackResult(
        question_id="Q1",
        valid=True,
        overall_score=None,
        prts=[
            StackPRTResult(
                prt_name="prt1",
                score=None,
                penalty=None,
            ),
        ],
    )

    with pytest.raises(
        ValueError,
        match="no numeric score evidence",
    ):
        adapter.from_normalized_result(
            result=result
        )
