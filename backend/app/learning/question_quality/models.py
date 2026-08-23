from enum import Enum

from pydantic import BaseModel


class QualityStatus(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    FAIL = "FAIL"


class QualityCheck(BaseModel):
    name: str
    status: QualityStatus
    message: str


class QuestionQualityReport(BaseModel):
    question_id: str

    deployment: QualityCheck
    rendering: QualityCheck
    grading: QualityCheck

    mathematical_quality: QualityCheck
    educational_quality: QualityCheck

    overall_status: QualityStatus
