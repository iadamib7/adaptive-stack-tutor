from __future__ import annotations

from backend.app.learning.adaptive_tasks.extractor import (
    extract_adaptive_tasks,
)
from backend.app.learning.adaptive_tasks.models import (
    AdaptiveTask,
)
from backend.app.learning.adaptive_tasks.runtime_models import (
    AdaptiveTaskRuntimeState,
)
from backend.app.learning.adaptive_tasks.runtime_repository import (
    AdaptiveTaskRuntimeRepository,
)


class AdaptiveTaskRuntimeError(
    ValueError
):
    pass


class AdaptiveTaskRuntimeService:
    """
    Manage a learner's progress through the adaptive tasks
    extracted from one source STACK question.

    This service does not perform STACK grading.

    Grading integration will be added separately.
    """

    def __init__(
        self,
        repository: (
            AdaptiveTaskRuntimeRepository
            | None
        ) = None,
    ) -> None:
        self.repository = (
            repository
            if repository is not None
            else AdaptiveTaskRuntimeRepository()
        )

    def start(
        self,
        *,
        student_id: int,
        source_question_id: str,
        question_xml: str,
    ) -> AdaptiveTaskRuntimeState:
        extracted = extract_adaptive_tasks(
            question_id=(
                source_question_id
            ),
            question_xml=question_xml,
        )

        state = AdaptiveTaskRuntimeState(
            student_id=student_id,
            source_question_id=(
                source_question_id
            ),
            tasks=extracted.tasks,
            current_task_index=0,
            completed=False,
        )

        self.repository.save(
            state
        )

        return state

    def get_state(
        self,
        student_id: int,
    ) -> AdaptiveTaskRuntimeState | None:
        return self.repository.get(
            student_id
        )

    def get_current_task(
        self,
        student_id: int,
    ) -> AdaptiveTask:
        state = self._require_state(
            student_id
        )

        task = state.current_task

        if task is None:
            raise AdaptiveTaskRuntimeError(
                "The current source question "
                "has already been completed."
            )

        return task

    def advance(
        self,
        student_id: int,
    ) -> AdaptiveTaskRuntimeState:
        state = self._require_state(
            student_id
        )

        if state.completed:
            raise AdaptiveTaskRuntimeError(
                "The current source question "
                "has already been completed."
            )

        next_index = (
            state.current_task_index
            + 1
        )

        if next_index >= state.task_count:
            updated = state.model_copy(
                update={
                    "current_task_index":
                        state.task_count,
                    "completed":
                        True,
                }
            )

        else:
            updated = state.model_copy(
                update={
                    "current_task_index":
                        next_index,
                }
            )

        self.repository.save(
            updated
        )

        return updated

    def restart(
        self,
        student_id: int,
    ) -> AdaptiveTaskRuntimeState:
        state = self._require_state(
            student_id
        )

        restarted = state.model_copy(
            update={
                "current_task_index": 0,
                "completed": False,
            }
        )

        self.repository.save(
            restarted
        )

        return restarted

    def clear(
        self,
        student_id: int,
    ) -> None:
        self.repository.delete(
            student_id
        )

    def _require_state(
        self,
        student_id: int,
    ) -> AdaptiveTaskRuntimeState:
        state = self.repository.get(
            student_id
        )

        if state is None:
            raise AdaptiveTaskRuntimeError(
                "No adaptive task runtime "
                "exists for this student."
            )

        return state
