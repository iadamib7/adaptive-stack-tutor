import argparse
from pathlib import Path

from backend.app.integrations.stack_xml.question_extractor import (
    write_stack_question,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Extract one STACK question from a Moodle XML "
            "question-bank export."
        )
    )

    parser.add_argument(
        "export_path",
        type=Path,
    )

    parser.add_argument(
        "--question-id",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
    )

    arguments = parser.parse_args()

    output_path = write_stack_question(
        export_path=arguments.export_path,
        question_id=arguments.question_id,
        output_path=arguments.output,
    )

    print(
        f"Extracted STACK question "
        f"{arguments.question_id} to {output_path}"
    )


if __name__ == "__main__":
    main()
