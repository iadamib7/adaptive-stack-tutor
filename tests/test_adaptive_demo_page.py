from fastapi.testclient import (
    TestClient,
)

from backend.app.main import app


client = TestClient(
    app
)


def test_adaptive_demo_page_loads() -> None:
    response = client.get(
        "/adaptive-demo"
    )

    assert response.status_code == 200

    assert (
        "Adaptive STACK Tutor"
        in response.text
    )


def test_demo_uses_new_adaptive_api() -> None:
    response = client.get(
        "/adaptive-demo"
    )

    assert (
        "/api/adaptive/sessions"
        in response.text
    )


def test_demo_accepts_xml_and_metadata() -> None:
    response = client.get(
        "/adaptive-demo"
    )

    assert (
        'id="xmlFile"'
        in response.text
    )

    assert (
        'id="metadataFile"'
        in response.text
    )


def test_demo_hides_internal_adaptive_trace(
) -> None:
    response = client.get(
        "/adaptive-demo"
    )

    assert response.status_code == 200

    body = response.text

    assert (
        "Adaptive Path"
        not in body
    )

    assert (
        'id="adaptivePath"'
        not in body
    )

    assert (
        "adaptivePathEntries"
        not in body
    )

    assert (
        "recordAdaptivePath"
        not in body
    )

    assert (
        "renderAdaptivePath"
        not in body
    )


def test_demo_hides_internal_routing_fields(
) -> None:
    response = client.get(
        "/adaptive-demo"
    )

    assert response.status_code == 200

    body = response.text

    assert (
        "return_target_question_id"
        not in body
    )

    assert (
        "previous_outcome"
        not in body
    )

    # decision_type is still used internally by the
    # learner page to choose a normal learner-facing
    # message. The raw value itself is not displayed.
    assert (
        "payload.decision_type"
        in body
    )


def test_demo_keeps_learner_adaptive_messages(
) -> None:
    response = client.get(
        "/adaptive-demo"
    )

    body = response.text

    assert (
        '"remediate"'
        in body
    )

    assert (
        '"reassess"'
        in body
    )

    assert (
        "Here is a support question"
        in body
    )

    assert (
        "Good progress. Now try the "
        in body
    )

    assert (
        "Correct. Here is your next question."
        in body
    )
