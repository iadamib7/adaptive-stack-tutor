from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.connection import Base


class StudentRecord(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    correct: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    incorrect: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    mastery_scores: Mapped[list["MasteryRecord"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )

    attempt_history: Mapped[list["AttemptRecord"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )


class MasteryRecord(Base):
    __tablename__ = "mastery_scores"
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "concept",
            name="uq_student_concept",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    concept: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )
    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    student: Mapped[StudentRecord] = relationship(
        back_populates="mastery_scores",
    )


class AttemptRecord(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    concept: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )
    correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )
    response: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    student: Mapped[StudentRecord] = relationship(
        back_populates="attempt_history",
    )