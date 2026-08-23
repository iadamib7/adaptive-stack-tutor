from __future__ import annotations


_CORRECT_MESSAGES = [
    (
        "Excellent work! ??<br><br>"
        "You got this one right.<br><br>"
        "Let's keep building on that success."
    ),
    (
        "Great thinking! ??<br><br>"
        "Your answer is correct.<br><br>"
        "You're ready for the next challenge."
    ),
    (
        "Nicely done! ?<br><br>"
        "You solved that correctly.<br><br>"
        "Keep going ? you're making strong progress."
    ),
    (
        "Well done! ??<br><br>"
        "That's the correct answer.<br><br>"
        "Let's see what you can do with the next one."
    ),
]

_PARTIAL_MESSAGES = [
    (
        "You're close! ??<br><br>"
        "Part of your work is correct, but something "
        "still needs adjusting.<br><br>"
        "Check your steps and try once more."
    ),
    (
        "Good progress! ?<br><br>"
        "You've got part of the idea.<br><br>"
        "Take another look at your working and try again."
    ),
]

_INCORRECT_MESSAGES = [
    (
        "Good try! ??<br><br>"
        "That answer isn't quite right yet.<br><br>"
        "Check your working carefully and give it "
        "another try."
    ),
    (
        "Keep going! ??<br><br>"
        "This one needs another look.<br><br>"
        "Work through the problem step by step and "
        "try again."
    ),
    (
        "Almost there! ??<br><br>"
        "Your answer needs a correction.<br><br>"
        "Take your time, check each step, and try again."
    ),
    (
        "Nice effort! ??<br><br>"
        "You haven't got this one yet, but that's okay."
        "<br><br>"
        "Review your steps and give it another shot."
    ),
]


def build_learner_feedback(
    *,
    score: float,
    concept_name: str,
    attempt_number: int,
    question_name: str | None = None,
    next_concept_name: str | None = None,
    concept_completed: bool = False,
) -> str:
    if concept_completed:
        if next_concept_name:
            return (
                "Fantastic work! ??<br><br>"
                f"You've completed "
                f"<strong>{concept_name}</strong>!"
                "<br><br>"
                f"You're now moving on to "
                f"<strong>{next_concept_name}</strong>."
            )

        return (
            "Fantastic work! ??<br><br>"
            f"You've completed "
            f"<strong>{concept_name}</strong>!"
        )

    index = max(
        attempt_number - 1,
        0,
    )

    if score >= 1.0:
        messages = _CORRECT_MESSAGES

    elif score > 0.0:
        messages = _PARTIAL_MESSAGES

    else:
        messages = _INCORRECT_MESSAGES

    message = messages[
        index % len(messages)
    ]

    if (
        score >= 1.0
        and question_name
    ):
        message += (
            "<br><br>"
            f"You've completed this step in "
            f"<strong>{concept_name}</strong>."
        )

    return message
