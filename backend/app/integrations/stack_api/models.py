from pydantic import BaseModel, Field


class StackPRTResult(BaseModel):
    prt_name: str = Field(min_length=1)

    score: float | None = Field(
        default=None,
        ge=0.0,
    )

    penalty: float | None = Field(
        default=None,
        ge=0.0,
    )

    answer_notes: list[str] = Field(
        default_factory=list,
    )

    feedback: str | None = None

    errors: list[str] = Field(
        default_factory=list,
    )


class NormalizedStackResult(BaseModel):
    question_id: str = Field(min_length=1)

    valid: bool
    seed: int | None = None

    overall_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    prts: list[StackPRTResult] = Field(
        default_factory=list,
    )

    validation_errors: list[str] = Field(
        default_factory=list,
    )

    raw_feedback: str | None = None

    @property
    def total_score(self) -> float:
        return sum(
            prt.score
            for prt in self.prts
            if prt.score is not None
        )

    @property
    def total_penalty(self) -> float:
        return sum(
            prt.penalty
            for prt in self.prts
            if prt.penalty is not None
        )

    @property
    def answer_notes(self) -> list[str]:
        return [
            note
            for prt in self.prts
            for note in prt.answer_notes
        ]

    @property
    def errors(self) -> list[str]:
        return [
            *self.validation_errors,
            *[
                error
                for prt in self.prts
                for error in prt.errors
            ],
        ]


class StackEvaluationRequest(BaseModel):
    question_id: str = Field(min_length=1)

    question_xml: str = Field(min_length=1)

    student_answers: dict[str, str] = Field(
        min_length=1,
    )

    seed: int | None = None
