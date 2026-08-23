from backend.app.learning.question_quality.models import (
    QualityStatus,
)
from backend.app.learning.question_quality.technical_validator import (
    TechnicalQuestionValidator,
)


def test_valid_question_passes() -> None:
    validator = TechnicalQuestionValidator()

    report = validator.validate(
        question_id="207582",
        xml_valid=True,
        deploy_successful=True,
        render_successful=True,
        grading_successful=True,
        prt_successful=True,
    )

    assert report.overall_status == (
        QualityStatus.PASS
    )


def test_failed_render_fails_report() -> None:
    validator = TechnicalQuestionValidator()

    report = validator.validate(
        question_id="207630",
        xml_valid=True,
        deploy_successful=True,
        render_successful=False,
        grading_successful=True,
        prt_successful=True,
    )

    assert report.rendering.status == (
        QualityStatus.FAIL
    )

    assert report.overall_status == (
        QualityStatus.FAIL
    )


def test_failed_prt_fails_report() -> None:
    validator = TechnicalQuestionValidator()

    report = validator.validate(
        question_id="999999",
        xml_valid=True,
        deploy_successful=True,
        render_successful=True,
        grading_successful=True,
        prt_successful=False,
    )

    assert report.overall_status == (
        QualityStatus.FAIL
    )
