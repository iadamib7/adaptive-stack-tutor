import pytest

from backend.app.learning.adaptive_tasks.extractor import (
    AdaptiveTaskExtractionError,
    extract_adaptive_tasks,
)


def make_question(
    question_text: str,
    prts: list[
        tuple[str, str]
    ],
) -> str:
    prt_xml = ""

    for (
        prt_name,
        answer_name,
    ) in prts:
        prt_xml += f"""
        <prt>
            <name>{prt_name}</name>
            <node>
                <name>0</name>
                <answertest>
                    AlgEquiv
                </answertest>
                <sans>
                    {answer_name}
                </sans>
                <tans>
                    teacher
                </tans>
            </node>
        </prt>
        """

    return f"""
    <quiz>
        <question type="stack">
            <questiontext>
                <text><![CDATA[
                    {question_text}
                ]]></text>
            </questiontext>

            {prt_xml}
        </question>
    </quiz>
    """


def test_single_input_question_is_one_task() -> None:
    xml = make_question(
        """
        <p>Simplify the expression.</p>
        <p>
            8^5 * 8^0 =
            [[input:ans1]]
            [[feedback:prt1]]
        </p>
        """,
        [
            (
                "prt1",
                "ans1",
            )
        ],
    )

    result = extract_adaptive_tasks(
        question_id="207419",
        question_xml=xml,
    )

    assert result.task_count == 1
    assert result.is_multi_part is False

    task = result.tasks[0]

    assert task.input_names == [
        "ans1"
    ]

    assert task.prt_names == [
        "prt1"
    ]


def test_three_inputs_in_same_expression_stay_together() -> None:
    xml = make_question(
        """
        <p>
            Write the number in its
            simplest index form.
        </p>

        <p>
            108 =
            [[input:ans1]]
            times
            [[input:ans2]]
            ^
            [[input:ans3]]

            [[feedback:prt1]]
            [[feedback:prt2]]
            [[feedback:prt3]]
        </p>
        """,
        [
            (
                "prt1",
                "ans1",
            ),
            (
                "prt2",
                "ans2",
            ),
            (
                "prt3",
                "ans3",
            ),
        ],
    )

    result = extract_adaptive_tasks(
        question_id="206819",
        question_xml=xml,
    )

    assert result.task_count == 1

    task = result.tasks[0]

    assert task.input_names == [
        "ans1",
        "ans2",
        "ans3",
    ]

    assert task.prt_names == [
        "prt1",
        "prt2",
        "prt3",
    ]


def test_two_blanks_in_same_equation_stay_together() -> None:
    xml = make_question(
        """
        <p>
            Complete the equation.
        </p>

        <p>
            4 ^ [[input:ans1]]
            =
            1 / 4^3
            =
            4^2 / 4 ^ [[input:ans2]]

            [[feedback:prt1]]
            [[feedback:prt2]]
        </p>
        """,
        [
            (
                "prt1",
                "ans1",
            ),
            (
                "prt2",
                "ans2",
            ),
        ],
    )

    result = extract_adaptive_tasks(
        question_id="207420",
        question_xml=xml,
    )

    assert result.task_count == 1

    assert (
        result.tasks[0].input_names
        == [
            "ans1",
            "ans2",
        ]
    )


def test_four_separate_parts_become_four_tasks() -> None:
    xml = make_question(
        """
        <p>
            Simplify the following expressions.
        </p>

        <p>
            (a) 2^3 * 2^4 =
            [[input:ans1]] ^
            [[input:ans2]]
            [[feedback:prt1]]
            [[feedback:prt2]]
        </p>

        <p>
            (b) 5^8 / 5^3 =
            [[input:ans3]] ^
            [[input:ans4]]
            [[feedback:prt3]]
            [[feedback:prt4]]
        </p>

        <p>
            (c) (3^2)^4 =
            [[input:ans5]] ^
            [[input:ans6]]
            [[feedback:prt5]]
            [[feedback:prt6]]
        </p>

        <p>
            (d) 7^-3 =
            [[input:ans7]] ^
            [[input:ans8]]
            [[feedback:prt7]]
            [[feedback:prt8]]
        </p>
        """,
        [
            ("prt1", "ans1"),
            ("prt2", "ans2"),
            ("prt3", "ans3"),
            ("prt4", "ans4"),
            ("prt5", "ans5"),
            ("prt6", "ans6"),
            ("prt7", "ans7"),
            ("prt8", "ans8"),
        ],
    )

    result = extract_adaptive_tasks(
        question_id="206946",
        question_xml=xml,
    )

    assert result.task_count == 4
    assert result.is_multi_part is True

    assert [
        task.task_id
        for task in result.tasks
    ] == [
        "206946::a",
        "206946::b",
        "206946::c",
        "206946::d",
    ]

    assert (
        result.tasks[0].input_names
        == [
            "ans1",
            "ans2",
        ]
    )

    assert (
        result.tasks[1].input_names
        == [
            "ans3",
            "ans4",
        ]
    )

    assert (
        result.tasks[2].input_names
        == [
            "ans5",
            "ans6",
        ]
    )

    assert (
        result.tasks[3].input_names
        == [
            "ans7",
            "ans8",
        ]
    )


def test_correct_prts_are_attached_to_each_part() -> None:
    xml = make_question(
        """
        <p>Work these out.</p>

        <p>
            (a)
            [[input:ans1]]
            [[input:ans2]]
        </p>

        <p>
            (b)
            [[input:ans3]]
            [[input:ans4]]
        </p>
        """,
        [
            ("prt1", "ans1"),
            ("prt2", "ans2"),
            ("prt3", "ans3"),
            ("prt4", "ans4"),
        ],
    )

    result = extract_adaptive_tasks(
        question_id="multi",
        question_xml=xml,
    )

    assert (
        result.tasks[0].prt_names
        == [
            "prt1",
            "prt2",
        ]
    )

    assert (
        result.tasks[1].prt_names
        == [
            "prt3",
            "prt4",
        ]
    )


def test_intro_is_included_with_each_task() -> None:
    xml = make_question(
        """
        <p>
            Simplify each expression
            in index form.
        </p>

        <p>
            (a)
            [[input:ans1]]
        </p>

        <p>
            (b)
            [[input:ans2]]
        </p>
        """,
        [
            ("prt1", "ans1"),
            ("prt2", "ans2"),
        ],
    )

    result = extract_adaptive_tasks(
        question_id="example",
        question_xml=xml,
    )

    assert (
        "Simplify each expression"
        in result.tasks[0].prompt_template
    )

    assert (
        "Simplify each expression"
        in result.tasks[1].prompt_template
    )


def test_question_without_inputs_is_rejected() -> None:
    xml = make_question(
        """
        <p>
            This question has no answer.
        </p>
        """,
        [],
    )

    with pytest.raises(
        AdaptiveTaskExtractionError,
        match="no STACK answer inputs",
    ):
        extract_adaptive_tasks(
            question_id="bad",
            question_xml=xml,
        )

def test_shared_prt_can_reference_inputs_via_feedback_variables() -> None:
    xml = """
    <quiz>
        <question type="stack">
            <questiontext>
                <text><![CDATA[
                    <p>
                        Drag the two points.
                    </p>

                    <p>
                        [[input:ans1]]
                        [[input:ans2]]
                        [[feedback:prt1]]
                    </p>
                ]]></text>
            </questiontext>

            <prt>
                <name>prt1</name>

                <feedbackvariables>
                    <text>
                        sans_equation:
                        y=(ans1[2]-ans2[2])
                        /(ans1[1]-ans2[1])
                        *(x-ans1[1])
                        +ans1[2];
                    </text>
                </feedbackvariables>

                <node>
                    <name>0</name>
                    <answertest>
                        AlgEquiv
                    </answertest>
                    <sans>
                        sans_equation
                    </sans>
                    <tans>
                        equation
                    </tans>
                </node>
            </prt>
        </question>
    </quiz>
    """

    result = extract_adaptive_tasks(
        question_id="207067",
        question_xml=xml,
    )

    assert result.task_count == 1

    task = result.tasks[0]

    assert task.input_names == [
        "ans1",
        "ans2",
    ]

    assert task.prt_names == [
        "prt1"
    ]


def test_extracts_multi_prt_hidden_inputs_as_one_interactive_task():
    xml = """
    <quiz>
        <question type="stack">
            <name>
                <text>
                    Four-input interactive graph
                </text>
            </name>

            <questiontext format="html">
                <text><![CDATA[
                    <p>
                        Plot two relations on the
                        same Cartesian plane.
                    </p>

                    <p>
                        [[jsxgraph
                        input-ref-ans1="sA1"
                        input-ref-ans2="sA2"
                        input-ref-ans3="sB1"
                        input-ref-ans4="sB2"]]

                        stack_jxg.bind_point(
                            sA1,
                            a1
                        );

                        stack_jxg.bind_point(
                            sA2,
                            a2
                        );

                        stack_jxg.bind_point(
                            sB1,
                            b1
                        );

                        stack_jxg.bind_point(
                            sB2,
                            b2
                        );

                        [[/jsxgraph]]
                    </p>

                    <p style="visibility:hidden">
                        [[input:ans1]]
                        [[validation:ans1]]
                    </p>

                    <p style="visibility:hidden">
                        [[input:ans2]]
                        [[validation:ans2]]
                    </p>

                    <p style="visibility:hidden">
                        [[input:ans3]]
                        [[validation:ans3]]
                    </p>

                    <p style="visibility:hidden">
                        [[input:ans4]]
                        [[validation:ans4]]
                    </p>
                ]]></text>
            </questiontext>

            <prt>
                <name>prt1</name>

                <feedbackvariables>
                    <text>
                        errorA:
                        (ans1[1]-ans2[1])^2
                        +
                        (ans1[2]-ans2[2])^2;
                    </text>
                </feedbackvariables>

                <node>
                    <name>0</name>
                    <answertest>
                        NumAbsolute
                    </answertest>
                    <sans>
                        errorA
                    </sans>
                    <tans>0</tans>
                </node>
            </prt>

            <prt>
                <name>prt2</name>

                <feedbackvariables>
                    <text>
                        errorB:
                        (ans3[1]-ans4[1])^2
                        +
                        (ans3[2]-ans4[2])^2;
                    </text>
                </feedbackvariables>

                <node>
                    <name>0</name>
                    <answertest>
                        NumAbsolute
                    </answertest>
                    <sans>
                        errorB
                    </sans>
                    <tans>0</tans>
                </node>
            </prt>
        </question>
    </quiz>
    """

    result = extract_adaptive_tasks(
        question_id="QLIN-05",
        question_xml=xml,
    )

    assert result.task_count == 1

    task = result.tasks[0]

    assert task.input_names == [
        "ans1",
        "ans2",
        "ans3",
        "ans4",
    ]

    assert task.prt_names == [
        "prt1",
        "prt2",
    ]


def test_merges_hidden_jsxgraph_inputs_with_visible_followup():
    xml = """
    <quiz>
        <question type="stack">
            <name>
                <text>
                    Interactive graph with solution
                </text>
            </name>

            <questiontext format="html">
                <text><![CDATA[
                    <p>
                        Graph both equations and then
                        report their intersection.
                    </p>

                    <p>
                        [[jsxgraph
                        input-ref-ans1="sA1"
                        input-ref-ans2="sA2"
                        input-ref-ans3="sB1"
                        input-ref-ans4="sB2"]]

                        stack_jxg.bind_point(
                            sA1,
                            a1
                        );

                        stack_jxg.bind_point(
                            sA2,
                            a2
                        );

                        stack_jxg.bind_point(
                            sB1,
                            b1
                        );

                        stack_jxg.bind_point(
                            sB2,
                            b2
                        );

                        [[/jsxgraph]]
                    </p>

                    <p style="visibility:hidden">
                        [[input:ans1]]
                        [[validation:ans1]]
                    </p>

                    <p style="visibility:hidden">
                        [[input:ans2]]
                        [[validation:ans2]]
                    </p>

                    <p style="visibility:hidden">
                        [[input:ans3]]
                        [[validation:ans3]]
                    </p>

                    <p style="visibility:hidden">
                        [[input:ans4]]
                        [[validation:ans4]]
                    </p>

                    <p>
                        Enter the common solution.

                        [[input:ans5]]
                        [[validation:ans5]]

                        [[feedback:prt3]]
                    </p>
                ]]></text>
            </questiontext>

            <prt>
                <name>prt1</name>
                <node>
                    <name>0</name>
                    <sans>
                        ans1 + ans2
                    </sans>
                    <tans>0</tans>
                </node>
            </prt>

            <prt>
                <name>prt2</name>
                <node>
                    <name>0</name>
                    <sans>
                        ans3 + ans4
                    </sans>
                    <tans>0</tans>
                </node>
            </prt>

            <prt>
                <name>prt3</name>
                <node>
                    <name>0</name>
                    <sans>ans5</sans>
                    <tans>solution</tans>
                </node>
            </prt>
        </question>
    </quiz>
    """

    result = extract_adaptive_tasks(
        question_id="interactive-followup",
        question_xml=xml,
    )

    assert result.task_count == 1

    task = result.tasks[0]

    assert task.input_names == [
        "ans1",
        "ans2",
        "ans3",
        "ans4",
        "ans5",
    ]

    assert task.prt_names == [
        "prt1",
        "prt2",
        "prt3",
    ]
