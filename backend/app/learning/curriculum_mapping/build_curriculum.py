import argparse
from pathlib import Path

from backend.app.learning.curriculum_mapping.builder import (
    write_curriculum,
)


DEFAULT_OUTPUT = Path(
    "examples/curriculum_mapping/"
    "kenya_grade9_integer_operations.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build the development curriculum "
            "mapping used by the adaptive tutor."
        )
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )

    arguments = parser.parse_args()

    output_path = write_curriculum(
        arguments.output
    )

    print(
        "Generated curriculum mapping:"
    )

    print(output_path)


if __name__ == "__main__":
    main()
