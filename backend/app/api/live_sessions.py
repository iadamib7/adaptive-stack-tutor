from backend.app.integrations.stack_api.variant_deployer import (
    StackVariantDeploymentError,
)

from fastapi import APIRouter, HTTPException

from backend.app.integrations.stack_api.http_client import (
    StackApiConnectionError,
    StackApiResponseError,
)
from backend.app.learning.learner_feedback import (
    build_learner_feedback,
)
from backend.app.learning.adaptive_tasks.projector import (
    project_question_xml_for_task,
)
from backend.app.schemas.live_sessions import (
    LiveSessionResponse,
    RenderedStackQuestion,
    StartLiveSessionRequest,
    SubmitLiveAnswerRequest,
)
from backend.app.services.active_curriculum_registry import (
    active_curriculum_registry,
)
from backend.app.services.curriculum_runtime_resolver import (
    curriculum_runtime_resolver,
)
from backend.app.services.live_session_factory import (
    CurriculumRuntimeBundle,
)
from backend.app.services.stack_question_runtime_service import (
    StackQuestionRuntimeError,
)


router = APIRouter(
    prefix="/live-sessions",
    tags=["Live STACK Learning"],
)


def render_current_question(
    *,
    bundle: CurriculumRuntimeBundle,
    student_id: int,
    question_id: str | None,
) -> RenderedStackQuestion | None:
    if question_id is None:
        return None

    rendered = (
        bundle.question_runtime_service
        .render_question(
            question_id=question_id
        )
    )

    presented = (
        bundle.adaptive_task_presentation_service
        .present(
            student_id=student_id,
            rendered_question=rendered,
        )
    )

    return RenderedStackQuestion(
        question_id=presented[
            "question_id"
        ],
        seed=presented["seed"],
        html=presented["html"],
        inputs=presented["inputs"],
        task_id=presented["task_id"],
        task_input_names=presented[
            "task_input_names"
        ],
        task_prt_names=presented[
            "task_prt_names"
        ],
        task_index=presented[
            "task_index"
        ],
        task_count=presented[
            "task_count"
        ],
        worked_solution=presented[
            "worked_solution"
        ],
        question_note=presented[
            "question_note"
        ],
        available_variants=presented[
            "available_variants"
        ],
    )


def validate_task_answers(
    *,
    required_inputs: list[str],
    student_answers: dict[str, str],
) -> None:
    required = set(
        required_inputs
    )

    submitted = set(
        student_answers
    )

    missing = required - submitted

    if missing:
        raise ValueError(
            "Please complete every answer field."
        )

    unexpected = submitted - required

    if unexpected:
        raise ValueError(
            "The response contains answer fields that "
            "do not belong to the current activity."
        )

    for input_name in required_inputs:
        value = student_answers.get(
            input_name,
            "",
        )

        if not value.strip():
            raise ValueError(
                "Please complete every answer field."
            )


@router.post(
    "/start",
    response_model=LiveSessionResponse,
)
def start_live_session(
    request: StartLiveSessionRequest,
) -> LiveSessionResponse:
    previous_profile_id = (
        active_curriculum_registry.snapshot(
            request.student_id
        )
    )

    profile_assignment_changed = False

    try:
        if request.curriculum_profile_id is not None:
            bundle = (
                curriculum_runtime_resolver
                .assign_and_get_bundle(
                    student_id=request.student_id,
                    profile_id=(
                        request.curriculum_profile_id
                    ),
                )
            )

            profile_assignment_changed = (
                previous_profile_id
                != bundle.profile.profile_id
            )
        else:
            bundle = (
                curriculum_runtime_resolver
                .get_bundle_for_student(
                    request.student_id
                )
            )

        concept_id = (
            request.concept_id
            or bundle.profile.starting_concept_id
        )

        session = (
            bundle.live_session_service
            .start_session(
                student_id=request.student_id,
                concept_id=concept_id,
            )
        )

        question_id = (
            session.question.id
            if session.question is not None
            else None
        )

        rendered = render_current_question(
            bundle=bundle,
            student_id=request.student_id,
            question_id=question_id,
        )

        return LiveSessionResponse(
            session=session,
            rendered_question=rendered,
        )

    except (
        ValueError,
        StackQuestionRuntimeError,
        StackApiConnectionError,
        StackApiResponseError,
        StackVariantDeploymentError,
    ) as error:
        if profile_assignment_changed:
            active_curriculum_registry.restore(
                request.student_id,
                previous_profile_id,
            )

        print("")
        print(
            "========== LIVE SESSION ERROR =========="
        )
        print(type(error).__name__)
        print(str(error))
        print(
            "========================================"
        )
        print("")

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.post(
    "/submit-answer",
    response_model=LiveSessionResponse,
)
def submit_live_answer(
    request: SubmitLiveAnswerRequest,
) -> LiveSessionResponse:
    session_snapshot = None
    evidence_snapshot = None
    task_snapshot = None

    session_repository = None
    evidence_repository = None
    task_repository = None

    transaction_started = False

    try:
        bundle = (
            curriculum_runtime_resolver
            .get_bundle_for_student(
                request.student_id
            )
        )

        live_session_service = (
            bundle.live_session_service
        )

        question_runtime_service = (
            bundle.question_runtime_service
        )

        adaptive_task_runtime_service = (
            bundle.adaptive_task_runtime_service
        )

        before_session = (
            live_session_service.get_session(
                request.student_id
            )
        )

        if before_session is None:
            raise ValueError(
                "No active learning session exists "
                "for this student."
            )

        task_state = (
            adaptive_task_runtime_service
            .get_state(
                request.student_id
            )
        )

        if task_state is None:
            raise ValueError(
                "The current learning activity is not "
                "ready. Please reload the question."
            )

        if (
            task_state.source_question_id
            != request.question_id
        ):
            raise ValueError(
                "The submitted activity is no longer "
                "the learner's current activity."
            )

        current_task = (
            task_state.current_task
        )

        if current_task is None:
            raise ValueError(
                "This learning activity has already "
                "been completed."
            )

        validate_task_answers(
            required_inputs=(
                current_task.input_names
            ),
            student_answers=(
                request.student_answers
            ),
        )

        question_xml, _ = (
            question_runtime_service
            .prepare_question(
                question_id=request.question_id
            )
        )

        grading_question_xml = (
            project_question_xml_for_task(
                question_xml=question_xml,
                task=current_task,
            )
        )

        scored_outcome = (
            live_session_service.evaluate_answer(
                student_id=request.student_id,
                concept_id=request.concept_id,
                question_id=request.question_id,
                question_xml=grading_question_xml,
                student_answers=(
                    request.student_answers
                ),

                # The server derives grading targets
                # from the active adaptive task.
                target_prt_names=(
                    current_task.prt_names
                ),

                seed=request.seed,
            )
        )

        submitted_question_name = None

        if before_session.question is not None:
            submitted_question_name = (
                before_session.question.name
            )

        concept_name = (
            before_session.progress
            .concept_name
        )

        attempt_number = (
            before_session.progress.attempts
            + 1
        )

        # --------------------------------------------------
        # Multi-part STACK source question
        # --------------------------------------------------

        # --------------------------------------------------


        # Transaction snapshot


        # --------------------------------------------------


        # STACK grading above is read-only with respect to


        # learner progression. From this point onward the


        # adaptive task state, evidence history, and session


        # assignment may change.





        session_repository = (


            live_session_service


            .session_engine


            .session_repository


        )





        evidence_repository = (


            live_session_service


            .session_engine


            .evidence_tracker


            .evidence_repository


        )





        task_repository = (


            adaptive_task_runtime_service


            .repository


        )





        session_snapshot = (


            session_repository.snapshot(


                request.student_id


            )


        )





        evidence_snapshot = (


            evidence_repository.snapshot_student(


                request.student_id


            )


        )





        task_snapshot = (


            task_repository.snapshot(


                request.student_id


            )


        )





        transaction_started = True





        if task_state.task_count > 1:
            if scored_outcome.score < 1.0:
                rendered = render_current_question(
                    bundle=bundle,
                    student_id=request.student_id,
                    question_id=request.question_id,
                )

                feedback = (
                    build_learner_feedback(
                        score=scored_outcome.score,
                        concept_name=concept_name,
                        attempt_number=(
                            attempt_number
                        ),
                        question_name=(
                            submitted_question_name
                        ),
                    )
                )

                return LiveSessionResponse(
                    session=before_session,
                    rendered_question=rendered,
                    submitted_feedback=feedback,
                )

            updated_task_state = (
                adaptive_task_runtime_service
                .advance(
                    request.student_id
                )
            )

            # More tasks remain inside this same
            # source STACK question.
            if not updated_task_state.completed:
                rendered = render_current_question(
                    bundle=bundle,
                    student_id=request.student_id,
                    question_id=request.question_id,
                )

                feedback = (
                    build_learner_feedback(
                        score=1.0,
                        concept_name=concept_name,
                        attempt_number=(
                            attempt_number
                        ),
                        question_name=(
                            submitted_question_name
                        ),
                    )
                )

                return LiveSessionResponse(
                    session=before_session,
                    rendered_question=rendered,
                    submitted_feedback=feedback,
                )

        # --------------------------------------------------
        # Source question is complete.
        #
        # For a normal single-task question we arrive here
        # immediately.
        #
        # For a multi-part source question we arrive here
        # only after its final task has been answered
        # correctly.
        # --------------------------------------------------

        completed_session = (
            live_session_service.submit_outcome(
                scored_outcome
            )
        )

        concept_completed = (
            completed_session.question is None
            and bool(
                completed_session.next_concept_id
            )
        )

        completed_concept_name = (
            completed_session.progress
            .concept_name
        )

        session_to_return = (
            completed_session
        )

        if concept_completed:
            session_to_return = (
                live_session_service.start_session(
                    student_id=request.student_id,
                    concept_id=(
                        completed_session
                        .next_concept_id
                    ),
                )
            )

        next_question_id = (
            session_to_return.question.id
            if session_to_return.question
            is not None
            else None
        )

        rendered = render_current_question(
            bundle=bundle,
            student_id=request.student_id,
            question_id=next_question_id,
        )

        next_concept_name = None

        if concept_completed:
            next_concept_name = (
                session_to_return.progress
                .concept_name
            )

        submitted_feedback = (
            build_learner_feedback(
                score=scored_outcome.score,
                concept_name=(
                    completed_concept_name
                ),
                attempt_number=(
                    completed_session.progress
                    .attempts
                ),
                question_name=(
                    submitted_question_name
                ),
                next_concept_name=(
                    next_concept_name
                ),
                concept_completed=(
                    concept_completed
                ),
            )
        )

        return LiveSessionResponse(
            session=session_to_return,
            rendered_question=rendered,
            submitted_feedback=(
                submitted_feedback
            ),
        )

    except (
        ValueError,
        StackQuestionRuntimeError,
        StackApiConnectionError,
        StackApiResponseError,
        StackVariantDeploymentError,
    ) as error:
        if transaction_started:

            session_repository.restore(

                request.student_id,

                session_snapshot,

            )



            evidence_repository.restore_student(

                request.student_id,

                evidence_snapshot,

            )



            task_repository.restore(

                request.student_id,

                task_snapshot,

            )



            print("")

            print(

                "===== LEARNER STATE ROLLED BACK ====="

            )



        print("")

        print("========== SUBMIT ANSWER ERROR ==========")
        print(type(error).__name__)
        print(str(error))
        print("=========================================")
        print("")

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
