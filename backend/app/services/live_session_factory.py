from dataclasses import dataclass

from backend.app.learning.adaptive_tasks.presentation import (
    AdaptiveTaskPresentationService,
)
from backend.app.learning.adaptive_tasks.runtime import (
    AdaptiveTaskRuntimeService,
)
from backend.app.learning.knowledge_graph.loader import (
    load_knowledge_graph,
)
from backend.app.learning.knowledge_graph.repository import (
    KnowledgeGraphRepository,
)
from backend.app.services.curriculum_runtime_profiles import (
    DEFAULT_CURRICULUM_PROFILE_ID,
    CurriculumRuntimeProfile,
    get_curriculum_runtime_profile,
)
from backend.app.services.session_service_factory import (
    build_live_stack_session_service,
)
from backend.app.services.stack_adaptive_session_service import (
    StackAdaptiveSessionService,
)
from backend.app.services.stack_question_runtime_service import (
    StackQuestionRuntimeService,
)


@dataclass
class CurriculumRuntimeBundle:
    profile: CurriculumRuntimeProfile

    live_session_service: (
        StackAdaptiveSessionService
    )

    question_runtime_service: (
        StackQuestionRuntimeService
    )

    adaptive_task_runtime_service: (
        AdaptiveTaskRuntimeService
    )

    adaptive_task_presentation_service: (
        AdaptiveTaskPresentationService
    )


def build_curriculum_runtime_bundle(
    profile_id: str,
) -> CurriculumRuntimeBundle:
    profile = get_curriculum_runtime_profile(
        profile_id
    )

    concepts = load_knowledge_graph(
        profile.knowledge_graph_path
    )

    knowledge_graph = (
        KnowledgeGraphRepository(
            concepts
        )
    )

    live_service = (
        build_live_stack_session_service(
            mapping_path=profile.mapping_path,
            knowledge_graph=knowledge_graph,
        )
    )

    question_service = (
        StackQuestionRuntimeService(
            export_path=(
                profile.stack_export_path
            ),
            generated_directory=(
                profile
                .generated_question_directory
            ),
            additional_generated_directories=(
                profile
                .additional_generated_directories
            ),
        )
    )

    task_runtime_service = (
        AdaptiveTaskRuntimeService()
    )

    task_presentation_service = (
        AdaptiveTaskPresentationService(
            runtime_service=(
                task_runtime_service
            ),
        )
    )

    return CurriculumRuntimeBundle(
        profile=profile,
        live_session_service=live_service,
        question_runtime_service=(
            question_service
        ),
        adaptive_task_runtime_service=(
            task_runtime_service
        ),
        adaptive_task_presentation_service=(
            task_presentation_service
        ),
    )


default_runtime_bundle = (
    build_curriculum_runtime_bundle(
        DEFAULT_CURRICULUM_PROFILE_ID
    )
)


# --------------------------------------------------
# Backward-compatible default service aliases.
#
# Existing API code continues to use the Kenya
# development profile until explicit curriculum
# selection is wired into the live-session API.
# --------------------------------------------------

live_session_service = (
    default_runtime_bundle
    .live_session_service
)

question_runtime_service = (
    default_runtime_bundle
    .question_runtime_service
)

adaptive_task_runtime_service = (
    default_runtime_bundle
    .adaptive_task_runtime_service
)

adaptive_task_presentation_service = (
    default_runtime_bundle
    .adaptive_task_presentation_service
)
