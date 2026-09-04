from backend.app.learning.adaptive_engine.adaptive_graph_builder import (
    StackAdaptiveGraphBuilder,
)

from backend.app.learning.adaptive_engine.bank_profile import (
    StackBankProfile,
    StackPRTBranchProfile,
    StackQuestionProfile,
)

from backend.app.learning.adaptive_engine.models import (
    AdaptiveQuestion,
)

from backend.app.learning.adaptive_engine.question_bank import (
    AdaptiveQuestionBank,
    ImportedAdaptiveQuestion,
)


CATEGORY = (
    "$course$/top/Functions/"
    "Mixed practice"
)


def profile_question(
    *,
    question_id: str,
    title: str,
    prompt: str,
    inputs: int,
    nodes: int,
    diagnostic: bool = False,
) -> StackQuestionProfile:
    branches = ()

    if diagnostic:
        branches = (
            StackPRTBranchProfile(
                prt_name="prt1",
                node_name="1",
                answer_test="AlgEquiv",
                true_answer_note=(
                    "prt1-2-T"
                ),
                false_answer_note=(
                    "prt1-2-F"
                ),
                true_feedback=(
                    "Check this step."
                ),
                false_feedback="",
            ),
        )

    return StackQuestionProfile(
        question_id=question_id,
        title=title,
        category_path=CATEGORY,
        input_names=tuple(
            f"ans{index}"
            for index in range(
                1,
                inputs + 1,
            )
        ),
        prt_names=("prt1",),
        prt_node_count=nodes,
        branches=branches,
        deployed_seed_count=0,
        prompt_text=prompt,
    )


def bank(
    *ids: str,
) -> AdaptiveQuestionBank:
    return AdaptiveQuestionBank(
        [
            ImportedAdaptiveQuestion(
                adaptive_question=(
                    AdaptiveQuestion(
                        question_id=question_id,
                        title=question_id,
                    )
                ),
                stack_xml=(
                    "<quiz></quiz>"
                ),
            )
            for question_id in ids
        ]
    )


def support_for(
    result,
    source_id: str,
) -> list[str]:
    aliases = (
        result.outcome_aliases.get(
            source_id,
            {},
        )
    )

    support_keys = set(
        aliases.values()
    )

    return [
        question.question_id
        for question
        in result.bank.adaptive_questions()
        if (
            support_keys
            & set(
                question.supports
            )
        )
    ]


def test_rational_question_prefers_rational_support(
) -> None:
    profile = StackBankProfile(
        questions=(
            profile_question(
                question_id="SOURCE",
                title=(
                    "Rational expression challenge"
                ),
                prompt=(
                    "Simplify a rational expression "
                    "using a common denominator."
                ),
                inputs=3,
                nodes=4,
                diagnostic=True,
            ),
            profile_question(
                question_id="RATIONAL",
                title=(
                    "Solving Rational Equations"
                ),
                prompt=(
                    "Solve a rational equation "
                    "containing fractions."
                ),
                inputs=1,
                nodes=1,
            ),
            profile_question(
                question_id="NUMBER_LINE",
                title=(
                    "Distance on a number line"
                ),
                prompt=(
                    "Find the distance between "
                    "two points."
                ),
                inputs=1,
                nodes=1,
            ),
        )
    )

    result = (
        StackAdaptiveGraphBuilder()
        .build(
            bank=bank(
                "SOURCE",
                "RATIONAL",
                "NUMBER_LINE",
            ),
            profile=profile,
        )
    )

    assert support_for(
        result,
        "SOURCE",
    ) == [
        "RATIONAL"
    ]


def test_number_line_is_not_rational_remediation(
) -> None:
    profile = StackBankProfile(
        questions=(
            profile_question(
                question_id="SOURCE",
                title="Rational expression",
                prompt=(
                    "Find a common denominator "
                    "for this rational expression."
                ),
                inputs=2,
                nodes=3,
                diagnostic=True,
            ),
            profile_question(
                question_id="NUMBER_LINE",
                title=(
                    "Distance on a number line"
                ),
                prompt=(
                    "Calculate the distance "
                    "between points A and B."
                ),
                inputs=1,
                nodes=1,
            ),
        )
    )

    result = (
        StackAdaptiveGraphBuilder()
        .build(
            bank=bank(
                "SOURCE",
                "NUMBER_LINE",
            ),
            profile=profile,
        )
    )

    assert (
        result.outcome_aliases
        .get(
            "SOURCE",
            {},
        )
        == {}
    )

    question = (
        result.bank.require(
            "NUMBER_LINE"
        ).adaptive_question
    )

    assert (
        question.supports
        == ()
    )


def test_trigonometric_question_does_not_use_exponential_support(
) -> None:
    profile = StackBankProfile(
        questions=(
            profile_question(
                question_id="TRIG",
                title=(
                    "Solve the trigonometric "
                    "equation using identities"
                ),
                prompt=(
                    "Use trigonometric identities "
                    "to solve for x."
                ),
                inputs=3,
                nodes=5,
                diagnostic=True,
            ),
            profile_question(
                question_id="EXP",
                title=(
                    "Solve the exponential equation"
                ),
                prompt=(
                    "Solve an exponential equation "
                    "using logarithms."
                ),
                inputs=1,
                nodes=1,
            ),
        )
    )

    result = (
        StackAdaptiveGraphBuilder()
        .build(
            bank=bank(
                "TRIG",
                "EXP",
            ),
            profile=profile,
        )
    )

    assert (
        support_for(
            result,
            "TRIG",
        )
        == []
    )


def test_quadratic_prefers_quadratic_support(
) -> None:
    profile = StackBankProfile(
        questions=(
            profile_question(
                question_id="WORD",
                title=(
                    "Quadratic Word Problems"
                ),
                prompt=(
                    "Solve a word problem leading "
                    "to a quadratic equation."
                ),
                inputs=3,
                nodes=5,
                diagnostic=True,
            ),
            profile_question(
                question_id="QUADRATIC",
                title=(
                    "Solving a Quadratic Equation "
                    "using the Quadratic Formula"
                ),
                prompt=(
                    "Solve the quadratic using "
                    "the quadratic formula."
                ),
                inputs=1,
                nodes=1,
            ),
            profile_question(
                question_id="LINEAR",
                title=(
                    "Solve a linear inequality"
                ),
                prompt=(
                    "Solve a linear inequality "
                    "for x."
                ),
                inputs=1,
                nodes=1,
            ),
        )
    )

    result = (
        StackAdaptiveGraphBuilder()
        .build(
            bank=bank(
                "WORD",
                "QUADRATIC",
                "LINEAR",
            ),
            profile=profile,
        )
    )

    assert support_for(
        result,
        "WORD",
    ) == [
        "QUADRATIC"
    ]


def test_generic_word_equation_is_not_enough(
) -> None:
    profile = StackBankProfile(
        questions=(
            profile_question(
                question_id="TRIG",
                title=(
                    "Trigonometric equation"
                ),
                prompt=(
                    "Use sine and cosine "
                    "identities."
                ),
                inputs=2,
                nodes=4,
                diagnostic=True,
            ),
            profile_question(
                question_id="EXP",
                title=(
                    "Exponential equation"
                ),
                prompt=(
                    "Use logarithms and "
                    "exponents."
                ),
                inputs=1,
                nodes=1,
            ),
        )
    )

    result = (
        StackAdaptiveGraphBuilder()
        .build(
            bank=bank(
                "TRIG",
                "EXP",
            ),
            profile=profile,
        )
    )

    assert (
        support_for(
            result,
            "TRIG",
        )
        == []
    )



def test_prompt_overlap_cannot_override_different_topics(
) -> None:
    profile = StackBankProfile(
        questions=(
            profile_question(
                question_id="TRIG",
                title=(
                    "Solve the trigonometric "
                    "equation using identities"
                ),
                prompt=(
                    "Find the exact solutions "
                    "and use the correct mathematical "
                    "method to obtain the solutions."
                ),
                inputs=3,
                nodes=5,
                diagnostic=True,
            ),
            profile_question(
                question_id="EXP",
                title=(
                    "Solve the exponential equation "
                    "and write it using logarithms"
                ),
                prompt=(
                    "Find the exact solutions "
                    "and use the correct mathematical "
                    "method to obtain the solutions."
                ),
                inputs=1,
                nodes=1,
            ),
        )
    )

    result = (
        StackAdaptiveGraphBuilder()
        .build(
            bank=bank(
                "TRIG",
                "EXP",
            ),
            profile=profile,
        )
    )

    assert (
        support_for(
            result,
            "TRIG",
        )
        == []
    )
