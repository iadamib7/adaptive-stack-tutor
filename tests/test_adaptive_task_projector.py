from xml.etree import ElementTree as ET

from backend.app.learning.adaptive_tasks.models import (
    AdaptiveTask,
)
from backend.app.learning.adaptive_tasks.projector import (
    project_question_xml_for_task,
)


def source_xml() -> str:
    return """
    <quiz>
        <question type="stack">
            <questiontext>
                <text><![CDATA[
                    <p>Express these in index form.</p>

                    <p>
                        (i)
                        [[input:ans1]] ^
                        [[input:ans2]]
                        [[validation:ans1]]
                        [[validation:ans2]]
                        [[feedback:prt1]]
                        [[feedback:prt2]]
                    </p>

                    <p>
                        (ii)
                        [[input:ans3]] ^
                        [[input:ans4]]
                        [[feedback:prt3]]
                        [[feedback:prt4]]
                    </p>
                ]]></text>
            </questiontext>

            <questionvariables>
                <text>
                    a:10;
                    b:4;
                </text>
            </questionvariables>

            <input>
                <name>ans1</name>
                <type>algebraic</type>
                <tans>a</tans>
            </input>

            <input>
                <name>ans2</name>
                <type>algebraic</type>
                <tans>b</tans>
            </input>

            <input>
                <name>ans3</name>
                <type>algebraic</type>
                <tans>a</tans>
            </input>

            <input>
                <name>ans4</name>
                <type>algebraic</type>
                <tans>b</tans>
            </input>

            <prt>
                <name>prt1</name>
                <node>
                    <name>0</name>
                    <sans>ans1</sans>
                    <tans>a</tans>
                </node>
            </prt>

            <prt>
                <name>prt2</name>
                <node>
                    <name>0</name>
                    <sans>ans2</sans>
                    <tans>b</tans>
                </node>
            </prt>

            <prt>
                <name>prt3</name>
                <node>
                    <name>0</name>
                    <sans>ans3</sans>
                    <tans>a</tans>
                </node>
            </prt>

            <prt>
                <name>prt4</name>
                <node>
                    <name>0</name>
                    <sans>ans4</sans>
                    <tans>b</tans>
                </node>
            </prt>

            <qtest>
                <testcase>1</testcase>
            </qtest>
        </question>
    </quiz>
    """


def part_one_task() -> AdaptiveTask:
    return AdaptiveTask(
        task_id="206793::i",
        source_question_id="206793",
        display_order=1,
        prompt_template=(
            "<p>Express these in index form.</p>"
            "<p>(i) "
            "[[input:ans1]] ^ "
            "[[input:ans2]] "
            "[[validation:ans1]] "
            "[[validation:ans2]] "
            "[[feedback:prt1]] "
            "[[feedback:prt2]]"
            "</p>"
        ),
        input_names=[
            "ans1",
            "ans2",
        ],
        prt_names=[
            "prt1",
            "prt2",
        ],
        part_label="i",
    )


def test_projection_keeps_only_task_inputs() -> None:
    projected = (
        project_question_xml_for_task(
            question_xml=source_xml(),
            task=part_one_task(),
        )
    )

    root = ET.fromstring(
        projected
    )

    names = [
        element.findtext("name")
        for element in root.findall(
            ".//input"
        )
    ]

    assert names == [
        "ans1",
        "ans2",
    ]


def test_projection_keeps_only_task_prts() -> None:
    projected = (
        project_question_xml_for_task(
            question_xml=source_xml(),
            task=part_one_task(),
        )
    )

    root = ET.fromstring(
        projected
    )

    names = [
        element.findtext("name")
        for element in root.findall(
            ".//prt"
        )
    ]

    assert names == [
        "prt1",
        "prt2",
    ]


def test_projection_replaces_question_text() -> None:
    projected = (
        project_question_xml_for_task(
            question_xml=source_xml(),
            task=part_one_task(),
        )
    )

    root = ET.fromstring(
        projected
    )

    text = root.findtext(
        ".//questiontext/text"
    )

    assert text is not None

    assert "[[input:ans1]]" in text
    assert "[[input:ans2]]" in text

    assert "[[input:ans3]]" not in text
    assert "[[input:ans4]]" not in text


def test_projection_preserves_question_variables() -> None:
    projected = (
        project_question_xml_for_task(
            question_xml=source_xml(),
            task=part_one_task(),
        )
    )

    root = ET.fromstring(
        projected
    )

    variables = root.findtext(
        ".//questionvariables/text"
    )

    assert variables is not None
    assert "a:10" in variables
    assert "b:4" in variables


def test_projection_removes_qtests() -> None:
    projected = (
        project_question_xml_for_task(
            question_xml=source_xml(),
            task=part_one_task(),
        )
    )

    root = ET.fromstring(
        projected
    )

    assert root.find(
        ".//qtest"
    ) is None
