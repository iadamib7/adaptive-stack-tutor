import pytest

from backend.app.learning.adaptive_engine.historical_responses import (
    HistoricalStackResponseImporter,
)


CSV_TEXT = """Last name,First name,Email address,State,Grade/10.00,Question 1,Response 1,Right answer 1,Question 2,Response 2,Right answer 2
,,,Finished,5,Solve x+2=5,"Seed: 100; ans1: 3 [score]; prt1: # = 1 | prt1-1-T","Seed: 100; ans1: 3 [score]; prt1: # = 1 | prt1-1-T",Solve x-1=4,"Seed: 200; ans1: 4 [score]; prt1: # = 0 | prt1-1-F","Seed: 200; ans1: 5 [score]; prt1: # = 1 | prt1-1-T"
,,,Finished,10,Solve x+2=5,"Seed: 101; ans1: 3 [score]; prt1: # = 1 | prt1-1-T","Seed: 101; ans1: 3 [score]; prt1: # = 1 | prt1-1-T",Solve x-1=4,"Seed: 201; ans1: 5 [score]; prt1: # = 1 | prt1-1-T","Seed: 201; ans1: 5 [score]; prt1: # = 1 | prt1-1-T"
"""


def test_detects_stack_response_export() -> None:
    dataset = (
        HistoricalStackResponseImporter()
        .import_text(
            source_name=(
                "example-responses.csv"
            ),
            csv_text=CSV_TEXT,
        )
    )

    assert dataset.question_count == 2

    assert dataset.attempt_count == 2

    assert len(
        dataset.attempts
    ) == 4


def test_extracts_seed_and_answer() -> None:
    dataset = (
        HistoricalStackResponseImporter()
        .import_text(
            source_name=(
                "example-responses.csv"
            ),
            csv_text=CSV_TEXT,
        )
    )

    attempt = dataset.attempts[0]

    assert attempt.seed == 100

    assert attempt.submitted_answers == (
        (
            "ans1",
            "3",
        ),
    )


def test_extracts_prt_score_and_notes() -> None:
    dataset = (
        HistoricalStackResponseImporter()
        .import_text(
            source_name=(
                "example-responses.csv"
            ),
            csv_text=CSV_TEXT,
        )
    )

    attempt = dataset.attempts[0]

    assert len(
        attempt.prts
    ) == 1

    assert attempt.prts[0].score == 1.0

    assert (
        attempt.prts[0]
        .answer_notes
        == (
            "prt1-1-T",
        )
    )


def test_computes_item_statistics() -> None:
    dataset = (
        HistoricalStackResponseImporter()
        .import_text(
            source_name=(
                "example-responses.csv"
            ),
            csv_text=CSV_TEXT,
        )
    )

    q1 = dataset.item_statistics[0]

    q2 = dataset.item_statistics[1]

    assert q1.question_number == 1

    assert q1.attempt_count == 2

    assert q1.mean_score == 1.0

    assert q1.full_credit_rate == 1.0

    assert q2.mean_score == 0.5

    assert q2.full_credit_rate == 0.5

    assert q2.zero_credit_rate == 0.5


def test_counts_historical_prt_paths() -> None:
    dataset = (
        HistoricalStackResponseImporter()
        .import_text(
            source_name=(
                "example-responses.csv"
            ),
            csv_text=CSV_TEXT,
        )
    )

    q2 = dataset.item_statistics[1]

    counts = dict(
        q2.prt_outcome_counts
    )

    assert counts[
        "prt1:prt1-1-F"
    ] == 1

    assert counts[
        "prt1:prt1-1-T"
    ] == 1


def test_does_not_retain_personal_identity_fields() -> None:
    dataset = (
        HistoricalStackResponseImporter()
        .import_text(
            source_name=(
                "example-responses.csv"
            ),
            csv_text=CSV_TEXT,
        )
    )

    attempt = dataset.attempts[0]

    assert not hasattr(
        attempt,
        "email"
    )

    assert not hasattr(
        attempt,
        "first_name"
    )

    assert not hasattr(
        attempt,
        "last_name"
    )


def test_non_response_csv_is_rejected() -> None:
    importer = (
        HistoricalStackResponseImporter()
    )

    with pytest.raises(
        ValueError,
    ):
        importer.import_text(
            source_name="questions.csv",
            csv_text=(
                "question_id,question,answer\n"
                "Q1,Solve x=1,1\n"
            ),
        )
