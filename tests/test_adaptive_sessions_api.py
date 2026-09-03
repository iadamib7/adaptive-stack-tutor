from fastapi.testclient import (
    TestClient,
)

from backend.app.main import app


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
