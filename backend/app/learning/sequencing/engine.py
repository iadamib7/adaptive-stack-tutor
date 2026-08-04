from backend.app.learning.sequencing.models import (
    SequencingAction,
    SequencingDecision,
    SequencingMap,
)
from backend.app.learning.sequencing.strategies import (
    ChoiceStrategy,
    FixedChoiceStrategy,
    WeightedRandomChoiceStrategy,
)


class DeterministicSequencingEngine:
    def __init__(
        self,
        sequencing_map: SequencingMap,
        strategies: dict[str, ChoiceStrategy] | None = None,
    ) -> None:
        self.sequencing_map = sequencing_map
        self.strategies = strategies or {
            "fixed": FixedChoiceStrategy(),
            "weighted_random": WeightedRandomChoiceStrategy(),
        }

    def get_start_question(self) -> str:
        return self.sequencing_map.start_question

    def decide(
        self,
        current_question: str,
        prt_name: str,
        outcome_code: str,
    ) -> SequencingDecision:
        question_mapping = self.sequencing_map.questions.get(
            current_question
        )

        if question_mapping is None:
            raise ValueError(
                f"No sequencing entry exists for "
                f"{current_question}."
            )

        prt_mapping = question_mapping.prts.get(prt_name)

        if prt_mapping is None:
            raise ValueError(
                f"Question {current_question} has no mapping "
                f"for PRT {prt_name}."
            )

        route = prt_mapping.outcomes.get(outcome_code)

        if route is None:
            raise ValueError(
                f"No route exists for outcome "
                f"{outcome_code} in {current_question}/{prt_name}."
            )

        if route.action == SequencingAction.HALT:
            return SequencingDecision(
                source_question=current_question,
                prt_name=prt_name,
                outcome_code=outcome_code,
                action=route.action,
                next_question=None,
                reason=route.reason,
                allow_loop=route.allow_loop,
                max_visits=route.max_visits,
            )

        strategy = self.strategies.get(route.strategy)

        if strategy is None:
            raise ValueError(
                f"Unknown sequencing strategy: {route.strategy}"
            )

        selected = strategy.choose(route.next_questions)

        if selected is None:
            raise ValueError(
                f"Route {outcome_code} has no next question."
            )

        return SequencingDecision(
            source_question=current_question,
            prt_name=prt_name,
            outcome_code=outcome_code,
            action=route.action,
            next_question=selected.file,
            reason=route.reason,
            allow_loop=route.allow_loop,
            max_visits=route.max_visits,
        )
