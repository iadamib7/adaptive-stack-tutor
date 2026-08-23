from __future__ import annotations

from backend.app.learning.adaptive_tasks.runtime_models import (
    AdaptiveTaskRuntimeState,
)


class AdaptiveTaskRuntimeRepository:
    """
    In-memory repository for adaptive task runtime state.

    A persistent implementation can replace this later
    without changing the runtime service interface.
    """

    def __init__(self) -> None:
        self._states: dict[
            int,
            AdaptiveTaskRuntimeState,
        ] = {}

    def save(
        self,
        state: AdaptiveTaskRuntimeState,
    ) -> None:
        self._states[
            state.student_id
        ] = state

    def get(
        self,
        student_id: int,
    ) -> AdaptiveTaskRuntimeState | None:
        return self._states.get(
            student_id
        )

    def delete(
        self,
        student_id: int,
    ) -> None:
        self._states.pop(
            student_id,
            None,
        )

    def clear(
        self,
    ) -> None:
        self._states.clear()

    def snapshot(
        self,
        student_id: int,
    ) -> AdaptiveTaskRuntimeState | None:
        state = self.get(
            student_id
        )

        if state is None:
            return None

        return state.model_copy(
            deep=True
        )

    def restore(
        self,
        student_id: int,
        state: AdaptiveTaskRuntimeState | None,
    ) -> None:
        if state is None:
            self.delete(
                student_id
            )
            return

        self.save(
            state.model_copy(
                deep=True
            )
        )
