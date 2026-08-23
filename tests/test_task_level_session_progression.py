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
from backend.app.learning.session.models import (
    ScoredStackOutcome,
)
from backend.app.services.stack_adaptive_session_service import (
    StackAdaptiveSessionService,
)


class FakeSessionEngine:
    def __init__(self) -> None:
        self.session = None
        self.submitted = []

    def get_session(
        self,
        student_id: int,
    ):
        return self.session

    def submit_outcome(
        self,
        outcome,
    ):
        self.submitted.append(
            outcome
        )

        return "submitted"


def test_submit_outcome_is_separate_from_evaluation() -> None:
    engine = FakeSessionEngine()

    service = StackAdaptiveSessionService(
        stack_adapter=StackEvaluationAdapter(
            client=MockStackEvaluationClient()
        ),
        session_engine=engine,
    )

    outcome = ScoredStackOutcome(
        student_id=1,
        concept_id="concept",
        question_id="question",
        outcome_code="correct",
        score=1.0,
        stack_feedback=None,
    )

    result = service.submit_outcome(
        outcome
    )

    assert result == "submitted"

    assert engine.submitted == [
        outcome
    ]


def test_submit_outcome_does_not_regrade() -> None:
    engine = FakeSessionEngine()

    client = MockStackEvaluationClient()

    service = StackAdaptiveSessionService(
        stack_adapter=StackEvaluationAdapter(
            client=client
        ),
        session_engine=engine,
    )

    outcome = ScoredStackOutcome(
        student_id=1,
        concept_id="concept",
        question_id="question",
        outcome_code="correct",
        score=1.0,
        stack_feedback=None,
    )

    service.submit_outcome(
        outcome
    )

    assert client.requests == []
