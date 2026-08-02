from __future__ import annotations

from sympy import Symbol, simplify
from sympy.core.expr import Expr
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from backend.app.learning.assessment.evaluation_result import (
    EvaluationResult,
)


class AnswerEvaluator:
    """
    Evaluates whether a student's mathematical expression is
    equivalent to the expected answer stored in the question bank.

    Examples treated as equivalent:

    5x^4
    5*x**4
    x^4*5
    5(x^4)
    """

    _transformations = standard_transformations + (
        implicit_multiplication_application,
        convert_xor,
    )

    _allowed_symbols = {
        "x": Symbol("x"),
        "y": Symbol("y"),
        "z": Symbol("z"),
        "t": Symbol("t"),
        "n": Symbol("n"),
    }

    def evaluate(
        self,
        student_answer: str,
        expected_answer: str,
    ) -> EvaluationResult:
        cleaned_student_answer = self._clean_answer(student_answer)
        cleaned_expected_answer = self._clean_answer(expected_answer)

        if not cleaned_student_answer:
            return EvaluationResult(
                correct=False,
                student_answer=student_answer,
                expected_answer=expected_answer,
                error_message="No answer was provided.",
            )

        try:
            student_expression = self._parse_expression(
                cleaned_student_answer
            )
        except (SyntaxError, TypeError, ValueError):
            return EvaluationResult(
                correct=False,
                student_answer=student_answer,
                expected_answer=expected_answer,
                error_message=(
                    "The answer could not be interpreted as a "
                    "mathematical expression."
                ),
            )

        try:
            expected_expression = self._parse_expression(
                cleaned_expected_answer
            )
        except (SyntaxError, TypeError, ValueError):
            raise ValueError(
                "The stored correct answer could not be interpreted."
            )

        correct = self._expressions_are_equivalent(
            student_expression,
            expected_expression,
        )

        return EvaluationResult(
            correct=correct,
            student_answer=student_answer,
            expected_answer=expected_answer,
        )

    def _parse_expression(self, answer: str) -> Expr:
        expression = parse_expr(
            answer,
            local_dict=self._allowed_symbols,
            transformations=self._transformations,
            evaluate=True,
        )

        unsupported_symbols = (
            expression.free_symbols
            - set(self._allowed_symbols.values())
        )

        if unsupported_symbols:
            raise ValueError(
                "The answer contains unsupported variables."
            )

        return expression

    @staticmethod
    def _expressions_are_equivalent(
        student_expression: Expr,
        expected_expression: Expr,
    ) -> bool:
        difference = simplify(
            student_expression - expected_expression
        )

        return difference == 0

    @staticmethod
    def _clean_answer(answer: str) -> str:
        return (
            answer.strip()
            .replace("×", "*")
            .replace("÷", "/")
            .replace("−", "-")
        )