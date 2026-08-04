from pathlib import Path

from backend.app.learning.sequencing.loader import (
    load_sequencing_map,
)
from backend.app.learning.sequencing.models import (
    NextQuestionOption,
    OutcomeRoute,
    PRTMapping,
    QuestionMapping,
    SequencingAction,
    SequencingMap,
)
from backend.app.learning.sequencing.validator import (
    SequencingMapValidator,
)


MAP_PATH = Path(
    "examples/integration_demo/sequencing_map.json"
)


def build_minimal_map() -> SequencingMap:
    return SequencingMap(
        version="1.0",
        start_question="Question_1.xml",
        halt_questions=["Question_2.xml"],
        questions={
            "Question_1.xml": QuestionMapping(
                prts={
                    "prt1": PRTMapping(
                        outcomes={
                            "prt-1-T": OutcomeRoute(
                                action=(
                                    SequencingAction.ADVANCE
                                ),
                                strategy="fixed",
                                reason="Advance to the next question.",
                                next_questions=[
                                    NextQuestionOption(
                                        file="Question_2.xml"
                                    )
                                ],
                            )
                        }
                    )
                }
            )
        },
    )


def test_valid_map_has_no_errors() -> None:
    report = SequencingMapValidator().validate(
        build_minimal_map()
    )

    assert report.is_valid is True
    assert report.errors == []


def test_example_map_is_valid() -> None:
    sequencing_map = load_sequencing_map(MAP_PATH)

    report = SequencingMapValidator().validate(
        sequencing_map
    )

    assert report.is_valid is True


def test_missing_start_mapping_is_reported() -> None:
    sequencing_map = build_minimal_map()
    sequencing_map.start_question = "Unknown.xml"

    report = SequencingMapValidator().validate(
        sequencing_map
    )

    assert any(
        issue.code == "missing_start_mapping"
        for issue in report.errors
    )


def test_unknown_target_is_reported() -> None:
    sequencing_map = build_minimal_map()

    route = sequencing_map.questions[
        "Question_1.xml"
    ].prts["prt1"].outcomes["prt-1-T"]

    route.next_questions[0].file = "Unknown.xml"

    report = SequencingMapValidator().validate(
        sequencing_map
    )

    assert any(
        issue.code == "unknown_target"
        for issue in report.errors
    )


def test_fixed_route_requires_one_target() -> None:
    sequencing_map = build_minimal_map()

    route = sequencing_map.questions[
        "Question_1.xml"
    ].prts["prt1"].outcomes["prt-1-T"]

    route.next_questions.append(
        NextQuestionOption(
            file="Question_2.xml"
        )
    )

    report = SequencingMapValidator().validate(
        sequencing_map
    )

    assert any(
        issue.code == "invalid_fixed_route"
        for issue in report.errors
    )


def test_missing_xml_file_is_reported(
    tmp_path: Path,
) -> None:
    sequencing_map = build_minimal_map()

    (tmp_path / "Question_1.xml").write_text(
        "<quiz />",
        encoding="utf-8",
    )

    report = SequencingMapValidator().validate(
        sequencing_map,
        question_directory=tmp_path,
    )

    assert any(
        issue.code == "missing_question_file"
        and issue.question == "Question_2.xml"
        for issue in report.errors
    )


def test_existing_xml_files_pass_validation(
    tmp_path: Path,
) -> None:
    sequencing_map = build_minimal_map()

    for filename in [
        "Question_1.xml",
        "Question_2.xml",
    ]:
        (tmp_path / filename).write_text(
            "<quiz />",
            encoding="utf-8",
        )

    report = SequencingMapValidator().validate(
        sequencing_map,
        question_directory=tmp_path,
    )

    assert report.is_valid is True


def test_unreachable_question_is_reported() -> None:
    sequencing_map = build_minimal_map()

    sequencing_map.questions[
        "Unused.xml"
    ] = QuestionMapping(
        prts={
            "prt1": PRTMapping(
                outcomes={
                    "prt-1-T": OutcomeRoute(
                        action=SequencingAction.HALT,
                        reason="End unused pathway.",
                    )
                }
            )
        }
    )

    report = SequencingMapValidator().validate(
        sequencing_map
    )

    assert any(
        issue.code == "unreachable_question"
        and issue.question == "Unused.xml"
        for issue in report.warnings
    )


def test_undeclared_cycle_is_reported() -> None:
    sequencing_map = build_minimal_map()

    sequencing_map.halt_questions = []

    sequencing_map.questions[
        "Question_2.xml"
    ] = QuestionMapping(
        prts={
            "prt1": PRTMapping(
                outcomes={
                    "prt-1-T": OutcomeRoute(
                        action=(
                            SequencingAction.RETURN_TO_DECISION
                        ),
                        strategy="fixed",
                        reason="Return to Question 1.",
                        next_questions=[
                            NextQuestionOption(
                                file="Question_1.xml"
                            )
                        ],
                        allow_loop=False,
                    )
                }
            )
        }
    )

    report = SequencingMapValidator().validate(
        sequencing_map
    )

    assert any(
        issue.code == "undeclared_cycle"
        for issue in report.errors
    )
