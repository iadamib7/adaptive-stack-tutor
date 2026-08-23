from pathlib import Path

from backend.app.content.models import (
    ContentDifficulty,
    ContentKind,
    ContentSource,
    LearningContentItem,
    LicenseDecision,
)
from backend.app.content.repository import (
    LearningContentRepository,
)
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
from backend.app.learning.adaptive_pathway.adapter import (
    AdaptivePathwayDecisionAdapter,
)
from backend.app.learning.adaptive_pathway.content_selector import (
    AdaptiveContentSelector,
)
from backend.app.learning.adaptive_pathway.policy import (
    AdaptivePathwayPolicy,
)
from backend.app.learning.adaptive_pathway.selector import (
    AdaptiveConceptSelector,
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
from backend.app.learning.knowledge_graph.models import (
    ConceptDifficultyBand,
    KnowledgeConcept,
)
from backend.app.learning.knowledge_graph.repository import (
    KnowledgeGraphRepository,
)
from backend.app.learning.session.engine import (
    AdaptiveLearningSessionEngine,
)
from backend.app.services.stack_adaptive_session_service import (
    StackAdaptiveSessionService,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_MAPPING_PATH = (
    PROJECT_ROOT
    / "examples"
    / "curriculum_mapping"
    / "kenya_grade9_integer_operations.json"
)


def _question_difficulty(
    *,
    role: str,
    required_for_mastery: bool,
) -> ContentDifficulty:
    if required_for_mastery:
        return ContentDifficulty.MASTERY

    if role == "foundation":
        return ContentDifficulty.FOUNDATION

    return ContentDifficulty.MEDIUM


def _build_live_pathway(
    curriculum_map,
    knowledge_graph: (
        KnowledgeGraphRepository | None
    ) = None,
) -> tuple[
    AdaptivePathwayPolicy,
    AdaptivePathwayDecisionAdapter,
]:
    concepts: list[KnowledgeConcept] = []
    content_items: list[
        LearningContentItem
    ] = []

    for mapping in curriculum_map.mappings:
        concepts.append(
            KnowledgeConcept(
                concept_id=(
                    mapping.concept_id
                ),
                name=mapping.concept_name,
                domain="Mathematics",
                strand=mapping.strand,
                level_id=mapping.level_id,
                description=(
                    mapping.learning_outcome
                ),
                difficulty_band=(
                    ConceptDifficultyBand.DEVELOPING
                ),
                prerequisite_concept_ids=tuple(
                    mapping.prerequisite_concept_ids
                ),
                remediation_concept_ids=tuple(
                    mapping.prerequisite_concept_ids
                ),
                extension_concept_ids=tuple(
                    mapping.next_concept_ids
                ),
                mastery_threshold=0.75,
                recommended_question_count=max(
                    1,
                    len(mapping.questions),
                ),
                curriculum_tags=(
                    mapping.curriculum_profile_id,
                    mapping.sub_strand,
                ),
            )
        )

        ordered_questions = sorted(
            mapping.questions,
            key=lambda question: (
                question.sequence_order,
                question.question_id,
            ),
        )

        for question in ordered_questions:
            content_items.append(
                LearningContentItem(
                    content_id=(
                        question.question_id
                    ),
                    concept_id=(
                        mapping.concept_id
                    ),
                    title=(
                        question.question_name
                    ),
                    kind=ContentKind.QUESTION,
                    source=ContentSource.STACK,
                    source_reference=(
                        question.source_file
                    ),
                    difficulty=(
                        _question_difficulty(
                            role=question.role.value,
                            required_for_mastery=(
                                question
                                .required_for_mastery
                            ),
                        )
                    ),
                    license_code=(
                        "existing-stack-bank"
                    ),
                    license_decision=(
                        LicenseDecision.ALLOWED
                    ),
                    attribution=(
                        "Existing Innodems STACK "
                        "question-bank item."
                    ),
                    is_mastery_evidence=(
                        question.required_for_mastery
                    ),
                    active=True,
                )
            )

    if knowledge_graph is None:
        knowledge_graph = (
            KnowledgeGraphRepository(
                concepts
            )
        )

    content_repository = (
        LearningContentRepository(
            content_items
        )
    )

    deliverable_concept_ids = {
        item.concept_id
        for item
        in content_repository.all_items()
        if item.can_be_delivered
    }

    concept_selector = (
        AdaptiveConceptSelector(
            knowledge_graph,
            deliverable_concept_ids=(
                deliverable_concept_ids
            ),
        )
    )

    content_selector = (
        AdaptiveContentSelector(
            content_repository
        )
    )

    pathway_policy = (
        AdaptivePathwayPolicy(
            concept_selector=(
                concept_selector
            ),
            content_selector=(
                content_selector
            ),
        )
    )

    pathway_adapter = (
        AdaptivePathwayDecisionAdapter(
            knowledge_graph=(
                knowledge_graph
            )
        )
    )

    return (
        pathway_policy,
        pathway_adapter,
    )


def build_stack_session_service(
    stack_client: StackEvaluationClient,
    knowledge_graph: (
        KnowledgeGraphRepository | None
    ) = None,
    mapping_path: Path | None = None,
) -> StackAdaptiveSessionService:
    """
    Build the live deterministic adaptive learning
    architecture from the validated curriculum mapping.
    """

    active_mapping_path = (
        mapping_path
        or DEFAULT_MAPPING_PATH
    )

    curriculum_map = (
        load_curriculum_question_map(
            active_mapping_path
        )
    )

    mapping_repository = (
        CurriculumMappingRepository(
            curriculum_map
        )
    )

    evidence_tracker = (
        ConceptEvidenceTracker(
            mapping_repository=(
                mapping_repository
            )
        )
    )

    decision_engine = (
        ConceptDecisionEngine(
            mapping_repository=(
                mapping_repository
            ),
            evidence_tracker=(
                evidence_tracker
            ),
        )
    )

    (
        pathway_policy,
        pathway_adapter,
    ) = _build_live_pathway(
        curriculum_map,
        knowledge_graph=knowledge_graph,
    )

    session_engine = (
        AdaptiveLearningSessionEngine(
            evidence_tracker=(
                evidence_tracker
            ),
            decision_engine=(
                decision_engine
            ),
            pathway_policy=(
                pathway_policy
            ),
            pathway_adapter=(
                pathway_adapter
            ),
        )
    )

    stack_adapter = StackEvaluationAdapter(
        client=stack_client
    )

    return StackAdaptiveSessionService(
        stack_adapter=stack_adapter,
        session_engine=session_engine,
    )


def build_mock_stack_session_service(
    mapping_path: Path | None = None,
    knowledge_graph: (
        KnowledgeGraphRepository | None
    ) = None,
) -> tuple[
    StackAdaptiveSessionService,
    MockStackEvaluationClient,
]:
    stack_client = MockStackEvaluationClient()

    service = build_stack_session_service(
        stack_client=stack_client,
        knowledge_graph=knowledge_graph,
        mapping_path=mapping_path,
    )

    return service, stack_client


def build_live_stack_session_service(
    base_url: str = "http://localhost:3080",
    timeout_seconds: int = 120,
    mapping_path: Path | None = None,
    knowledge_graph: (
        KnowledgeGraphRepository | None
    ) = None,
) -> StackAdaptiveSessionService:
    stack_client = HttpStackEvaluationClient(
        base_url=base_url,
        timeout_seconds=timeout_seconds,
    )

    return build_stack_session_service(
        stack_client=stack_client,
        knowledge_graph=knowledge_graph,
        mapping_path=mapping_path,
    )


# Development API service.
session_service, stack_client = (
    build_mock_stack_session_service()
)
