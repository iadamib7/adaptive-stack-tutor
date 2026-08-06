import argparse
from pathlib import Path

from backend.app.integrations.stack_api.variant_deployer import (
    StackVariantDeployer,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate tested deployed variants for one "
            "authored STACK question."
        )
    )

    parser.add_argument(
        "question_file",
        type=Path,
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--count",
        default=5,
        type=int,
    )

    parser.add_argument(
        "--max-attempts",
        default=100,
        type=int,
    )

    parser.add_argument(
        "--base-url",
        default="http://localhost:3080",
    )

    arguments = parser.parse_args()

    question_xml = (
        arguments.question_file.read_text(
            encoding="utf-8",
        )
    )

    deployer = StackVariantDeployer(
        base_url=arguments.base_url,
    )

    result = deployer.deploy(
        question_xml=question_xml,
        variant_count=arguments.count,
        max_attempts=arguments.max_attempts,
    )

    arguments.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    arguments.output.write_text(
        result.question_xml,
        encoding="utf-8",
    )

    print(
        f"Deployed {len(result.variants)} "
        f"STACK variants."
    )

    for variant in result.variants:
        print(
            f"Seed {variant.seed}: "
            f"{variant.question_note}"
        )

    print(
        f"Saved deployed question to "
        f"{arguments.output}"
    )


if __name__ == "__main__":
    main()
