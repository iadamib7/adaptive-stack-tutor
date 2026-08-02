from __future__ import annotations

from html import escape
from typing import Any

import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 10


st.set_page_config(
    page_title="Adaptive STACK Tutor",
    page_icon="📚",
    layout="wide",
)


st.markdown(
    """
    <style>
        .block-container {
            max-width: 1250px;
            padding-top: 1.5rem;
        }

        .hero,
        .card {
            padding: 1.25rem;
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 16px;
            margin-bottom: 1rem;
        }

        .hero h1 {
            margin: 0;
        }

        .hero p {
            margin: 0.35rem 0 0;
            opacity: 0.75;
        }

        .label {
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            opacity: 0.65;
        }

        .question-text {
            font-size: 1.2rem;
            font-weight: 650;
            line-height: 1.5;
            margin-top: 0.5rem;
        }

        .correct-box {
            padding: 1rem;
            border: 1px solid rgba(0, 150, 80, 0.4);
            border-radius: 12px;
            margin-bottom: 1rem;
        }

        .incorrect-box {
            padding: 1rem;
            border: 1px solid rgba(220, 60, 60, 0.4);
            border-radius: 12px;
            margin-bottom: 1rem;
        }

        div[data-testid="stMetric"] {
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 12px;
            padding: 0.6rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_get(path: str) -> tuple[Any | None, str | None]:
    try:
        response = requests.get(
            f"{API_URL}{path}",
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as error:
        return None, f"Could not connect to the backend: {error}"

    if response.status_code == 200:
        return response.json(), None

    if response.status_code == 404:
        return None, None

    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text

    return None, f"Backend returned {response.status_code}: {detail}"


def api_post(
    path: str,
    payload: dict[str, Any],
) -> tuple[dict[str, Any] | None, str | None]:
    try:
        response = requests.post(
            f"{API_URL}{path}",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as error:
        return None, f"Could not connect to the backend: {error}"

    if response.status_code == 200:
        return response.json(), None

    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text

    return None, f"Backend returned {response.status_code}: {detail}"


def initialize_state() -> None:
    defaults = {
        "student_id": 1,
        "student_name": "Ibrahim Adam",
        "current_question": None,
        "last_result": None,
        "backend_error": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_first_question() -> None:
    question, error = api_get("/questions/first")
    st.session_state.backend_error = error

    if isinstance(question, dict):
        st.session_state.current_question = question


def load_student() -> dict[str, Any] | None:
    student, error = api_get(
        f"/learning/students/{st.session_state.student_id}"
    )

    if error:
        st.session_state.backend_error = error

    return student if isinstance(student, dict) else None


def load_attempts() -> list[dict[str, Any]]:
    attempts, error = api_get(
        f"/learning/students/{st.session_state.student_id}/attempts"
    )

    if error:
        st.session_state.backend_error = error

    if isinstance(attempts, list):
        return [
            attempt
            for attempt in attempts
            if isinstance(attempt, dict)
        ]

    return []


def difficulty_label(value: Any) -> str:
    if isinstance(value, str):
        return value.replace("_", " ").title()

    labels = {
        1: "Beginner",
        2: "Easy",
        3: "Medium",
        4: "Hard",
        5: "Advanced",
    }

    return labels.get(
        value,
        str(value or "Not specified"),
    )


def submit_attempt(
    question: dict[str, Any],
    answer: str,
) -> None:
    payload = {
        "student_id": st.session_state.student_id,
        "student_name": st.session_state.student_name,
        "question_id": question["id"],
        "response": answer,
        "course": question.get("course"),
    }

    result, error = api_post(
        "/learning/attempts",
        payload,
    )

    st.session_state.backend_error = error

    if result is not None:
        st.session_state.last_result = result

        next_question = result.get("next_question")

        if isinstance(next_question, dict):
            st.session_state.current_question = next_question


initialize_state()


if st.session_state.current_question is None:
    load_first_question()


st.markdown(
    """
    <div class="hero">
        <h1>📚 Adaptive STACK Tutor</h1>
        <p>
            Personalized mathematics learning using automatic symbolic
            grading, mastery tracking, feedback, and adaptive
            recommendations.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.header("Student Profile")

    student_id = st.number_input(
        "Student ID",
        min_value=1,
        step=1,
        value=int(st.session_state.student_id),
    )

    student_name = st.text_input(
        "Student name",
        value=st.session_state.student_name,
    )

    if int(student_id) != st.session_state.student_id:
        st.session_state.student_id = int(student_id)
        st.session_state.last_result = None
        st.session_state.current_question = None
        load_first_question()

    st.session_state.student_name = (
        student_name.strip() or "Student"
    )

    st.divider()

    if st.button(
        "Load first question",
        use_container_width=True,
    ):
        st.session_state.current_question = None
        st.session_state.last_result = None
        load_first_question()
        st.rerun()

    if st.button(
        "Refresh dashboard",
        use_container_width=True,
    ):
        st.rerun()

    st.caption(f"Backend: {API_URL}")


if st.session_state.backend_error:
    st.error(st.session_state.backend_error)
    st.info(
        "Make sure the backend is running with "
        "`uvicorn backend.app.main:app --reload`."
    )


question = st.session_state.current_question


if question is None:
    st.warning(
        "No question could be loaded. Check the backend and "
        "`datasets/questions.json`."
    )
    st.stop()


student = load_student() or {
    "attempts": 0,
    "correct": 0,
    "incorrect": 0,
    "mastery": {},
}

attempt_history = load_attempts()

attempt_count = int(student.get("attempts", 0))
correct_count = int(student.get("correct", 0))
incorrect_count = int(student.get("incorrect", 0))

accuracy = (
    correct_count / attempt_count * 100
    if attempt_count
    else 0.0
)

mastery = student.get("mastery") or {}

weakest = (
    min(mastery, key=mastery.get)
    if mastery
    else "Not available"
)

strongest = (
    max(mastery, key=mastery.get)
    if mastery
    else "Not available"
)


left, right = st.columns(
    [1.65, 1],
    gap="large",
)


with left:
    st.subheader("Current Question")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Course",
        question.get("course", "Not specified"),
    )

    col2.metric(
        "Concept",
        question.get("concept", "Not specified"),
    )

    col3.metric(
        "Difficulty",
        difficulty_label(question.get("difficulty")),
    )

    question_text = escape(
        str(
            question.get(
                "question_text",
                "Question text unavailable.",
            )
        )
    )

    question_id = escape(
        str(question.get("id", ""))
    )

    st.markdown(
        f"""
        <div class="card">
            <div class="label">Question #{question_id}</div>
            <div class="question-text">
                {question_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form(
        "attempt_form",
        clear_on_submit=True,
    ):
        answer = st.text_input(
            "Student answer",
            placeholder="Enter your mathematical answer",
            help=(
                "Examples: 5*x^4, 5x^4, x^2 + 2x + 1, or 1/2."
            ),
        )

        submitted = st.form_submit_button(
            "Submit answer and adapt",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not answer.strip():
                st.warning(
                    "Enter an answer before submitting."
                )
            else:
                submit_attempt(
                    question=question,
                    answer=answer.strip(),
                )
                st.rerun()

    result = st.session_state.last_result

    if isinstance(result, dict):
        st.subheader("Latest Learning Update")

        is_correct = bool(
            result.get("correct", False)
        )

        evaluation_error = result.get(
            "evaluation_error"
        )

        student_response = escape(
            str(result.get("student_response", ""))
        )

        expected_answer = escape(
            str(result.get("expected_answer", ""))
        )

        feedback = escape(
            str(
                result.get(
                    "feedback",
                    "No feedback was returned.",
                )
            )
        )

        if is_correct:
            st.success(
                "Correct — your answer is mathematically "
                "equivalent to the expected answer."
            )
        else:
            st.error(
                "Incorrect — your answer is not mathematically "
                "equivalent to the expected answer."
            )

        if evaluation_error:
            st.warning(str(evaluation_error))

        answer_col1, answer_col2 = st.columns(2)

        answer_col1.metric(
            "Your answer",
            student_response or "Not available",
        )

        answer_col2.metric(
            "Expected answer",
            expected_answer or "Not available",
        )

        before = float(
            result.get("mastery_before", 0.0)
        )

        after = float(
            result.get("mastery_after", 0.0)
        )

        r1, r2, r3 = st.columns(3)

        r1.metric(
            "Concept",
            result.get(
                "submitted_concept",
                "Unknown",
            ),
        )

        r2.metric(
            "Mastery before",
            f"{before:.0%}",
        )

        r3.metric(
            "Mastery after",
            f"{after:.0%}",
            delta=f"{after - before:+.0%}",
        )

        concept_mastered = bool(
            result.get("concept_mastered", False)
        )

        if concept_mastered:
            st.success(
                "Mastery achieved. You are ready to advance "
                "to the next learning target."
            )
        else:
            st.info(
                "Continue practicing this concept until your "
                "mastery reaches 85%."
            )

        st.markdown(
            f"""
            <div class="card">
                <div class="label">Personalized Feedback</div>
                <p>{feedback}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        next_question = result.get("next_question")
        reason = escape(
            str(
                result.get(
                    "recommendation_reason",
                    "No recommendation reason was returned.",
                )
            )
        )

        if isinstance(next_question, dict):
            recommendation_text = escape(
                str(
                    next_question.get(
                        "question_text",
                        "No question text available.",
                    )
                )
            )

            next_concept = escape(
                str(
                    next_question.get(
                        "concept",
                        "Not specified",
                    )
                )
            )

            next_difficulty = escape(
                difficulty_label(
                    next_question.get("difficulty")
                )
            )

            st.markdown(
                f"""
                <div class="card">
                    <div class="label">
                        Next Recommended Question
                    </div>
                    <div class="question-text">
                        {recommendation_text}
                    </div>
                    <p>
                        <strong>Concept:</strong> {next_concept}
                        &nbsp; | &nbsp;
                        <strong>Difficulty:</strong>
                        {next_difficulty}
                    </p>
                    <p>{reason}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info(
                "No additional question is currently available."
            )


with right:
    st.subheader("Learning Analytics")

    m1, m2 = st.columns(2)

    m1.metric(
        "Attempts",
        attempt_count,
    )

    m2.metric(
        "Accuracy",
        f"{accuracy:.0f}%",
    )

    m3, m4 = st.columns(2)

    m3.metric(
        "Correct",
        correct_count,
    )

    m4.metric(
        "Incorrect",
        incorrect_count,
    )

    st.markdown(
        f"""
        <div class="card">
            <div class="label">Strongest concept</div>
            <div class="question-text">
                {escape(str(strongest))}
            </div>
            <br>
            <div class="label">Priority concept</div>
            <div class="question-text">
                {escape(str(weakest))}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Concept Mastery")

    if mastery:
        for concept, score in sorted(
            mastery.items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            safe_score = max(
                0.0,
                min(float(score), 1.0),
            )

            st.write(
                f"**{concept}** — {safe_score:.0%}"
            )

            st.progress(safe_score)
    else:
        st.info(
            "Submit the first attempt to begin building "
            "the learner model."
        )

    st.subheader("Recent Attempts")

    if attempt_history:
        for attempt in reversed(
            attempt_history[-5:]
        ):
            correct = bool(
                attempt.get("correct", False)
            )

            symbol = "✅" if correct else "❌"
            status = "Correct" if correct else "Incorrect"

            concept = attempt.get(
                "concept",
                "Unknown concept",
            )

            response = attempt.get(
                "response",
                "No response",
            )

            st.markdown(
                f"""
                <div class="card">
                    <strong>{symbol} {status}</strong><br>
                    <span>{escape(str(concept))}</span><br>
                    <small>
                        Response: {escape(str(response))}
                    </small>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info(
            "No attempts have been recorded yet."
        )