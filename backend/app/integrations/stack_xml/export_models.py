from pydantic import BaseModel, Field


class StackPRTOutcome(BaseModel):
    prt_name: str = Field(min_length=1)
    node_name: str = Field(min_length=1)
    branch: str = Field(pattern="^[TF]$")

    outcome_code: str = Field(min_length=1)
    answer_test: str | None = None
    description: str | None = None

    score: float | None = None
    next_node: str | None = None
    feedback: str | None = None

    @property
    def exits_tree(self) -> bool:
        return self.next_node is None


class StackQuestionInventoryItem(BaseModel):
    source_file: str = Field(min_length=1)
    source_question_id: str | None = None
    question_name: str = Field(min_length=1)

    category_path: list[str] = Field(default_factory=list)
    input_names: list[str] = Field(default_factory=list)

    prt_names: list[str] = Field(default_factory=list)
    prt_count: int = Field(ge=0)
    node_count: int = Field(ge=0)

    outcomes: list[StackPRTOutcome] = Field(
        default_factory=list,
    )

    simple_single_prt: bool = False

    # This remains blank until the curriculum-mapping stage.
    curriculum_concept_id: str | None = None


class StackQuestionInventory(BaseModel):
    version: str = "1.0"
    profile_id: str = Field(min_length=1)
    source_file: str = Field(min_length=1)

    question_count: int = Field(ge=0)
    questions: list[StackQuestionInventoryItem] = Field(
        default_factory=list,
    )
