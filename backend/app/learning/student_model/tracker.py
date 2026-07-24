from .attempt import Attempt
from .mastery import update_mastery
from .student import Student


class StudentTracker:

    def process_attempt(
        self,
        student: Student,
        attempt: Attempt,
    ) -> None:

        student.attempts += 1

        if attempt.correct:
            student.correct += 1
        else:
            student.incorrect += 1

        update_mastery(
            student,
            attempt.concept,
            attempt.correct,
        )