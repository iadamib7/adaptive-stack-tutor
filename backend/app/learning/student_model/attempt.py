from pydantic import BaseModel


class Attempt(BaseModel):
    student_id: int

    question_id: int

    concept: str

    correct: bool

    response: str