from enum import Enum

from pydantic import BaseModel, Field


class SequencingAction(str, Enum):
    PRACTICE = "practice"
    ADVANCE = "advance"
    REMEDIATE = "remediate"
    REVIEW_PREREQUISITE = "review_prerequisite"
    RETURN_TO_DECISION = "return_to_decision"
    HALT = "halt"


class NextQuestionOption(BaseModel):
    file: str = Field(min_length=1)
    weight: float = Field(default=1.0, gt=0.0)


class OutcomeRoute(BaseModel):
    action: SequencingAction
    strategy: str = "fixed"
    reason: str = Field(min_length=1)
    next_questions: list[NextQuestionOption] = Field(
        default_factory=list,
    )
    allow_loop: bool = False
    max_visits: int | None = Field(default=None, ge=1)


class PRTMapping(BaseModel):
    outcomes: dict[str, OutcomeRoute]


class QuestionMapping(BaseModel):
    notes: str | None = None
    prts: dict[str, PRTMapping]


class SequencingMap(BaseModel):
    version: str = Field(min_length=1)
    start_question: str = Field(min_length=1)
    questions: dict[str, QuestionMapping]
    halt_questions: list[str] = Field(default_factory=list)


class SequencingDecision(BaseModel):
    source_question: str
    prt_name: str
    outcome_code: str

    action: SequencingAction
    next_question: str | None
    reason: str

    allow_loop: bool = False
    max_visits: int | None = None
