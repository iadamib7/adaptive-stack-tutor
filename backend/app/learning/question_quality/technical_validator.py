from backend.app.learning.question_quality.models import (
    QualityCheck,
    QualityStatus,
    QuestionQualityReport,
)


class TechnicalQuestionValidator:

    def validate(
        self,
        question_id: str,
        *,
        xml_valid: bool,
        deploy_successful: bool,
        render_successful: bool,
        grading_successful: bool,
        prt_successful: bool,
    ) -> QuestionQualityReport:

        deployment = QualityCheck(
            name="Deployment",
            status=(
                QualityStatus.PASS
                if deploy_successful
                else QualityStatus.FAIL
            ),
            message=(
                "Deployment succeeded."
                if deploy_successful
                else "Deployment failed."
            ),
        )

        rendering = QualityCheck(
            name="Rendering",
            status=(
                QualityStatus.PASS
                if render_successful
                else QualityStatus.FAIL
            ),
            message=(
                "Rendering succeeded."
                if render_successful
                else "Rendering failed."
            ),
        )

        grading = QualityCheck(
            name="Grading",
            status=(
                QualityStatus.PASS
                if grading_successful
                else QualityStatus.FAIL
            ),
            message=(
                "Grading succeeded."
                if grading_successful
                else "Grading failed."
            ),
        )

        if (
            xml_valid
            and deploy_successful
            and render_successful
            and grading_successful
            and prt_successful
        ):
            overall = QualityStatus.PASS
        else:
            overall = QualityStatus.FAIL

        return QuestionQualityReport(
            question_id=question_id,
            deployment=deployment,
            rendering=rendering,
            grading=grading,
            mathematical_quality=QualityCheck(
                name="Mathematics",
                status=QualityStatus.REVIEW,
                message=(
                    "Not evaluated by the "
                    "technical validator."
                ),
            ),
            educational_quality=QualityCheck(
                name="Education",
                status=QualityStatus.REVIEW,
                message=(
                    "Not evaluated by the "
                    "technical validator."
                ),
            ),
            overall_status=overall,
        )
