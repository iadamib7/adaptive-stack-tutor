from .student import Student


def update_mastery(
    student: Student,
    concept: str,
    correct: bool,
) -> None:

    score = student.mastery.get(concept, 0.5)

    if correct:
        score += 0.10
    else:
        score -= 0.10

    score = max(0.0, min(1.0, score))

    student.mastery[concept] = score