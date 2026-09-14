from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(
    app
)


def test_adaptive_demo_redirects_to_instructor() -> None:
    response = client.get(
        "/adaptive-demo",
        follow_redirects=False,
    )

    assert response.status_code in {
        302,
        307,
    }

    assert (
        response.headers["location"]
        == "/instructor"
    )


def test_instructor_page_loads() -> None:
    response = client.get(
        "/instructor"
    )

    assert response.status_code == 200

    body = response.text

    assert (
        "Adaptive STACK Tutor"
        in body
    )

    assert (
        "Instructor workspace"
        in body
    )


def test_instructor_has_upload_controls() -> None:
    response = client.get(
        "/instructor"
    )

    body = response.text

    assert (
        'id="questionBank"'
        in body
    )

    assert (
        'id="metadataFile"'
        in body
    )

    assert (
        "Analyze Question Bank"
        in body
    )


def test_instructor_has_pathway_controls() -> None:
    response = client.get(
        "/instructor"
    )

    body = response.text

    assert (
        "Review Adaptive Pathway"
        in body
    )

    assert (
        "Difficulty"
        in body
    )

    assert (
        "Entry point"
        in body
    )

    assert (
        "Prerequisites"
        in body
    )

    assert (
        "Supports"
        in body
    )

    assert (
        "Publish Learner Session"
        in body
    )


def test_instructor_does_not_render_learner_answer_ui(
) -> None:
    response = client.get(
        "/instructor"
    )

    body = response.text

    assert (
        'id="questionHtml"'
        not in body
    )

    assert (
        'id="submitButton"'
        not in body
    )

    assert (
        "/answers"
        not in body
    )


def test_student_page_loads() -> None:
    response = client.get(
        "/student/example-session"
    )

    assert response.status_code == 200

    body = response.text

    assert (
        "Adaptive STACK Tutor"
        in body
    )

    assert (
        "Learner session"
        in body
    )


def test_student_has_answer_interface() -> None:
    response = client.get(
        "/student/example-session"
    )

    body = response.text

    assert (
        'id="questionTitle"'
        in body
    )

    assert (
        'id="questionHtml"'
        in body
    )

    assert (
        'id="submitButton"'
        in body
    )

    assert (
        "Submit Answer"
        in body
    )

    assert (
        "/api/adaptive/sessions/"
        in body
    )

    assert (
        "/answers"
        in body
    )


def test_student_does_not_show_instructor_controls(
) -> None:
    response = client.get(
        "/student/example-session"
    )

    body = response.text

    assert (
        'id="questionBank"'
        not in body
    )

    assert (
        'id="metadataFile"'
        not in body
    )

    assert (
        "Analyze Question Bank"
        not in body
    )

    assert (
        "Review Adaptive Pathway"
        not in body
    )

    assert (
        "Publish Learner Session"
        not in body
    )

    assert (
        "Prerequisites"
        not in body
    )

    assert (
        "Supports"
        not in body
    )
    

def test_student_hides_internal_routing_fields() -> None:
    response = client.get(
        "/student/example-session"
    )

    body = response.text

    assert (
        "return_target_question_id"
        not in body
    )

    assert (
        "previous_outcome"
        not in body
    )

    assert (
        "decision_reason"
        not in body
    )

    assert (
        "candidate_score"
        not in body
    )


def test_student_keeps_learner_facing_feedback() -> None:
    response = client.get(
        "/student/example-session"
    )

    body = response.text

    assert (
        "Correct. Here is your next question."
        in body
    )

    assert (
        "Partially correct."
        in body
    )

    assert (
        "Your response was recorded."
        in body
    )
