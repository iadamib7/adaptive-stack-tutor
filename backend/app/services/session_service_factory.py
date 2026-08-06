from pathlib import Path

from backend.app.integrations.stack_api.adapter import (
    StackEvaluationAdapter,
)
from backend.app.integrations.stack_api.client import (
    StackEvaluationClient,
)
from backend.app.integrations.stack_api.http_client import (
    HttpStackEvaluationClient,
)
from backend.app.integrations.stack_api.mock_client import (
    MockStackEvaluationClient,
)
from backend.app.learning.concept_decision.engine import (
    ConceptDecisionEngine,
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


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MAPPING_PATH = (
    PROJECT_ROOT
    / "examples"
    / "curriculum_mapping"
    / "kenya_grade9_integer_operations.json"
)


def build_stack_session_service(
    stack_client: StackEvaluationClient,
) -> StackAdaptiveSessionService:
    """
    Build the adaptive session service around any STACK client.

    Tests and development endpoints may inject the mock client.
    The running live application can inject the HTTP client.
    """

    curriculum_map = load_curriculum_question_map(
        MAPPING_PATH
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

    stack_adapter = StackEvaluationAdapter(
        client=stack_client
    )

    return StackAdaptiveSessionService(
        stack_adapter=stack_adapter,
        session_engine=session_engine,
    )


def build_mock_stack_session_service() -> tuple[
    StackAdaptiveSessionService,
    MockStackEvaluationClient,
]:
    stack_client = MockStackEvaluationClient()

    service = build_stack_session_service(
        stack_client=stack_client
    )

    return service, stack_client


def build_live_stack_session_service(
    base_url: str = "http://localhost:3080",
    timeout_seconds: int = 120,
) -> StackAdaptiveSessionService:
    stack_client = HttpStackEvaluationClient(
        base_url=base_url,
        timeout_seconds=timeout_seconds,
    )

    return build_stack_session_service(
        stack_client=stack_client
    )


# Keep the current development API on the mock service until
# its request schema stops accepting fabricated STACK results.
session_service, stack_client = (
    build_mock_stack_session_service()
)
