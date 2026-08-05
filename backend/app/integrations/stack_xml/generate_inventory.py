import argparse
from pathlib import Path

from backend.app.integrations.stack_xml.export_parser import (
    StackExportParser,
)
from backend.app.integrations.stack_xml.inventory_writer import (
    InventoryWriter,
)


def main() -> None:
    argument_parser = argparse.ArgumentParser(
        description=(
            "Generate JSON and CSV inventories from a "
            "multi-question STACK Moodle XML export."
        )
    )

    argument_parser.add_argument(
        "input",
        type=Path,
        help="Path to the STACK Moodle XML export.",
    )

    argument_parser.add_argument(
        "--profile-id",
        required=True,
        help=(
            "Curriculum profile identifier, such as "
            "kenya-grade9-development."
        ),
    )

    argument_parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path("resources/generated"),
    )

    arguments = argument_parser.parse_args()

    inventory = StackExportParser().parse(
        path=arguments.input,
        profile_id=arguments.profile_id,
    )

    output_stem = arguments.input.stem
    json_path = (
        arguments.output_directory
        / f"{output_stem}_inventory.json"
    )
    csv_path = (
        arguments.output_directory
        / f"{output_stem}_inventory.csv"
    )

    writer = InventoryWriter()
    writer.write_json(inventory, json_path)
    writer.write_csv(inventory, csv_path)

    simple_count = sum(
        question.simple_single_prt
        for question in inventory.questions
    )

    print(
        f"Parsed {inventory.question_count} STACK questions."
    )
    print(
        f"Simple single-input/single-PRT questions: "
        f"{simple_count}"
    )
    print(f"JSON inventory: {json_path}")
    print(f"CSV inventory: {csv_path}")


if __name__ == "__main__":
    main()
