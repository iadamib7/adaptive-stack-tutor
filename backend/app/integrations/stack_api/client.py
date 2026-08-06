from abc import ABC, abstractmethod

from backend.app.integrations.stack_api.models import (
    NormalizedStackResult,
    StackEvaluationRequest,
)


class StackEvaluationClient(ABC):
    """
    Interface for evaluating a STACK question.

    The real implementation will later convert STACK XML into
    the request format expected by the STACK API and send the
    learner response to the configured endpoint.
    """

    @abstractmethod
    def evaluate(
        self,
        request: StackEvaluationRequest,
    ) -> NormalizedStackResult:
        raise NotImplementedError
