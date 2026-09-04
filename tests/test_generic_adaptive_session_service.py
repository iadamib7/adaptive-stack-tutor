from backend.app.integrations.stack_api.client import (
    StackEvaluationClient,
)

from backend.app.integrations.stack_api.models import (
    NormalizedStackResult,
    StackEvaluationRequest,
    StackPRTResult,
)

from backend.app.learning.adaptive_engine import (
    StackXmlQuestionBankImporter,
)

from backend.app.learning.adaptive_engine.session_service import (
    GenericAdaptiveSessionService,
)

from backend.app.learning.adaptive_engine.stack_runtime import (
    RenderedAdaptiveQuestion,
)


XML = """
<quiz>
  <question type="stack">
    <name>
      <text>Entry question</text>
    </name>
    <idnumber>Q1</idnumber>
    <questiontext format="html">
      <text>Entry</text>
    </questiontext>
  </question>

  <question type="stack">
    <name>
      <text>Targeted support</text>
    </name>
    <idnumber>Q2</idnumber>
    <questiontext format="html">
      <text>Support</text>
    </questiontext>
  </question>

  <question type="stack">
    <name>
      <text>General practice</text>
    </name>
    <idnumber>Q3</idnumber>
    <questiontext format="html">
      <text>General</text>
    </questiontext>
  </question>
</quiz>
"""


class FakeRenderer:
    def render(
        self,
        *,
        question_id: str,
        question_xml: str,
        seed: int,
    ) -> RenderedAdaptiveQuestion:
        return RenderedAdaptiveQuestion(
            question_id=question_id,
            seed=seed,
            html=(
                f"<p>{question_id}</p>"
            ),
            inputs={
                "ans1": {}
            },
        )


class SignErrorClient(
    StackEvaluationClient
):
    def evaluate(
        self,
        request:
            StackEvaluationRequest,
    ) -> NormalizedStackResult:
        return NormalizedStackResult(
            question_id=(
                request.question_id
            ),
            valid=True,
            seed=request.seed,
            prts=[
                StackPRTResult(
                    prt_name="prt1",
                    score=0.0,
                    penalty=0.1,
                    answer_notes=[
                        "prt1-1-F",
                        "prt1-2-T",
                    ],
                )
            ],
        )


def build_service():
    importer = (
        StackXmlQuestionBankImporter()
    )

    bank = importer.import_text(
        XML
    )

    questions = (
        bank.adaptive_questions()
    )

    for question in questions:
        if question.question_id == "Q2":
            object.__setattr__(
                question,
                "supports",
                ("sign_error",),
            )

        if question.question_id == "Q3":
            object.__setattr__(
                question,
                "difficulty",
                0.4,
            )

    return GenericAdaptiveSessionService(
        question_bank=bank,
        evaluation_client=(
            SignErrorClient()
        ),
        renderer=FakeRenderer(),
        outcome_aliases={
            "Q1": {
                (
                    "prt1:"
                    "prt1-1-F|prt1-2-T"
                ): "sign_error",
            }
        },
    )


def test_session_starts_from_imported_bank() -> None:
    service = build_service()

    session = service.start(
        learner_id=1
    )

    assert session.question_id == "Q1"

    assert session.html == (
        "<p>Q1</p>"
    )


def test_stack_prt_changes_next_question() -> None:
    service = build_service()

    first = service.start(
        learner_id=2
    )

    assert first.question_id == "Q1"

    second = service.submit_answer(
        learner_id=2,
        student_answers={
            "ans1": "wrong",
        },
    )

    assert second.question_id == "Q2"

    assert (
        second.previous_outcome
        == "sign_error"
    )


def test_same_evidence_is_deterministic() -> None:
    service_a = build_service()
    service_b = build_service()

    service_a.start(
        learner_id=10
    )

    service_b.start(
        learner_id=10
    )

    next_a = (
        service_a.submit_answer(
            learner_id=10,
            student_answers={
                "ans1": "wrong",
            },
        )
    )

    next_b = (
        service_b.submit_answer(
            learner_id=10,
            student_answers={
                "ans1": "wrong",
            },
        )
    )

    assert (
        next_a.question_id
        == next_b.question_id
        == "Q2"
    )

    assert (
        next_a.seed
        == next_b.seed
    )


def test_service_has_no_curriculum_input() -> None:
    service = build_service()

    assert not hasattr(
        service,
        "curriculum"
    )

    assert not hasattr(
        service,
        "concept_id"
    )

    assert not hasattr(
        service,
        "knowledge_graph"
    )


METADATA_JSON = """
{
  "questions": {
    "Q1": {
      "difficulty": 0.0,
      "prt_outcomes": {
        "prt1:prt1-1-F|prt1-2-T":
          "sign_error"
      }
    },
    "Q2": {
      "difficulty": -0.4,
      "supports": [
        "sign_error"
      ]
    },
    "Q3": {
      "difficulty": 0.4
    }
  }
}
"""


def test_from_xml_applies_metadata_manifest() -> None:
    service = (
        GenericAdaptiveSessionService
        .from_xml(
            xml_text=XML,
            metadata_json=(
                METADATA_JSON
            ),
            evaluation_client=(
                SignErrorClient()
            ),
            renderer=FakeRenderer(),
        )
    )

    q2 = (
        service.question_bank
        .require(
            "Q2"
        )
        .adaptive_question
    )

    assert q2.supports == (
        "sign_error",
    )

    assert q2.difficulty == -0.4


def test_from_xml_metadata_drives_prt_branch() -> None:
    service = (
        GenericAdaptiveSessionService
        .from_xml(
            xml_text=XML,
            metadata_json=(
                METADATA_JSON
            ),
            evaluation_client=(
                SignErrorClient()
            ),
            renderer=FakeRenderer(),
        )
    )

    first = service.start(
        learner_id=500
    )

    assert first.question_id == "Q1"

    second = service.submit_answer(
        learner_id=500,
        student_answers={
            "ans1": "wrong",
        },
    )

    assert (
        second.previous_outcome
        == "sign_error"
    )

    assert second.question_id == "Q2"


def test_from_xml_metadata_is_optional() -> None:
    service = (
        GenericAdaptiveSessionService
        .from_xml(
            xml_text=XML,
            evaluation_client=(
                SignErrorClient()
            ),
            renderer=FakeRenderer(),
        )
    )

    assert (
        service.question_bank.count
        == 3
    )



def test_from_xml_builds_adaptive_graph_automatically(
) -> None:
    xml = """
    <quiz>
      <question type="category">
        <category>
          <text>
            $course$/top/Functions
          </text>
        </category>
      </question>

      <!-- Deliberately harder question first. -->
      <question type="stack">
        <name>
          <text>Advanced functions</text>
        </name>
        <idnumber>Q5</idnumber>

        <input>
          <name>ans1</name>
        </input>
        <input>
          <name>ans2</name>
        </input>
        <input>
          <name>ans3</name>
        </input>

        <prt>
          <name>prt1</name>

          <node>
            <name>0</name>
          </node>

          <node>
            <name>1</name>
          </node>

          <node>
            <name>2</name>
          </node>

          <node>
            <name>3</name>
          </node>
        </prt>
      </question>

      <!-- Simpler question appears later. -->
      <question type="stack">
        <name>
          <text>Function basics</text>
        </name>
        <idnumber>Q1</idnumber>

        <input>
          <name>ans1</name>
        </input>

        <prt>
          <name>prt1</name>

          <node>
            <name>0</name>
          </node>
        </prt>
      </question>
    </quiz>
    """

    service = (
        GenericAdaptiveSessionService
        .from_xml(
            xml_text=xml,
            evaluation_client=(
                SignErrorClient()
            ),
            renderer=FakeRenderer(),
        )
    )

    q1 = (
        service.question_bank
        .require(
            "Q1"
        )
        .adaptive_question
    )

    q5 = (
        service.question_bank
        .require(
            "Q5"
        )
        .adaptive_question
    )

    assert q1.entry_point is True
    assert q5.entry_point is False

    assert (
        q1.difficulty
        < q5.difficulty
    )


def test_from_xml_does_not_use_xml_order_as_entry(
) -> None:
    xml = """
    <quiz>
      <question type="category">
        <category>
          <text>
            $course$/top/Functions
          </text>
        </category>
      </question>

      <question type="stack">
        <name>
          <text>Hard first</text>
        </name>
        <idnumber>Q9</idnumber>

        <input>
          <name>ans1</name>
        </input>
        <input>
          <name>ans2</name>
        </input>
        <input>
          <name>ans3</name>
        </input>

        <prt>
          <name>prt1</name>
          <node>
            <name>0</name>
          </node>
          <node>
            <name>1</name>
          </node>
          <node>
            <name>2</name>
          </node>
        </prt>
      </question>

      <question type="stack">
        <name>
          <text>Simple later</text>
        </name>
        <idnumber>Q1</idnumber>

        <input>
          <name>ans1</name>
        </input>

        <prt>
          <name>prt1</name>
          <node>
            <name>0</name>
          </node>
        </prt>
      </question>
    </quiz>
    """

    service = (
        GenericAdaptiveSessionService
        .from_xml(
            xml_text=xml,
            evaluation_client=(
                SignErrorClient()
            ),
            renderer=FakeRenderer(),
        )
    )

    decision = service.engine.start(
        learner_id=99
    )

    assert decision is not None

    assert (
        decision.question.question_id
        == "Q1"
    )


def test_explicit_metadata_overrides_inferred_graph(
) -> None:
    xml = """
    <quiz>
      <question type="category">
        <category>
          <text>
            $course$/top/Functions
          </text>
        </category>
      </question>

      <question type="stack">
        <name>
          <text>Question one</text>
        </name>
        <idnumber>Q1</idnumber>

        <input>
          <name>ans1</name>
        </input>

        <prt>
          <name>prt1</name>
          <node>
            <name>0</name>
          </node>
        </prt>
      </question>
    </quiz>
    """

    metadata = """
    {
      "questions": {
        "Q1": {
          "difficulty": 1.5,
          "entry_point": true,
          "skills": [
            "instructor-skill"
          ]
        }
      }
    }
    """

    service = (
        GenericAdaptiveSessionService
        .from_xml(
            xml_text=xml,
            evaluation_client=(
                SignErrorClient()
            ),
            renderer=FakeRenderer(),
            metadata_json=metadata,
        )
    )

    question = (
        service.question_bank
        .require(
            "Q1"
        )
        .adaptive_question
    )

    assert question.difficulty == 1.5

    assert question.skills == (
        "instructor-skill",
    )

    assert question.entry_point is True
