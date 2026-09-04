from backend.app.integrations.stack_api.models import (
    NormalizedStackResult,
    StackPRTResult,
)

from backend.app.learning.adaptive_engine.adaptive_graph_builder import (
    StackAdaptiveGraphBuilder,
)

from backend.app.learning.adaptive_engine.bank_profile import (
    StackBankProfiler,
)

from backend.app.learning.adaptive_engine.engine import (
    CurriculumIndependentAdaptiveEngine,
)

from backend.app.learning.adaptive_engine.question_bank import (
    StackXmlQuestionBankImporter,
)

from backend.app.learning.adaptive_engine.session_service import (
    GenericAdaptiveSessionService,
)

from backend.app.learning.adaptive_engine.stack_evidence import (
    StackEvidenceAdapter,
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

  <!--
      Q1 is deliberately first in XML but is
      structurally more complex.
  -->
  <question type="stack">
    <name>
      <text>Rational expression challenge</text>
    </name>

    <idnumber>Q1</idnumber>

    <input>
      <name>ans1</name>
    </input>

    <prt>
      <name>prt1</name>

      <node>
        <name>0</name>

        <trueanswernote>
          prt1-1-T
        </trueanswernote>

        <falseanswernote>
          prt1-1-F
        </falseanswernote>
      </node>

      <node>
        <name>1</name>

        <trueanswernote>
          prt1-2-T
        </trueanswernote>

        <falseanswernote>
          prt1-2-F
        </falseanswernote>

        <truefeedback format="html">
          <text>
            &lt;p&gt;
            Check the negative sign.
            &lt;/p&gt;
          </text>
        </truefeedback>
      </node>
    </prt>
  </question>

  <!--
      Q2 is structurally simpler and appears
      later in XML.
  -->
  <question type="stack">
    <name>
      <text>Rational expression support</text>
    </name>

    <idnumber>Q2</idnumber>

    <input>
      <name>ans1</name>
    </input>

    <prt>
      <name>prt1</name>

      <node>
        <name>0</name>

        <trueanswernote>
          prt1-1-T
        </trueanswernote>

        <falseanswernote>
          prt1-1-F
        </falseanswernote>
      </node>
    </prt>
  </question>
</quiz>
"""


def build_graph():
    importer = (
        StackXmlQuestionBankImporter()
    )

    bank = importer.import_text(
        XML
    )

    profile = (
        StackBankProfiler()
        .profile_text(
            XML
        )
    )

    return (
        StackAdaptiveGraphBuilder()
        .build(
            bank=bank,
            profile=profile,
        )
    )


def test_graph_creates_support_from_authored_feedback(
) -> None:
    result = build_graph()

    q2 = result.bank.require(
        "Q2"
    ).adaptive_question

    assert q2.supports

    aliases = (
        result.outcome_aliases[
            "Q1"
        ]
    )

    assert (
        "note:prt1-2-T"
        in aliases
    )

    support_key = aliases[
        "note:prt1-2-T"
    ]

    assert support_key in q2.supports


def test_stack_evidence_resolves_feedback_note_alias(
) -> None:
    result = build_graph()

    aliases = (
        result.outcome_aliases[
            "Q1"
        ]
    )

    evidence = (
        StackEvidenceAdapter()
        .from_normalized_result(
            result=NormalizedStackResult(
                question_id="Q1",
                valid=True,
                seed=123,
                prts=[
                    StackPRTResult(
                        prt_name="prt1",
                        score=0.0,
                        penalty=0.0,
                        answer_notes=[
                            "prt1-1-F",
                            "prt1-2-T",
                        ],
                    )
                ],
            ),
            outcome_aliases=aliases,
        )
    )

    assert (
        evidence.prt_outcome
        == aliases[
            "note:prt1-2-T"
        ]
    )


def test_real_prt_branch_drives_figure8_cycle(
) -> None:
    result = build_graph()

    engine = (
        CurriculumIndependentAdaptiveEngine(
            result.bank.adaptive_questions()
        )
    )

    # XML says Q1 first.
    #
    # Adaptive graph chooses simpler Q2 instead.
    first = engine.start(
        learner_id=1
    )

    assert first is not None

    assert (
        first.question.question_id
        == "Q2"
    )

    # Master the support/basic skill first.
    next_decision = engine.submit(
        learner_id=1,
        evidence=(
            StackEvidenceAdapter()
            .from_normalized_result(
                result=NormalizedStackResult(
                    question_id="Q2",
                    valid=True,
                    seed=111,
                    prts=[
                        StackPRTResult(
                            prt_name="prt1",
                            score=1.0,
                            penalty=0.0,
                            answer_notes=[
                                "prt1-1-T"
                            ],
                        )
                    ],
                )
            )
        ),
    )

    assert next_decision is not None

    assert (
        next_decision.question.question_id
        == "Q1"
    )

    # Q1 now triggers the real feedback-bearing
    # PRT branch.
    diagnostic_evidence = (
        StackEvidenceAdapter()
        .from_normalized_result(
            result=NormalizedStackResult(
                question_id="Q1",
                valid=True,
                seed=222,
                prts=[
                    StackPRTResult(
                        prt_name="prt1",
                        score=0.0,
                        penalty=0.0,
                        answer_notes=[
                            "prt1-1-F",
                            "prt1-2-T",
                        ],
                    )
                ],
            ),
            outcome_aliases=(
                result.outcome_aliases[
                    "Q1"
                ]
            ),
        )
    )

    remediation = engine.submit(
        learner_id=1,
        evidence=diagnostic_evidence,
    )

    assert remediation is not None

    assert (
        remediation.question.question_id
        == "Q2"
    )

    assert (
        remediation.decision_type
        == "remediate"
    )

    assert (
        remediation.return_target_question_id
        == "Q1"
    )

    # Successful remediation must return the
    # learner to Q1 before normal progression.
    reassessment = engine.submit(
        learner_id=1,
        evidence=(
            StackEvidenceAdapter()
            .from_normalized_result(
                result=NormalizedStackResult(
                    question_id="Q2",
                    valid=True,
                    seed=333,
                    prts=[
                        StackPRTResult(
                            prt_name="prt1",
                            score=1.0,
                            penalty=0.0,
                            answer_notes=[
                                "prt1-1-T"
                            ],
                        )
                    ],
                )
            )
        ),
    )

    assert reassessment is not None

    assert (
        reassessment.question.question_id
        == "Q1"
    )

    assert (
        reassessment.decision_type
        == "reassess"
    )


def test_from_xml_exposes_automatic_prt_aliases(
) -> None:
    # No rendering or grading is required for this
    # construction test, so simple objects are enough.
    service = (
        GenericAdaptiveSessionService
        .from_xml(
            xml_text=XML,
            evaluation_client=object(),
            renderer=object(),
        )
    )

    aliases = (
        service.outcome_aliases[
            "Q1"
        ]
    )

    assert (
        "note:prt1-2-T"
        in aliases
    )

    q2 = (
        service.question_bank
        .require(
            "Q2"
        )
        .adaptive_question
    )

    assert (
        aliases[
            "note:prt1-2-T"
        ]
        in q2.supports
    )
