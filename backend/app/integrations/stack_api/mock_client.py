from backend.app.integrations.stack_api.client import (
    StackEvaluationClient,
)
from backend.app.integrations.stack_api.models import (
    NormalizedStackResult,
    StackEvaluationRequest,
)


class MockStackEvaluationClient(
    StackEvaluationClient
):
    """
    Configurable mock used by tests and local development.

    Results are registered by question ID, so no live STACK
    installation is required.
    """

    def __init__(
        self,
        results: dict[
            str,
            NormalizedStackResult,
        ] | None = None,
    ) -> None:
        self._results = results or {}
        self.requests: list[
            StackEvaluationRequest
        ] = []

    def register_result(
        self,
        result: NormalizedStackResult,
    ) -> None:
        self._results[result.question_id] = result

    def evaluate(
        self,
        request: StackEvaluationRequest,
    ) -> NormalizedStackResult:
        self.requests.append(request)

        result = self._results.get(
            request.question_id
        )

        if result is None:
            raise ValueError(
                "No mock STACK result is registered for "
                f"question {request.question_id}."
            )

        return result
