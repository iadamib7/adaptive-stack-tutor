import random

import pytest

from backend.app.integrations.stack_api.variant_deployer import (
    StackVariantDeployer,
    add_deployed_seeds,
    get_deployed_seeds,
)


QUESTION_XML = """
<quiz>
  <question type="stack">
    <name>
      <text>Random question</text>
    </name>
    <questionvariables>
      <text>a:rand(10)+1;</text>
    </questionvariables>
    <questionnote>
      <text>{@a@}</text>
    </questionnote>
  </question>
</quiz>
""".strip()


class FakeResponse:
    def __init__(
        self,
        payload: dict,
        ok: bool = True,
    ) -> None:
        self._payload = payload
        self.ok = ok

    def json(self) -> dict:
        return self._payload


class FakeSession:
    def __init__(self) -> None:
        self.requests: list[
            tuple[str, dict]
        ] = []

    def post(
        self,
        url: str,
        json: dict,
        timeout: int,
    ) -> FakeResponse:
        self.requests.append(
            (
                url,
                json,
            )
        )

        xml = json["questionDefinition"]
        seed = get_deployed_seeds(xml)[0]

        if url.endswith("/test"):
            return FakeResponse(
                {
                    "messages": "",
                    "isupgradeerror": False,
                    "results": {
                        str(seed): {
                            "passes": 1,
                            "fails": 0,
                            "messages": "",
                        }
                    },
                }
            )

        return FakeResponse(
            {
                "questionnote": (
                    f"Variant for seed {seed}"
                )
            }
        )


def test_adds_deployed_seeds() -> None:
    deployed = add_deployed_seeds(
        QUESTION_XML,
        [10, 20, 30],
    )

    assert get_deployed_seeds(
        deployed
    ) == [10, 20, 30]


def test_replaces_existing_seeds() -> None:
    first = add_deployed_seeds(
        QUESTION_XML,
        [10],
    )

    second = add_deployed_seeds(
        first,
        [20],
    )

    assert get_deployed_seeds(
        second
    ) == [20]


def test_rejects_non_positive_seed() -> None:
    with pytest.raises(
        ValueError,
        match="positive",
    ):
        add_deployed_seeds(
            QUESTION_XML,
            [0],
        )


def test_deploys_requested_variants() -> None:
    session = FakeSession()

    deployer = StackVariantDeployer(
        session=session,
        random_generator=random.Random(7),
    )

    result = deployer.deploy(
        question_xml=QUESTION_XML,
        variant_count=3,
        max_attempts=10,
    )

    assert len(result.variants) == 3
    assert len(result.seeds) == 3
    assert len(set(result.seeds)) == 3

    assert get_deployed_seeds(
        result.question_xml
    ) == result.seeds


def test_calls_test_and_render_routes() -> None:
    session = FakeSession()

    deployer = StackVariantDeployer(
        session=session,
        random_generator=random.Random(7),
    )

    deployer.deploy(
        question_xml=QUESTION_XML,
        variant_count=1,
        max_attempts=5,
    )

    urls = [
        request[0]
        for request in session.requests
    ]

    assert any(
        url.endswith("/test")
        for url in urls
    )

    assert any(
        url.endswith("/render")
        for url in urls
    )


def test_rejects_more_than_100_variants() -> None:
    deployer = StackVariantDeployer(
        session=FakeSession(),
    )

    with pytest.raises(
        ValueError,
        match="100",
    ):
        deployer.deploy(
            question_xml=QUESTION_XML,
            variant_count=101,
        )
