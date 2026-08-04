import argparse
import json
from pathlib import Path

from backend.app.integrations.stack_xml.parser import (
    StackXMLParser,
)
from backend.app.integrations.stack_xml.template_generator import (
    SequencingTemplateGenerator,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate blank adaptive sequencing entries "
            "from STACK XML questions."
        )
    )

    parser.add_argument(
        "input",
        type=Path,
        help="STACK XML file or directory.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("generated_sequencing_entries.json"),
        help="Path for the generated JSON file.",
    )

    arguments = parser.parse_args()

    xml_parser = StackXMLParser()
    generator = SequencingTemplateGenerator()

    if arguments.input.is_dir():
        questions = xml_parser.parse_directory(
            arguments.input
        )
    else:
        questions = [
            xml_parser.parse_file(arguments.input)
        ]

    entries: dict = {}

    for question in questions:
        entries.update(
            generator.generate_question_entry(
                question
            )
        )

    arguments.output.write_text(
        json.dumps(entries, indent=2),
        encoding="utf-8",
    )

    print(
        f"Generated {len(entries)} sequencing-map "
        f"entries at {arguments.output}"
    )


if __name__ == "__main__":
    main()
