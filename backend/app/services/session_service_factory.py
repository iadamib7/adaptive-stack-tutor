from pathlib import Path

from backend.app.integrations.stack_api.adapter import (
    StackEvaluationAdapter,
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


def build_stack_session_service() -> tuple[
    StackAdaptiveSessionService,
    MockStackEvaluationClient,
]:
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

    stack_client = MockStackEvaluationClient()

    stack_adapter = StackEvaluationAdapter(
        client=stack_client
    )

    service = StackAdaptiveSessionService(
        stack_adapter=stack_adapter,
        session_engine=session_engine,
    )

    return service, stack_client


session_service, stack_client = (
    build_stack_session_service()
)
