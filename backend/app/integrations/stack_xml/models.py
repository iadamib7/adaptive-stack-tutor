from pydantic import BaseModel, Field


class PRTBranch(BaseModel):
    branch: str = Field(pattern="^[TF]$")
    next_node: int | None = None

    @property
    def exits_tree(self) -> bool:
        return self.next_node is None


class PRTNode(BaseModel):
    number: int = Field(ge=1)
    true_branch: PRTBranch
    false_branch: PRTBranch


class PRTStructure(BaseModel):
    name: str = Field(min_length=1)
    nodes: list[PRTNode] = Field(default_factory=list)


class StackQuestionStructure(BaseModel):
    filename: str = Field(min_length=1)
    question_name: str = Field(min_length=1)
    prts: list[PRTStructure] = Field(default_factory=list)
