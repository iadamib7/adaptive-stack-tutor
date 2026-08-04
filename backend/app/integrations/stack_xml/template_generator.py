from backend.app.integrations.stack_xml.models import (
    StackQuestionStructure,
)


class SequencingTemplateGenerator:
    """
    Generate a blank teacher-editable sequencing-map entry.

    Only branches which exit the PRT receive routing placeholders.
    Branches which continue to another node remain internal to STACK
    and therefore do not need cross-question routes.
    """

    def generate_question_entry(
        self,
        question: StackQuestionStructure,
    ) -> dict:
        prt_entries: dict[str, dict] = {}

        for prt in question.prts:
            outcomes: dict[str, dict] = {}

            for node in prt.nodes:
                for branch in [
                    node.true_branch,
                    node.false_branch,
                ]:
                    if not branch.exits_tree:
                        continue

                    outcome_code = (
                        f"prt-{node.number}-{branch.branch}"
                    )

                    outcomes[outcome_code] = {
                        "action": "practice",
                        "strategy": "fixed",
                        "reason": (
                            "TODO: explain why this route "
                            "is educationally appropriate."
                        ),
                        "next_questions": [],
                        "allow_loop": False,
                        "max_visits": None,
                    }

            prt_entries[prt.name] = {
                "outcomes": outcomes,
            }

        return {
            question.filename: {
                "notes": (
                    f"Generated from STACK question: "
                    f"{question.question_name}"
                ),
                "prts": prt_entries,
            }
        }
