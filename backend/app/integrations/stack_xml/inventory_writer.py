import csv
import json
from pathlib import Path

from backend.app.integrations.stack_xml.export_models import (
    StackQuestionInventory,
)


class InventoryWriter:
    def write_json(
        self,
        inventory: StackQuestionInventory,
        output_path: Path,
    ) -> None:
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            inventory.model_dump_json(indent=2),
            encoding="utf-8",
        )

    def write_csv(
        self,
        inventory: StackQuestionInventory,
        output_path: Path,
    ) -> None:
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as output_file:
            writer = csv.DictWriter(
                output_file,
                fieldnames=[
                    "source_question_id",
                    "question_name",
                    "category_path",
                    "input_count",
                    "prt_count",
                    "node_count",
                    "exit_outcome_count",
                    "simple_single_prt",
                    "outcome_codes",
                    "curriculum_concept_id",
                ],
            )

            writer.writeheader()

            for question in inventory.questions:
                exit_outcomes = [
                    outcome
                    for outcome in question.outcomes
                    if outcome.exits_tree
                ]

                writer.writerow(
                    {
                        "source_question_id": (
                            question.source_question_id
                            or ""
                        ),
                        "question_name": (
                            question.question_name
                        ),
                        "category_path": " > ".join(
                            question.category_path
                        ),
                        "input_count": len(
                            question.input_names
                        ),
                        "prt_count": question.prt_count,
                        "node_count": question.node_count,
                        "exit_outcome_count": len(
                            exit_outcomes
                        ),
                        "simple_single_prt": (
                            question.simple_single_prt
                        ),
                        "outcome_codes": " | ".join(
                            outcome.outcome_code
                            for outcome in exit_outcomes
                        ),
                        "curriculum_concept_id": (
                            question.curriculum_concept_id
                            or ""
                        ),
                    }
                )
