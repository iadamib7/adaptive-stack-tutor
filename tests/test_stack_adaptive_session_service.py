from pathlib import Path

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
from backend.app.learning.concept_decision.engine import (
    ConceptDecisionEngine,
)
from backend.app.learning.concept_decision.models import (
    ConceptDecisionAction,
)
from backend.app.learning.concept_evidence.tracker import (
    ConceptEvidenceTracker,
)
from backend.app.learning.curriculum_mapping.loader import (
    load_curriculum_question_map,
)
from backend.app.learning.curriculum_mapping.repository import (
    CurriculumMappingRepository,
)
from backend.app.learning.session.engine import (
    AdaptiveLearningSessionEngine,
)
from backend.app.services.stack_adaptive_session_service import (
    StackAdaptiveSessionService,
)


MAP_PATH = Path(
    "examples/curriculum_mapping/"
    "kenya_grade9_integer_operations.json"
)

CONCEPT_ID = "KE-G9-INTEGER-OPERATIONS"


def correct_result(
    question_id: str,
) -> NormalizedStackResult:
    return NormalizedStackResult(
        question_id=question_id,
        valid=True,
        seed=123,
        prts=[
            StackPRTResult(
                prt_name="prt1",
                score=1.0,
                penalty=0.0,
                answer_notes=["prt1-1-T"],
                feedback=(
                    "Correct answer, well done."
                ),
            )
        ],
    )


def incorrect_result(
    question_id: str,
) -> NormalizedStackResult:
    return NormalizedStackResult(
        question_id=question_id,
        valid=True,
        seed=123,
        prts=[
            StackPRTResult(
                prt_name="prt1",
                score=0.0,
                penalty=0.0,
                answer_notes=["prt1-1-F"],
                feedback=(
                    "Review this integer operation."
                ),
            )
        ],
    )


def build_service(
    results: dict[
        str,
        NormalizedStackResult,
    ] | None = None,
) -> tuple[
    StackAdaptiveSessionService,
    MockStackEvaluationClient,
]:
    curriculum_map = load_curriculum_question_map(
        MAP_PATH
    )

    mapping_repository = CurriculumMappingRepository(
        curriculum_map
    )

    evidence_tracker = ConceptEvidenceTracker(
        mapping_repository=mapping_repository
    )

    decision_engine = ConceptDecisionEngine(
        mapping_repository=mapping_repository,
        evidence_tracker=evidence_tracker,
    )

    session_engine = AdaptiveLearningSessionEngine(
        evidence_tracker=evidence_tracker,
        decision_engine=decision_engine,
    )

    mock_client = MockStackEvaluationClient(
        results=results
    )

    stack_adapter = StackEvaluationAdapter(
        client=mock_client
    )

    service = StackAdaptiveSessionService(
        stack_adapter=stack_adapter,
        session_engine=session_engine,
    )

    return service, mock_client


def test_service_starts_curriculum_session() -> None:
    service, _ = build_service()

    session = service.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert session.action == (
        ConceptDecisionAction.START_FOUNDATION
    )

    assert session.question is not None
    assert session.question.id == "207582"


def test_correct_stack_answer_advances_session() -> None:
    service, client = build_service(
        {
            "207582": correct_result("207582"),
        }
    )

    service.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    session = service.submit_answer(
        student_id=1,
        concept_id=CONCEPT_ID,
        question_id="207582",
        question_xml="<question></question>",
        student_answers={
            "ans1": "25",
        },
    )

    assert session.action == (
        ConceptDecisionAction.TARGET_PRACTICE
    )

    assert session.question is not None
    assert session.question.id == "207596"

    assert session.progress.attempts == 1
    assert session.progress.positive_evidence_count == 1

    assert len(client.requests) == 1
    assert client.requests[0].student_answers == {
        "ans1": "25",
    }


def test_incorrect_stack_answer_targets_same_skill() -> None:
    service, _ = build_service(
        {
            "207582": incorrect_result(
                "207582"
            ),
        }
    )

    service.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    session = service.submit_answer(
        student_id=1,
        concept_id=CONCEPT_ID,
        question_id="207582",
        question_xml="<question></question>",
        student_answers={
            "ans1": "10",
        },
    )

    assert session.action == (
        ConceptDecisionAction.TARGET_PRACTICE
    )

    assert session.question is not None
    assert session.question.id == "207582"

    assert session.progress.negative_evidence_count == 1
    assert "Review" in session.feedback


def test_full_stack_flow_completes_concept() -> None:
    question_ids = [
        "207582",
        "207596",
        "207591",
        "207589",
        "207630",
    ]

    service, _ = build_service(
        {
            question_id: correct_result(
                question_id
            )
            for question_id in question_ids
        }
    )

    session = service.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    for question_id in question_ids:
        assert session.question is not None
        assert session.question.id == question_id

        session = service.submit_answer(
            student_id=1,
            concept_id=CONCEPT_ID,
            question_id=question_id,
            question_xml="<question></question>",
            student_answers={
                "ans1": "teacher-answer",
            },
        )

    assert session.action == (
        ConceptDecisionAction.COMPLETE_CONCEPT
    )

    assert session.session_complete is True
    assert session.progress.concept_mastered is True
    assert session.question is None


def test_service_requires_active_session() -> None:
    service, _ = build_service(
        {
            "207582": correct_result("207582"),
        }
    )

    with pytest.raises(
        ValueError,
        match="No active learning session",
    ):
        service.submit_answer(
            student_id=1,
            concept_id=CONCEPT_ID,
            question_id="207582",
            question_xml="<question></question>",
            student_answers={
                "ans1": "25",
            },
        )


def test_service_rejects_wrong_question() -> None:
    service, _ = build_service(
        {
            "207596": correct_result("207596"),
        }
    )

    service.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    with pytest.raises(
        ValueError,
        match="does not match",
    ):
        service.submit_answer(
            student_id=1,
            concept_id=CONCEPT_ID,
            question_id="207596",
            question_xml="<question></question>",
            student_answers={
                "ans1": "25",
            },
        )


def test_service_rejects_invalid_stack_result() -> None:
    invalid_result = NormalizedStackResult(
        question_id="207582",
        valid=False,
        validation_errors=[
            "Student input has invalid syntax.",
        ],
    )

    service, _ = build_service(
        {
            "207582": invalid_result,
        }
    )

    service.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    with pytest.raises(
        ValueError,
        match="invalid syntax",
    ):
        service.submit_answer(
            student_id=1,
            concept_id=CONCEPT_ID,
            question_id="207582",
            question_xml="<question></question>",
            student_answers={
                "ans1": "(",
            },
        )


def test_seed_is_forwarded_to_stack_client() -> None:
    service, client = build_service(
        {
            "207582": correct_result("207582"),
        }
    )

    service.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    service.submit_answer(
        student_id=1,
        concept_id=CONCEPT_ID,
        question_id="207582",
        question_xml="<question></question>",
        student_answers={
            "ans1": "25",
        },
        seed=98765,
    )

    assert len(client.requests) == 1
    assert client.requests[0].seed == 98765


def test_existing_session_can_be_retrieved() -> None:
    service, _ = build_service()

    started_session = service.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    stored_session = service.get_session(1)

    assert stored_session == started_session
