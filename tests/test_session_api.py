from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.session_service_factory import (
    session_service,
)


client = TestClient(app)

CONCEPT_ID = "KE-G9-INTEGER-OPERATIONS"


def test_start_session_endpoint() -> None:
    response = client.post(
        "/sessions/start",
        json={
            "student_id": 901,
            "concept_id": CONCEPT_ID,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["student_id"] == 901
    assert data["question"]["id"] == "207582"
    assert data["action"] == "start_foundation"


def test_submit_correct_answer_endpoint() -> None:
    client.post(
        "/sessions/start",
        json={
            "student_id": 902,
            "concept_id": CONCEPT_ID,
        },
    )

    response = client.post(
        "/sessions/submit-answer",
        json={
            "student_id": 902,
            "concept_id": CONCEPT_ID,
            "question_id": "207582",
            "student_answers": {
                "ans1": "25"
            },
            "prt_name": "prt1",
            "score": 1.0,
            "answer_note": "prt1-1-T",
            "feedback": (
                "Correct answer, well done."
            ),
            "penalty": 0.0,
            "seed": 123,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"]["id"] == "207596"
    assert data["progress"]["attempts"] == 1
    assert (
        data["progress"][
            "positive_evidence_count"
        ]
        == 1
    )


def test_submit_incorrect_answer_endpoint() -> None:
    client.post(
        "/sessions/start",
        json={
            "student_id": 903,
            "concept_id": CONCEPT_ID,
        },
    )

    response = client.post(
        "/sessions/submit-answer",
        json={
            "student_id": 903,
            "concept_id": CONCEPT_ID,
            "question_id": "207582",
            "student_answers": {
                "ans1": "10"
            },
            "prt_name": "prt1",
            "score": 0.0,
            "answer_note": "prt1-1-F",
            "feedback": (
                "Review integer addition."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"]["id"] == "207582"
    assert (
        data["progress"][
            "negative_evidence_count"
        ]
        == 1
    )


def test_get_existing_session_endpoint() -> None:
    client.post(
        "/sessions/start",
        json={
            "student_id": 904,
            "concept_id": CONCEPT_ID,
        },
    )

    response = client.get(
        "/sessions/904"
    )

    assert response.status_code == 200
    assert response.json()["student_id"] == 904


def test_get_unknown_session_returns_404() -> None:
    response = client.get(
        "/sessions/999999"
    )

    assert response.status_code == 404


def test_wrong_question_returns_400() -> None:
    client.post(
        "/sessions/start",
        json={
            "student_id": 905,
            "concept_id": CONCEPT_ID,
        },
    )

    response = client.post(
        "/sessions/submit-answer",
        json={
            "student_id": 905,
            "concept_id": CONCEPT_ID,
            "question_id": "207596",
            "student_answers": {
                "ans1": "20"
            },
            "prt_name": "prt1",
            "score": 1.0,
            "answer_note": "prt1-1-T",
        },
    )

    assert response.status_code == 400
    assert "does not match" in (
        response.json()["detail"]
    )
