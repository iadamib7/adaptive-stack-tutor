from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.database.connection import SessionLocal
from backend.app.database.models import (
    AttemptRecord,
    MasteryRecord,
    StudentRecord,
)
from backend.app.learning.student_model.attempt import Attempt
from backend.app.learning.student_model.student import Student


class StudentProgressRepository:
    def get_student(
        self,
        student_id: int,
    ) -> Student | None:
        with SessionLocal() as session:
            statement = (
                select(StudentRecord)
                .options(
                    selectinload(StudentRecord.mastery_scores),
                )
                .where(StudentRecord.id == student_id)
            )

            record = session.scalar(statement)

            if record is None:
                return None

            return self._to_student(record)

    def save_progress(
        self,
        student: Student,
        attempt: Attempt,
    ) -> None:
        with SessionLocal.begin() as session:
            student_record = session.get(
                StudentRecord,
                student.id,
            )

            if student_record is None:
                student_record = StudentRecord(
                    id=student.id,
                    name=student.name,
                )
                session.add(student_record)

            student_record.name = student.name
            student_record.attempts = student.attempts
            student_record.correct = student.correct
            student_record.incorrect = student.incorrect

            existing_mastery_records = {
                record.concept: record
                for record in session.scalars(
                    select(MasteryRecord).where(
                        MasteryRecord.student_id == student.id
                    )
                )
            }

            for concept, score in student.mastery.items():
                mastery_record = existing_mastery_records.get(
                    concept,
                )

                if mastery_record is None:
                    mastery_record = MasteryRecord(
                        student_id=student.id,
                        concept=concept,
                        score=score,
                    )
                    session.add(mastery_record)
                else:
                    mastery_record.score = score

            session.add(
                AttemptRecord(
                    student_id=attempt.student_id,
                    question_id=attempt.question_id,
                    concept=attempt.concept,
                    correct=attempt.correct,
                    response=attempt.response,
                )
            )

    def get_attempt_history(
        self,
        student_id: int,
    ) -> list[Attempt]:
        with SessionLocal() as session:
            statement = (
                select(AttemptRecord)
                .where(
                    AttemptRecord.student_id == student_id,
                )
                .order_by(AttemptRecord.created_at.asc())
            )

            records = session.scalars(statement).all()

            return [
                Attempt(
                    student_id=record.student_id,
                    question_id=record.question_id,
                    concept=record.concept,
                    correct=record.correct,
                    response=record.response,
                )
                for record in records
            ]

    def get_attempted_question_ids(
        self,
        student_id: int,
    ) -> set[int]:
        with SessionLocal() as session:
            statement = select(
                AttemptRecord.question_id,
            ).where(
                AttemptRecord.student_id == student_id,
            )

            return set(session.scalars(statement).all())

    @staticmethod
    def _to_student(
        record: StudentRecord,
    ) -> Student:
        return Student(
            id=record.id,
            name=record.name,
            attempts=record.attempts,
            correct=record.correct,
            incorrect=record.incorrect,
            mastery={
                mastery.concept: mastery.score
                for mastery in record.mastery_scores
            },
        )
    