from types import SimpleNamespace

from fastapi.testclient import (
    TestClient,
)

from backend.app.main import app

from backend.app.api.adaptive_sessions import (
    _build_response,
)


client = TestClient(
    app
)


def test_adaptive_health_route() -> None:
    response = client.get(
        "/api/adaptive/health"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "mode": (
            "curriculum-independent"
        ),
    }


def test_missing_session_returns_404() -> None:
    response = client.post(
        (
            "/api/adaptive/"
            "sessions/not-real/answers"
        ),
        json={
            "learner_id": 1,
            "answers": {
                "ans1": "1",
            },
        },
    )

    assert response.status_code == 404


def test_invalid_question_bank_returns_400() -> None:
    response = client.post(
        "/api/adaptive/sessions",
        json={
            "learner_id": 1,
            "question_bank_xml": (
                "<questions />"
            ),
        },
    )

    assert response.status_code == 400


def test_adaptive_route_is_registered() -> None:
    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    paths = response.json()[
        "paths"
    ]

    assert (
        "/api/adaptive/sessions"
        in paths
    )

    assert (
        "/api/adaptive/"
        "sessions/{session_id}/answers"
        in paths
    )


def test_app_description_matches_new_direction() -> None:
    description = (
        app.description.lower()
    )

    assert (
        "curriculum-independent"
        in description
    )


def test_adaptive_response_exposes_routing_fields(
) -> None:
    view = SimpleNamespace(
        learner_id=7,
        question_id="Q2",
        title="Sign support",
        seed=123,
        html="<p>Support</p>",
        inputs={},
        ability=-0.2,
        decision_reason=(
            "Diagnostic evidence triggered "
            "remediation."
        ),
        decision_type="remediate",
        return_target_question_id="Q1",
        previous_score=0.0,
        previous_outcome="sign_error",
    )

    response = _build_response(
        session_id="session-1",
        view=view,
    )

    assert (
        response.decision_type
        == "remediate"
    )

    assert (
        response.return_target_question_id
        == "Q1"
    )

    assert (
        response.previous_outcome
        == "sign_error"
    )


def test_adaptive_response_exposes_reassessment(
) -> None:
    view = SimpleNamespace(
        learner_id=7,
        question_id="Q1",
        title="Initial equation",
        seed=456,
        html="<p>Retry</p>",
        inputs={},
        ability=0.0,
        decision_reason=(
            "Remediation completed."
        ),
        decision_type="reassess",
        return_target_question_id="Q1",
        previous_score=1.0,
        previous_outcome="correct",
    )

    response = _build_response(
        session_id="session-2",
        view=view,
    )

    assert (
        response.decision_type
        == "reassess"
    )

    assert (
        response.question_id
        == "Q1"
    )

    assert (
        response.return_target_question_id
        == "Q1"
    )
