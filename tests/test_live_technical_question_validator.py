from backend.app.learning.question_quality.live_technical_validator import (
    LiveTechnicalQuestionValidator,
)
from backend.app.learning.question_quality.models import (
    QualityStatus,
)


QUESTION_XML = """
<quiz>
  <question type="stack">
    <deployedseed>12345</deployedseed>
  </question>
</quiz>
""".strip()


class FakeResponse:
    def __init__(
        self,
        payload: object,
        ok: bool = True,
    ) -> None:
        self.payload = payload
        self.ok = ok

    def json(self) -> object:
        return self.payload


class FakeSession:
    def __init__(
        self,
        render_payload: dict | None = None,
        grade_payload: dict | None = None,
        render_ok: bool = True,
        grade_ok: bool = True,
    ) -> None:
        self.render_payload = (
            render_payload
            if render_payload is not None
            else {
                "questioninputs": {
                    "ans1": {
                        "samplesolution": {
                            "": "32"
                        }
                    }
                }
            }
        )

        self.grade_payload = (
            grade_payload
            if grade_payload is not None
            else {
                "isgradable": True,
                "prtresults": {
                    "prt1": {
                        "score": 1,
                        "answernotes": [
                            "prt1-1-T"
                        ],
                    }
                },
            }
        )

        self.render_ok = render_ok
        self.grade_ok = grade_ok

        self.requests: list[
            tuple[str, dict]
        ] = []

    def post(
        self,
        url: str,
        json: dict,
        timeout: int,
    ) -> FakeResponse:
        self.requests.append(
            (
                url,
                json,
            )
        )

        if url.endswith(
            "/render"
        ):
            return FakeResponse(
                self.render_payload,
                ok=self.render_ok,
            )

        return FakeResponse(
            self.grade_payload,
            ok=self.grade_ok,
        )


def test_live_question_passes() -> None:
    validator = (
        LiveTechnicalQuestionValidator(
            session=FakeSession()
        )
    )

    report = validator.validate(
        question_id="207582",
        question_xml=QUESTION_XML,
    )

    assert report.overall_status == (
        QualityStatus.PASS
    )

    assert report.deployment.status == (
        QualityStatus.PASS
    )

    assert report.rendering.status == (
        QualityStatus.PASS
    )

    assert report.grading.status == (
        QualityStatus.PASS
    )


def test_invalid_xml_fails() -> None:
    validator = (
        LiveTechnicalQuestionValidator(
            session=FakeSession()
        )
    )

    report = validator.validate(
        question_id="broken",
        question_xml="<quiz>",
    )

    assert report.overall_status == (
        QualityStatus.FAIL
    )


def test_missing_deployed_seed_fails() -> None:
    validator = (
        LiveTechnicalQuestionValidator(
            session=FakeSession()
        )
    )

    report = validator.validate(
        question_id="207582",
        question_xml=(
            "<quiz>"
            "<question type='stack'>"
            "</question>"
            "</quiz>"
        ),
    )

    assert report.deployment.status == (
        QualityStatus.FAIL
    )

    assert report.overall_status == (
        QualityStatus.FAIL
    )


def test_render_failure_fails() -> None:
    validator = (
        LiveTechnicalQuestionValidator(
            session=FakeSession(
                render_ok=False
            )
        )
    )

    report = validator.validate(
        question_id="207582",
        question_xml=QUESTION_XML,
    )

    assert report.rendering.status == (
        QualityStatus.FAIL
    )

    assert report.overall_status == (
        QualityStatus.FAIL
    )


def test_missing_sample_answer_fails_grading() -> None:
    session = FakeSession(
        render_payload={
            "questioninputs": {
                "ans1": {
                    "samplesolution": {}
                }
            }
        }
    )

    validator = (
        LiveTechnicalQuestionValidator(
            session=session
        )
    )

    report = validator.validate(
        question_id="207582",
        question_xml=QUESTION_XML,
    )

    assert report.grading.status == (
        QualityStatus.FAIL
    )


def test_missing_prt_result_fails() -> None:
    session = FakeSession(
        grade_payload={
            "isgradable": True,
            "prtresults": {},
        }
    )

    validator = (
        LiveTechnicalQuestionValidator(
            session=session
        )
    )

    report = validator.validate(
        question_id="207582",
        question_xml=QUESTION_XML,
    )

    assert report.overall_status == (
        QualityStatus.FAIL
    )


def test_sample_answer_is_sent_to_grade() -> None:
    session = FakeSession()

    validator = (
        LiveTechnicalQuestionValidator(
            session=session
        )
    )

    validator.validate(
        question_id="207582",
        question_xml=QUESTION_XML,
    )

    grade_requests = [
        request
        for request in session.requests
        if request[0].endswith(
            "/grade"
        )
    ]

    assert len(
        grade_requests
    ) == 1

    payload = grade_requests[0][1]

    assert payload["answers"] == {
        "ans1": "32"
    }

    assert payload["seed"] == 12345
