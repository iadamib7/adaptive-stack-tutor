from backend.app.services.curriculum_runtime_profiles import (
    DEFAULT_CURRICULUM_PROFILE_ID,
    get_curriculum_runtime_profile,
)


class ActiveCurriculumRegistry:
    def __init__(self) -> None:
        self._profiles_by_student: dict[
            int,
            str,
        ] = {}

    def assign(
        self,
        *,
        student_id: int,
        profile_id: str,
    ) -> str:
        if student_id <= 0:
            raise ValueError(
                "Student ID must be positive."
            )

        profile = (
            get_curriculum_runtime_profile(
                profile_id
            )
        )

        self._profiles_by_student[
            student_id
        ] = profile.profile_id

        return profile.profile_id

    def get(
        self,
        student_id: int,
    ) -> str | None:
        return self._profiles_by_student.get(
            student_id
        )

    def get_or_default(
        self,
        student_id: int,
    ) -> str:
        profile_id = self.get(
            student_id
        )

        if profile_id is not None:
            return profile_id

        return DEFAULT_CURRICULUM_PROFILE_ID

    def clear(
        self,
        student_id: int,
    ) -> None:
        self._profiles_by_student.pop(
            student_id,
            None,
        )

    def snapshot(
        self,
        student_id: int,
    ) -> str | None:
        return self.get(
            student_id
        )

    def restore(
        self,
        student_id: int,
        profile_id: str | None,
    ) -> None:
        if profile_id is None:
            self.clear(
                student_id
            )
            return

        self.assign(
            student_id=student_id,
            profile_id=profile_id,
        )


active_curriculum_registry = (
    ActiveCurriculumRegistry()
)
