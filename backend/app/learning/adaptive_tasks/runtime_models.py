from __future__ import annotations

from pydantic import BaseModel, Field

from backend.app.learning.adaptive_tasks.models import (
    AdaptiveTask,
)


class AdaptiveTaskRuntimeState(BaseModel):
    """
    Runtime state for one learner working through the
    adaptive tasks extracted from one STACK source question.
    """

    student_id: int = Field(
        gt=0,
    )

    source_question_id: str = Field(
        min_length=1,
    )

    tasks: list[AdaptiveTask] = Field(
        min_length=1,
    )

    current_task_index: int = Field(
        default=0,
        ge=0,
    )

    completed: bool = False

    @property
    def task_count(self) -> int:
        return len(
            self.tasks
        )

    @property
    def current_task(
        self,
    ) -> AdaptiveTask | None:
        if self.completed:
            return None

        if self.current_task_index >= len(
            self.tasks
        ):
            return None

        return self.tasks[
            self.current_task_index
        ]

    @property
    def current_task_number(self) -> int:
        if self.completed:
            return len(
                self.tasks
            )

        return (
            self.current_task_index
            + 1
        )

    @property
    def has_next_task(self) -> bool:
        return (
            not self.completed
            and self.current_task_index
            + 1
            < len(self.tasks)
        )
