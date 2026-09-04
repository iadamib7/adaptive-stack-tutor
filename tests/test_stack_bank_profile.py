from backend.app.learning.adaptive_engine.bank_profile import (
    StackBankProfiler,
)


XML = """
<quiz>
  <question type="category">
    <category>
      <text>
        $course$/top/Functions/
        Rational Expressions
      </text>
    </category>
  </question>

  <question type="stack">
    <name>
      <text>Rational expression</text>
    </name>

    <idnumber>Q1</idnumber>

    <input>
      <name>ans1</name>
      <type>algebraic</type>
    </input>

    <input>
      <name>ans2</name>
      <type>algebraic</type>
    </input>

    <prt>
      <name>prt1</name>

      <node>
        <name>0</name>
        <answertest>AlgEquiv</answertest>

        <trueanswernote>
          prt1-1-T
        </trueanswernote>

        <falseanswernote>
          prt1-1-F
        </falseanswernote>

        <truefeedback format="html">
          <text></text>
        </truefeedback>

        <falsefeedback format="html">
          <text></text>
        </falsefeedback>
      </node>
    </prt>

    <prt>
      <name>prt2</name>

      <node>
        <name>0</name>
        <answertest>AlgEquiv</answertest>

        <trueanswernote>
          prt2-1-T
        </trueanswernote>

        <falseanswernote>
          prt2-1-F
        </falseanswernote>

        <falsefeedback format="html">
          <text></text>
        </falsefeedback>
      </node>

      <node>
        <name>1</name>
        <answertest>AlgEquiv</answertest>

        <trueanswernote>
          prt2-2-T
        </trueanswernote>

        <falseanswernote>
          prt2-2-F
        </falseanswernote>

        <truefeedback format="html">
          <text>
            &lt;p&gt;You may have forgotten
            the negative sign.&lt;/p&gt;
          </text>
        </truefeedback>

        <falsefeedback format="html">
          <text></text>
        </falsefeedback>
      </node>
    </prt>

    <deployedseed>100</deployedseed>
    <deployedseed>200</deployedseed>
    <deployedseed>300</deployedseed>
  </question>
</quiz>
"""


def build_profile():
    return StackBankProfiler().profile_text(
        XML
    )


def test_profiles_stack_question(
) -> None:
    profile = build_profile()

    assert profile.count == 1

    question = profile.require(
        "Q1"
    )

    assert (
        question.title
        == "Rational expression"
    )


def test_preserves_bank_local_category(
) -> None:
    question = build_profile().require(
        "Q1"
    )

    assert question.category_path is not None

    assert (
        "Rational Expressions"
        in question.category_path
    )


def test_extracts_inputs(
) -> None:
    question = build_profile().require(
        "Q1"
    )

    assert question.input_names == (
        "ans1",
        "ans2",
    )


def test_extracts_prts_and_nodes(
) -> None:
    question = build_profile().require(
        "Q1"
    )

    assert question.prt_names == (
        "prt1",
        "prt2",
    )

    assert (
        question.prt_node_count
        == 3
    )


def test_extracts_answer_note_branches(
) -> None:
    question = build_profile().require(
        "Q1"
    )

    notes = {
        branch.true_answer_note
        for branch in question.branches
    }

    assert "prt1-1-T" in notes
    assert "prt2-2-T" in notes


def test_preserves_instructor_feedback(
) -> None:
    question = build_profile().require(
        "Q1"
    )

    feedback = [
        branch.true_feedback
        for branch in question.branches
        if branch.true_feedback
    ]

    assert feedback == [
        "You may have forgotten "
        "the negative sign."
    ]

    assert (
        question.has_diagnostic_feedback
        is True
    )


def test_counts_deployed_variants(
) -> None:
    question = build_profile().require(
        "Q1"
    )

    assert (
        question.deployed_seed_count
        == 3
    )


def test_category_does_not_define_sequence(
) -> None:
    profile = build_profile()

    # The profiler describes structure only.
    # It creates no next-question field and
    # therefore cannot silently turn Moodle
    # XML order into an adaptive route.
    question = profile.require(
        "Q1"
    )

    assert not hasattr(
        question,
        "next_question_id"
    )

    assert not hasattr(
        question,
        "sequence_number"
    )


def test_profile_does_not_invent_curriculum(
) -> None:
    question = build_profile().require(
        "Q1"
    )

    assert not hasattr(
        question,
        "curriculum"
    )

    assert not hasattr(
        question,
        "standard"
    )

    assert not hasattr(
        question,
        "concept_id"
    )


def test_profile_does_not_invent_misconception_label(
) -> None:
    question = build_profile().require(
        "Q1"
    )

    branch = next(
        branch
        for branch in question.branches
        if branch.true_answer_note
        == "prt2-2-T"
    )

    assert (
        "negative sign"
        in branch.true_feedback.lower()
    )

    # We preserve what the instructor wrote,
    # but we do not silently claim a semantic
    # misconception classification.
    assert not hasattr(
        branch,
        "misconception"
    )
