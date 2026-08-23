from backend.app.learning.question_quality.models import (
    QualityCheck,
    QualityStatus,
    QuestionQualityReport,
)


def test_report_can_be_created() -> None:
    report = QuestionQualityReport(
        question_id="207630",

        deployment=QualityCheck(
            name="Deployment",
            status=QualityStatus.PASS,
            message="OK",
        ),

        rendering=QualityCheck(
            name="Rendering",
            status=QualityStatus.PASS,
            message="OK",
        ),

        grading=QualityCheck(
            name="Grading",
            status=QualityStatus.PASS,
            message="OK",
        ),

        mathematical_quality=QualityCheck(
            name="Mathematics",
            status=QualityStatus.REVIEW,
            message="Ambiguous notation",
        ),

        educational_quality=QualityCheck(
            name="Education",
            status=QualityStatus.REVIEW,
            message="Needs review",
        ),

        overall_status=QualityStatus.REVIEW,
    )

    assert report.question_id == "207630"

    assert report.overall_status == (
        QualityStatus.REVIEW
    )


def test_status_values() -> None:
    assert QualityStatus.PASS == "PASS"
    assert QualityStatus.REVIEW == "REVIEW"
    assert QualityStatus.FAIL == "FAIL"
