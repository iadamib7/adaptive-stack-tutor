from backend.app.learning.adaptive_engine.adaptive_graph_builder import (
    StackAdaptiveGraphBuilder,
)

from backend.app.learning.adaptive_engine.bank_profile import (
    StackBankProfile,
    StackQuestionProfile,
)

from backend.app.learning.adaptive_engine.models import (
    AdaptiveQuestion,
)

from backend.app.learning.adaptive_engine.question_bank import (
    AdaptiveQuestionBank,
    ImportedAdaptiveQuestion,
)


def _profile_question(
    *,
    question_id: str,
    title: str,
    category: str,
    inputs: int,
    nodes: int,
) -> StackQuestionProfile:
    return StackQuestionProfile(
        question_id=question_id,
        title=title,
        category_path=category,
        input_names=tuple(
            f"ans{index}"
            for index in range(
                1,
                inputs + 1,
            )
        ),
        prt_names=(
            ("prt1",)
            if nodes
            else ()
        ),
        prt_node_count=nodes,
        branches=(),
        deployed_seed_count=0,
    )


def _bank(
    order: list[str],
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
            for question_id in order
        ]
    )


def _profile() -> StackBankProfile:
    # Deliberately scrambled.
    #
    # Q5 occurs first but is structurally more
    # complex than Q1.
    return StackBankProfile(
        questions=(
            _profile_question(
                question_id="Q5",
                title="Advanced functions",
                category="Functions",
                inputs=3,
                nodes=4,
            ),
            _profile_question(
                question_id="Q3",
                title="Linear equation",
                category="Algebra",
                inputs=1,
                nodes=2,
            ),
            _profile_question(
                question_id="Q1",
                title="Function basics",
                category="Functions",
                inputs=1,
                nodes=1,
            ),
            _profile_question(
                question_id="Q4",
                title="Harder algebra",
                category="Algebra",
                inputs=2,
                nodes=4,
            ),
            _profile_question(
                question_id="Q2",
                title="Function practice",
                category="Functions",
                inputs=2,
                nodes=2,
            ),
        )
    )


def build():
    return (
        StackAdaptiveGraphBuilder()
        .build(
            bank=_bank(
                [
                    "Q5",
                    "Q3",
                    "Q1",
                    "Q4",
                    "Q2",
                ]
            ),
            profile=_profile(),
        )
    )


def test_builder_does_not_use_bank_order_for_entry(
) -> None:
    result = build()

    # Q5 is physically first.
    # Q1 is the simpler bank-local anchor.
    assert (
        result.entry_question_id
        == "Q1"
    )

    q1 = result.bank.require(
        "Q1"
    ).adaptive_question

    assert q1.entry_point is True


def test_only_one_global_entry_point(
) -> None:
    result = build()

    entries = [
        question.question_id
        for question
        in result.bank.adaptive_questions()
        if question.entry_point
    ]

    assert entries == [
        "Q1"
    ]


def test_questions_in_same_category_share_skill(
) -> None:
    result = build()

    q1 = result.bank.require(
        "Q1"
    ).adaptive_question

    q2 = result.bank.require(
        "Q2"
    ).adaptive_question

    q5 = result.bank.require(
        "Q5"
    ).adaptive_question

    assert q1.skills == q2.skills
    assert q2.skills == q5.skills


def test_later_category_items_require_category_mastery(
) -> None:
    result = build()

    q3 = result.bank.require(
        "Q3"
    ).adaptive_question

    q4 = result.bank.require(
        "Q4"
    ).adaptive_question

    assert q3.skills

    assert (
        q4.prerequisites
        == q3.skills
    )


def test_structurally_more_complex_items_are_harder(
) -> None:
    result = build()

    q1 = result.bank.require(
        "Q1"
    ).adaptive_question

    q2 = result.bank.require(
        "Q2"
    ).adaptive_question

    q5 = result.bank.require(
        "Q5"
    ).adaptive_question

    assert (
        q1.difficulty
        < q2.difficulty
        < q5.difficulty
    )


def test_builder_preserves_existing_diagnostic_metadata(
) -> None:
    bank = AdaptiveQuestionBank(
        [
            ImportedAdaptiveQuestion(
                adaptive_question=(
                    AdaptiveQuestion(
                        question_id="Q1",
                        title="Question",
                        supports=(
                            "sign_error",
                        ),
                        diagnoses=(
                            "algebra_error",
                        ),
                    )
                ),
                stack_xml=(
                    "<quiz></quiz>"
                ),
            )
        ]
    )

    profile = StackBankProfile(
        questions=(
            _profile_question(
                question_id="Q1",
                title="Question",
                category="Algebra",
                inputs=1,
                nodes=1,
            ),
        )
    )

    result = (
        StackAdaptiveGraphBuilder()
        .build(
            bank=bank,
            profile=profile,
        )
    )

    question = result.bank.require(
        "Q1"
    ).adaptive_question

    assert question.supports == (
        "sign_error",
    )

    assert question.diagnoses == (
        "algebra_error",
    )


def test_mismatched_profile_is_rejected(
) -> None:
    bank = _bank(
        ["Q1"]
    )

    profile = StackBankProfile(
        questions=(
            _profile_question(
                question_id="Q2",
                title="Other",
                category="Algebra",
                inputs=1,
                nodes=1,
            ),
        )
    )

    try:
        StackAdaptiveGraphBuilder().build(
            bank=bank,
            profile=profile,
        )
    except ValueError as error:
        assert (
            "do not describe the same"
            in str(error)
        )
    else:
        raise AssertionError(
            "Expected mismatched bank/profile "
            "to be rejected."
        )


def test_graph_contains_no_xml_sequence_field(
) -> None:
    result = build()

    for question in (
        result.bank.adaptive_questions()
    ):
        assert not hasattr(
            question,
            "xml_position"
        )

        assert not hasattr(
            question,
            "next_question_id"
        )
