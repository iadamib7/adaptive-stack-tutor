from pathlib import Path

from backend.app.learning.sequencing.models import (
    OutcomeRoute,
    SequencingAction,
    SequencingMap,
)
from backend.app.learning.sequencing.validation import (
    ValidationIssue,
    ValidationReport,
    ValidationSeverity,
)


class SequencingMapValidator:
    def validate(
        self,
        sequencing_map: SequencingMap,
        question_directory: Path | None = None,
    ) -> ValidationReport:
        issues: list[ValidationIssue] = []

        self._validate_start_question(
            sequencing_map=sequencing_map,
            issues=issues,
        )

        self._validate_routes(
            sequencing_map=sequencing_map,
            issues=issues,
        )

        self._validate_reachability(
            sequencing_map=sequencing_map,
            issues=issues,
        )

        self._validate_cycles(
            sequencing_map=sequencing_map,
            issues=issues,
        )

        if question_directory is not None:
            self._validate_files(
                sequencing_map=sequencing_map,
                question_directory=question_directory,
                issues=issues,
            )

        return ValidationReport(issues=issues)

    @staticmethod
    def _validate_start_question(
        sequencing_map: SequencingMap,
        issues: list[ValidationIssue],
    ) -> None:
        if (
            sequencing_map.start_question
            not in sequencing_map.questions
        ):
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="missing_start_mapping",
                    message=(
                        "The start question does not have a "
                        "sequencing-map entry."
                    ),
                    question=sequencing_map.start_question,
                )
            )

    def _validate_routes(
        self,
        sequencing_map: SequencingMap,
        issues: list[ValidationIssue],
    ) -> None:
        known_targets = (
            set(sequencing_map.questions)
            | set(sequencing_map.halt_questions)
        )

        for question_name, question_mapping in (
            sequencing_map.questions.items()
        ):
            for prt_name, prt_mapping in (
                question_mapping.prts.items()
            ):
                for outcome_code, route in (
                    prt_mapping.outcomes.items()
                ):
                    self._validate_route_shape(
                        question_name=question_name,
                        prt_name=prt_name,
                        outcome_code=outcome_code,
                        route=route,
                        issues=issues,
                    )

                    for option in route.next_questions:
                        if option.file not in known_targets:
                            issues.append(
                                ValidationIssue(
                                    severity=(
                                        ValidationSeverity.ERROR
                                    ),
                                    code="unknown_target",
                                    message=(
                                        f"Route targets "
                                        f"{option.file}, but that "
                                        "question is neither mapped "
                                        "nor declared as a halt "
                                        "question."
                                    ),
                                    question=question_name,
                                    prt_name=prt_name,
                                    outcome_code=outcome_code,
                                )
                            )

    @staticmethod
    def _validate_route_shape(
        question_name: str,
        prt_name: str,
        outcome_code: str,
        route: OutcomeRoute,
        issues: list[ValidationIssue],
    ) -> None:
        if route.action == SequencingAction.HALT:
            if route.next_questions:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        code="halt_route_has_target",
                        message=(
                            "A halt route must not contain a "
                            "next question."
                        ),
                        question=question_name,
                        prt_name=prt_name,
                        outcome_code=outcome_code,
                    )
                )
            return

        if not route.next_questions:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="route_has_no_target",
                    message=(
                        "A non-halt route must contain at least "
                        "one next question."
                    ),
                    question=question_name,
                    prt_name=prt_name,
                    outcome_code=outcome_code,
                )
            )

        if (
            route.strategy == "fixed"
            and len(route.next_questions) != 1
        ):
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="invalid_fixed_route",
                    message=(
                        "A fixed route must contain exactly one "
                        "next question."
                    ),
                    question=question_name,
                    prt_name=prt_name,
                    outcome_code=outcome_code,
                )
            )

        if (
            route.allow_loop
            and route.max_visits is None
        ):
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="unbounded_declared_loop",
                    message=(
                        "The route allows a loop but does not "
                        "define max_visits."
                    ),
                    question=question_name,
                    prt_name=prt_name,
                    outcome_code=outcome_code,
                )
            )

    def _validate_reachability(
        self,
        sequencing_map: SequencingMap,
        issues: list[ValidationIssue],
    ) -> None:
        reachable = self._find_reachable_questions(
            sequencing_map
        )

        for question_name in sequencing_map.questions:
            if question_name not in reachable:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        code="unreachable_question",
                        message=(
                            "This mapped question cannot be "
                            "reached from the configured start "
                            "question."
                        ),
                        question=question_name,
                    )
                )

    @staticmethod
    def _find_reachable_questions(
        sequencing_map: SequencingMap,
    ) -> set[str]:
        visited: set[str] = set()
        pending = [sequencing_map.start_question]

        while pending:
            current = pending.pop()

            if current in visited:
                continue

            visited.add(current)

            mapping = sequencing_map.questions.get(current)

            if mapping is None:
                continue

            for prt_mapping in mapping.prts.values():
                for route in prt_mapping.outcomes.values():
                    for option in route.next_questions:
                        if option.file not in visited:
                            pending.append(option.file)

        return visited

    def _validate_cycles(
        self,
        sequencing_map: SequencingMap,
        issues: list[ValidationIssue],
    ) -> None:
        graph: dict[str, list[tuple[str, bool]]] = {}

        for question_name, question_mapping in (
            sequencing_map.questions.items()
        ):
            edges: list[tuple[str, bool]] = []

            for prt_mapping in question_mapping.prts.values():
                for route in prt_mapping.outcomes.values():
                    for option in route.next_questions:
                        if option.file in sequencing_map.questions:
                            edges.append(
                                (
                                    option.file,
                                    route.allow_loop,
                                )
                            )

            graph[question_name] = edges

        visited: set[str] = set()
        active: set[str] = set()

        def visit(question_name: str) -> None:
            visited.add(question_name)
            active.add(question_name)

            for target, loop_allowed in graph.get(
                question_name,
                [],
            ):
                if target not in visited:
                    visit(target)
                elif target in active and not loop_allowed:
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            code="undeclared_cycle",
                            message=(
                                f"A cycle from {question_name} "
                                f"to {target} exists without "
                                "allow_loop=true."
                            ),
                            question=question_name,
                        )
                    )

            active.remove(question_name)

        for question_name in graph:
            if question_name not in visited:
                visit(question_name)

    @staticmethod
    def _validate_files(
        sequencing_map: SequencingMap,
        question_directory: Path,
        issues: list[ValidationIssue],
    ) -> None:
        referenced_files = (
            set(sequencing_map.questions)
            | set(sequencing_map.halt_questions)
        )

        for question_mapping in (
            sequencing_map.questions.values()
        ):
            for prt_mapping in question_mapping.prts.values():
                for route in prt_mapping.outcomes.values():
                    referenced_files.update(
                        option.file
                        for option in route.next_questions
                    )

        for filename in sorted(referenced_files):
            path = question_directory / filename

            if not path.is_file():
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        code="missing_question_file",
                        message=(
                            f"Referenced question file does not "
                            f"exist: {path}"
                        ),
                        question=filename,
                    )
                )
