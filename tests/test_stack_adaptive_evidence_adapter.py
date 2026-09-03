import pytest

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
