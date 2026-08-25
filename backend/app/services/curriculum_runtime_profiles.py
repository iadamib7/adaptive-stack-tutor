from pathlib import Path


from backend.app.services.session_service_factory import (
    PROJECT_ROOT,
)


class CurriculumRuntimeProfile:
    def __init__(
        self,
        *,
        profile_id: str,
        display_name: str,
        mapping_path: Path,
        knowledge_graph_path: Path,
        stack_export_path: Path,
        generated_question_directory: Path,
        starting_concept_id: str,
        use_shared_knowledge_graph: bool,
        additional_generated_directories: (
            tuple[Path, ...]
        ) = (),
    ) -> None:
        self.profile_id = profile_id
        self.display_name = display_name
        self.mapping_path = mapping_path
        self.knowledge_graph_path = (
            knowledge_graph_path
        )
        self.stack_export_path = (
            stack_export_path
        )
        self.generated_question_directory = (
            generated_question_directory
        )
        self.additional_generated_directories = (
            additional_generated_directories
        )
        self.starting_concept_id = (
            starting_concept_id
        )

        self.use_shared_knowledge_graph = (
            use_shared_knowledge_graph
        )


SHARED_KNOWLEDGE_GRAPH_PATH = (
    PROJECT_ROOT
    / "resources"
    / "knowledge_graph"
    / "grade9_grade10_transition.json"
)


KENYA_GRADE9_EXPORT_PATH = (
    PROJECT_ROOT
    / "resources"
    / "raw"
    / "kenya"
    / "grade9"
    / "grade9_questions.xml"
)


KENYA_GRADE9_GENERATED_DIRECTORY = (
    PROJECT_ROOT
    / "resources"
    / "generated"
    / "kenya"
    / "grade9"
    / "questions"
)


GHANA_BASIC9_GENERATED_DIRECTORY = (
    PROJECT_ROOT
    / "resources"
    / "generated"
    / "ghana"
    / "basic9"
    / "questions"
)


SHARED_LINEAR_RELATIONS_DIRECTORY = (
    PROJECT_ROOT
    / "resources"
    / "generated"
    / "shared"
    / "linear_relations"
)


KENYA_GRADE9_PROFILE = (
    CurriculumRuntimeProfile(
        profile_id=(
            "kenya-grade9-development"
        ),
        display_name=(
            "Kenya Grade 9 Development"
        ),
        mapping_path=(
            PROJECT_ROOT
            / "examples"
            / "curriculum_mapping"
            / (
                "kenya_grade9_"
                "integer_operations.json"
            )
        ),
        knowledge_graph_path=(
            SHARED_KNOWLEDGE_GRAPH_PATH
        ),
        stack_export_path=(
            KENYA_GRADE9_EXPORT_PATH
        ),
        generated_question_directory=(
            KENYA_GRADE9_GENERATED_DIRECTORY
        ),
        additional_generated_directories=(
            SHARED_LINEAR_RELATIONS_DIRECTORY,
        ),
        starting_concept_id=(
            "KE-G9-INTEGER-OPERATIONS"
        ),
        use_shared_knowledge_graph=False,
    )
)


GHANA_BASIC9_PROFILE = (
    CurriculumRuntimeProfile(
        profile_id=(
            "ghana-basic9-mathematics"
        ),
        display_name=(
            "Ghana Basic 9 Mathematics"
        ),
        mapping_path=(
            PROJECT_ROOT
            / "examples"
            / "curriculum_mapping"
            / (
                "ghana_basic9_"
                "linear_readiness.json"
            )
        ),
        knowledge_graph_path=(
            SHARED_KNOWLEDGE_GRAPH_PATH
        ),

        # The first Ghana pilot intentionally reuses
        # validated STACK questions from the existing
        # Grade 9 export. Curriculum alignment and
        # question source are separate concerns.
        stack_export_path=(
            KENYA_GRADE9_EXPORT_PATH
        ),
        generated_question_directory=(
            GHANA_BASIC9_GENERATED_DIRECTORY
        ),
        additional_generated_directories=(
            SHARED_LINEAR_RELATIONS_DIRECTORY,
        ),
        starting_concept_id=(
            "coordinate-graphs"
        ),
        use_shared_knowledge_graph=True,
    )
)


DEFAULT_CURRICULUM_PROFILE_ID = (
    "kenya-grade9-development"
)


CURRICULUM_RUNTIME_PROFILES = {
    profile.profile_id: profile
    for profile in (
        KENYA_GRADE9_PROFILE,
        GHANA_BASIC9_PROFILE,
    )
}


def get_curriculum_runtime_profile(
    profile_id: str,
) -> CurriculumRuntimeProfile:
    profile = (
        CURRICULUM_RUNTIME_PROFILES.get(
            profile_id
        )
    )

    if profile is None:
        available = ", ".join(
            sorted(
                CURRICULUM_RUNTIME_PROFILES
            )
        )

        raise ValueError(
            "Unknown curriculum profile "
            f"'{profile_id}'. "
            f"Available profiles: {available}."
        )

    return profile
