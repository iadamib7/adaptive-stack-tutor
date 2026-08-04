from pathlib import Path

import pytest

from backend.app.learning.sequencing.engine import (
    DeterministicSequencingEngine,
)
from backend.app.learning.sequencing.loader import (
    load_sequencing_map,
)
from backend.app.learning.sequencing.models import (
    SequencingAction,
)


MAP_PATH = Path(
    "examples/integration_demo/sequencing_map.json"
)


@pytest.fixture
def engine() -> DeterministicSequencingEngine:
    sequencing_map = load_sequencing_map(MAP_PATH)
    return DeterministicSequencingEngine(sequencing_map)


def test_loads_start_question(
    engine: DeterministicSequencingEngine,
) -> None:
    assert engine.get_start_question() == "Question_1.xml"


def test_fixed_outcome_selects_expected_question(
    engine: DeterministicSequencingEngine,
) -> None:
    decision = engine.decide(
        current_question="Question_1.xml",
        prt_name="prt1",
        outcome_code="prt-1-T",
    )

    assert decision.action == SequencingAction.ADVANCE
    assert decision.next_question == "Question_2.xml"


def test_remediation_outcome_selects_remediation_question(
    engine: DeterministicSequencingEngine,
) -> None:
    decision = engine.decide(
        current_question="Question_1.xml",
        prt_name="prt1",
        outcome_code="prt-2-F",
    )

    assert decision.action == SequencingAction.REMEDIATE
    assert decision.next_question == "Question_5.xml"


def test_loop_route_returns_to_original_question(
    engine: DeterministicSequencingEngine,
) -> None:
    decision = engine.decide(
        current_question="Question_5.xml",
        prt_name="prt1",
        outcome_code="prt-1-T",
    )

    assert (
        decision.action
        == SequencingAction.RETURN_TO_DECISION
    )
    assert decision.next_question == "Question_1.xml"
    assert decision.allow_loop is True
    assert decision.max_visits == 2


def test_unknown_question_raises_clear_error(
    engine: DeterministicSequencingEngine,
) -> None:
    with pytest.raises(
        ValueError,
        match="No sequencing entry exists",
    ):
        engine.decide(
            current_question="Unknown.xml",
            prt_name="prt1",
            outcome_code="prt-1-T",
        )


def test_unknown_prt_raises_clear_error(
    engine: DeterministicSequencingEngine,
) -> None:
    with pytest.raises(
        ValueError,
        match="has no mapping for PRT",
    ):
        engine.decide(
            current_question="Question_1.xml",
            prt_name="unknown_prt",
            outcome_code="prt-1-T",
        )


def test_unknown_outcome_raises_clear_error(
    engine: DeterministicSequencingEngine,
) -> None:
    with pytest.raises(
        ValueError,
        match="No route exists for outcome",
    ):
        engine.decide(
            current_question="Question_1.xml",
            prt_name="prt1",
            outcome_code="unknown-outcome",
        )
