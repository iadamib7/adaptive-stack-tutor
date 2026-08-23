from __future__ import annotations

from pydantic import BaseModel, Field


class AdaptiveTask(BaseModel):
    """
    One learner-facing mathematical task.

    A task may contain multiple answer fields when those
    fields form one mathematical response.
    """

    task_id: str = Field(
        min_length=1,
    )

    source_question_id: str = Field(
        min_length=1,
    )

    display_order: int = Field(
        ge=1,
    )

    prompt_template: str = Field(
        min_length=1,
    )

    input_names: list[str] = Field(
        min_length=1,
    )

    prt_names: list[str] = Field(
        min_length=1,
    )

    part_label: str | None = None


class AdaptiveQuestionTasks(BaseModel):
    source_question_id: str = Field(
        min_length=1,
    )

    introduction_template: str = ""

    tasks: list[AdaptiveTask] = Field(
        min_length=1,
    )

    @property
    def is_multi_part(self) -> bool:
        return len(self.tasks) > 1

    @property
    def task_count(self) -> int:
        return len(self.tasks)
