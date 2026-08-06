from backend.app.integrations.stack_api.http_client import (
    HttpStackEvaluationClient,
)
from backend.app.integrations.stack_api.mock_client import (
    MockStackEvaluationClient,
)
from backend.app.services.session_service_factory import (
    build_live_stack_session_service,
    build_mock_stack_session_service,
)


def test_mock_factory_uses_mock_stack_client() -> None:
    service, client = (
        build_mock_stack_session_service()
    )

    assert isinstance(
        client,
        MockStackEvaluationClient,
    )

    assert service.stack_adapter.client is client


def test_live_factory_uses_http_stack_client() -> None:
    service = build_live_stack_session_service(
        base_url="http://stack.test",
        timeout_seconds=45,
    )

    client = service.stack_adapter.client

    assert isinstance(
        client,
        HttpStackEvaluationClient,
    )

    assert client.base_url == "http://stack.test"
    assert client.timeout_seconds == 45
