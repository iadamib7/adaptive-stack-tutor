from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationResult:
    correct: bool
    student_answer: str
    expected_answer: str
    error_message: str | None = None