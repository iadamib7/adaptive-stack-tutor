from backend.app.learning.adaptive_engine.session_service import (
    GenericAdaptiveSessionService,
)


DEPLOYED_XML = """
<quiz>
  <question type="stack">
    <name>
      <text>Example</text>
    </name>

    <deployedseed>
      369312014
    </deployedseed>

    <deployedseed>
      1781965065
    </deployedseed>

    <deployedseed>
      956142585
    </deployedseed>
  </question>
</quiz>
"""


NO_DEPLOYED_XML = """
<quiz>
  <question type="stack">
    <name>
      <text>Example</text>
    </name>
  </question>
</quiz>
"""


def test_uses_real_deployed_seed_when_available(
) -> None:
    seed = (
        GenericAdaptiveSessionService
        ._seed_for_question(
            learner_id=1,
            question_id="Q1",
            question_xml=DEPLOYED_XML,
        )
    )

    assert seed in {
        369312014,
        1781965065,
        956142585,
    }


def test_deployed_seed_selection_is_deterministic(
) -> None:
    first = (
        GenericAdaptiveSessionService
        ._seed_for_question(
            learner_id=7,
            question_id="Q1",
            question_xml=DEPLOYED_XML,
        )
    )

    second = (
        GenericAdaptiveSessionService
        ._seed_for_question(
            learner_id=7,
            question_id="Q1",
            question_xml=DEPLOYED_XML,
        )
    )

    assert first == second


def test_seed_is_valid_for_different_learners(
) -> None:
    allowed = {
        369312014,
        1781965065,
        956142585,
    }

    for learner_id in range(
        1,
        20,
    ):
        seed = (
            GenericAdaptiveSessionService
            ._seed_for_question(
                learner_id=learner_id,
                question_id="Q1",
                question_xml=DEPLOYED_XML,
            )
        )

        assert seed in allowed


def test_question_without_deployed_seeds_uses_fallback(
) -> None:
    seed = (
        GenericAdaptiveSessionService
        ._seed_for_question(
            learner_id=3,
            question_id="Q1",
            question_xml=(
                NO_DEPLOYED_XML
            ),
        )
    )

    expected = (
        GenericAdaptiveSessionService
        ._stable_seed(
            learner_id=3,
            question_id="Q1",
        )
    )

    assert seed == expected


def test_bad_deployed_seed_is_ignored(
) -> None:
    xml = """
    <quiz>
      <question type="stack">
        <deployedseed>
          not-a-number
        </deployedseed>

        <deployedseed>
          429836441
        </deployedseed>
      </question>
    </quiz>
    """

    seed = (
        GenericAdaptiveSessionService
        ._seed_for_question(
            learner_id=1,
            question_id="Q2",
            question_xml=xml,
        )
    )

    assert seed == 429836441


def test_empty_deployed_seed_is_ignored(
) -> None:
    xml = """
    <quiz>
      <question type="stack">
        <deployedseed>
        </deployedseed>
      </question>
    </quiz>
    """

    seed = (
        GenericAdaptiveSessionService
        ._seed_for_question(
            learner_id=4,
            question_id="Q3",
            question_xml=xml,
        )
    )

    expected = (
        GenericAdaptiveSessionService
        ._stable_seed(
            learner_id=4,
            question_id="Q3",
        )
    )

    assert seed == expected
