from backend.app.services.active_curriculum_registry import (
    ActiveCurriculumRegistry,
    active_curriculum_registry,
)
from backend.app.services.curriculum_runtime_profiles import (
    CURRICULUM_RUNTIME_PROFILES,
    DEFAULT_CURRICULUM_PROFILE_ID,
    get_curriculum_runtime_profile,
)
from backend.app.services.live_session_factory import (
    CurriculumRuntimeBundle,
    build_curriculum_runtime_bundle,
)


class CurriculumRuntimeResolver:
    def __init__(
        self,
        registry: ActiveCurriculumRegistry,
    ) -> None:
        self.registry = registry

        self._bundles: dict[
            str,
            CurriculumRuntimeBundle,
        ] = {}

    def get_bundle(
        self,
        profile_id: str,
    ) -> CurriculumRuntimeBundle:
        get_curriculum_runtime_profile(
            profile_id
        )

        existing = self._bundles.get(
            profile_id
        )

        if existing is not None:
            return existing

        bundle = (
            build_curriculum_runtime_bundle(
                profile_id
            )
        )

        self._bundles[
            profile_id
        ] = bundle

        return bundle

    def get_bundle_for_student(
        self,
        student_id: int,
    ) -> CurriculumRuntimeBundle:
        profile_id = (
            self.registry.get_or_default(
                student_id
            )
        )

        return self.get_bundle(
            profile_id
        )

    def assign_and_get_bundle(
        self,
        *,
        student_id: int,
        profile_id: str,
    ) -> CurriculumRuntimeBundle:
        assigned_profile_id = (
            self.registry.assign(
                student_id=student_id,
                profile_id=profile_id,
            )
        )

        return self.get_bundle(
            assigned_profile_id
        )

    def preload_all(
        self,
    ) -> None:
        for profile_id in (
            CURRICULUM_RUNTIME_PROFILES
        ):
            self.get_bundle(
                profile_id
            )


curriculum_runtime_resolver = (
    CurriculumRuntimeResolver(
        registry=active_curriculum_registry
    )
)
