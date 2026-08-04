from enum import Enum

from pydantic import BaseModel


class ValidationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


class ValidationIssue(BaseModel):
    severity: ValidationSeverity
    code: str
    message: str
    question: str | None = None
    prt_name: str | None = None
    outcome_code: str | None = None


class ValidationReport(BaseModel):
    issues: list[ValidationIssue]

    @property
    def errors(self) -> list[ValidationIssue]:
        return [
            issue
            for issue in self.issues
            if issue.severity == ValidationSeverity.ERROR
        ]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [
            issue
            for issue in self.issues
            if issue.severity == ValidationSeverity.WARNING
        ]

    @property
    def is_valid(self) -> bool:
        return not self.errors
