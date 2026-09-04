from types import SimpleNamespace

from fastapi.testclient import (
    TestClient,
)

import backend.app.api.adaptive_uploads as uploads_api

from backend.app.main import app


client = TestClient(
    app
)


class FakeService:
    def start(
        self,
        *,
        learner_id: int,
    ):
        return SimpleNamespace(
            learner_id=learner_id,
            question_id="Q1",
            title="Imported question",
            seed=123,
            html="<p>Question</p>",
            inputs={
                "ans1": {}
            },
            ability=0.0,
            decision_reason=(
                "Test decision"
            ),
            previous_score=None,
            previous_outcome=None,
        )


def test_upload_health() -> None:
    response = client.get(
        "/api/adaptive/uploads/health"
    )

    assert response.status_code == 200

    payload = response.json()

    assert ".xml" in (
        payload[
            "supported_formats"
        ]
    )

    assert ".xlsx" in (
        payload[
            "supported_formats"
        ]
    )

    assert ".xlsm" in (
        payload[
            "supported_formats"
        ]
    )

    assert ".csv" in (
        payload[
            "supported_formats"
        ]
    )

    assert ".docx" in (
        payload[
            "supported_formats"
        ]
    )

    assert ".pdf" in (
        payload[
            "supported_formats"
        ]
    )


def test_unsupported_upload_rejected() -> None:
    response = client.post(
        "/api/adaptive/uploads/sessions",
        data={
            "learner_id": "1"
        },
        files={
            "question_bank": (
                "questions.txt",
                b"Question",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


def test_xml_upload_starts_session(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        uploads_api,
        "_build_service",
        lambda **kwargs:
            FakeService(),
    )

    xml = b"""
    <quiz>
      <question type="stack">
        <name>
          <text>Question</text>
        </name>
        <idnumber>Q1</idnumber>
      </question>
    </quiz>
    """

    response = client.post(
        "/api/adaptive/uploads/sessions",
        data={
            "learner_id": "5"
        },
        files={
            "question_bank": (
                "questions.xml",
                xml,
                "application/xml",
            )
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload[
        "learner_id"
    ] == 5

    assert payload[
        "question_id"
    ] == "Q1"


def test_metadata_merge_instructor_wins() -> None:
    generated = """
    {
      "questions": {
        "Q1": {
          "difficulty": -0.5,
          "tags": [
            "algebra"
          ]
        }
      }
    }
    """

    instructor = """
    {
      "questions": {
        "Q1": {
          "difficulty": 1.0,
          "supports": [
            "sign_error"
          ]
        }
      }
    }
    """

    merged = (
        uploads_api._merge_metadata(
            generated_json=generated,
            instructor_json=(
                instructor
            ),
        )
    )

    assert merged is not None

    import json

    payload = json.loads(
        merged
    )

    q1 = payload[
        "questions"
    ][
        "Q1"
    ]

    assert q1[
        "difficulty"
    ] == 1.0

    assert q1[
        "tags"
    ] == [
        "algebra"
    ]

    assert q1[
        "supports"
    ] == [
        "sign_error"
    ]


def test_demo_page_accepts_all_formats() -> None:
    response = client.get(
        "/adaptive-demo"
    )

    assert response.status_code == 200

    assert ".xml" in response.text
    assert ".xlsx" in response.text
    assert ".xlsm" in response.text
    assert ".csv" in response.text
    assert ".docx" in response.text
    assert ".pdf" in response.text

    assert (
        "/api/adaptive/uploads/sessions"
        in response.text
    )


def test_historical_response_csv_is_detected() -> None:
    csv_text = (
        "Last name,First name,Email address,"
        "Question 1,Response 1,Right answer 1\n"
        "Example,Learner,example@example.com,"
        "Solve x+2=5,"
        "\"Seed: 100; "
        "ans1: 3 [score]; "
        "prt1: # = 1 | prt1-1-T\","
        "\"Seed: 100; "
        "ans1: 3 [score]; "
        "prt1: # = 1 | prt1-1-T\"\n"
        "Second,Learner,second@example.com,"
        "Solve x+2=5,"
        "\"Seed: 101; "
        "ans1: 2 [score]; "
        "prt1: # = 0 | prt1-1-F\","
        "\"Seed: 101; "
        "ans1: 3 [score]; "
        "prt1: # = 1 | prt1-1-T\"\n"
    )

    response = client.post(
        "/api/adaptive/uploads/sessions",
        data={
            "learner_id": "1"
        },
        files={
            "question_bank": (
                "example-responses.csv",
                csv_text.encode(
                    "utf-8"
                ),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload[
            "kind"
        ]
        == "historical_analysis"
    )

    assert (
        payload[
            "attempt_count"
        ]
        == 2
    )

    assert (
        payload[
            "question_count"
        ]
        == 1
    )

    item = payload[
        "items"
    ][0]

    assert item[
        "mean_score"
    ] == 0.5


def test_question_source_csv_still_starts_session(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        uploads_api,
        "_build_service",
        lambda **kwargs:
            FakeService(),
    )

    csv_text = (
        "question_id,question,answer,difficulty\n"
        "Q20,Solve x+3=8,5,0.0\n"
    )

    response = client.post(
        "/api/adaptive/uploads/sessions",
        data={
            "learner_id": "20"
        },
        files={
            "question_bank": (
                "questions.csv",
                csv_text.encode(
                    "utf-8"
                ),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload[
            "kind"
        ]
        == "adaptive_session"
    )

    assert (
        payload[
            "learner_id"
        ]
        == 20
    )


def test_historical_response_hides_identity() -> None:
    csv_text = (
        "Last name,First name,Email address,"
        "Question 1,Response 1,Right answer 1\n"
        "SecretSurname,SecretName,"
        "secret@example.com,"
        "Solve x=1,"
        "\"Seed: 1; "
        "ans1: 1 [score]; "
        "prt1: # = 1 | prt1-1-T\","
        "\"Seed: 1; "
        "ans1: 1 [score]; "
        "prt1: # = 1 | prt1-1-T\"\n"
    )

    response = client.post(
        "/api/adaptive/uploads/sessions",
        data={
            "learner_id": "1"
        },
        files={
            "question_bank": (
                "responses.csv",
                csv_text.encode(
                    "utf-8"
                ),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    body = response.text

    assert (
        "SecretSurname"
        not in body
    )

    assert (
        "SecretName"
        not in body
    )

    assert (
        "secret@example.com"
        not in body
    )
