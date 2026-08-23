# Ghana Basic 9 Simultaneous-Equations Validation

## Purpose

This document records validated behavior for the Ghana Basic 9
simultaneous-equations adaptive pathway implemented in the
Adaptive STACK Tutor.

The pathway progresses through twelve learning activities:

- QLIN-01 through QLIN-11 provide progressively integrated
  practice and evidence.
- QLIN-12 is the required mastery-check activity.
- QLIN-12 integrates table completion, graph construction,
  intersection identification, and simultaneous-equation
  solution interpretation.

## Curriculum and Mastery Configuration

Curriculum concept:

`simultaneous-equations`

Required mastery item:

`qlin_12_table_graph_intersection_mastery`

QLIN-12 is configured as:

- sequence order: 12
- role: `mastery_check`
- `required_for_mastery: true`

No earlier QLIN activity is marked as required mastery evidence.

## Validation 1: Successful Mastery Path

### Learner history

The learner answered QLIN-01 through QLIN-11 correctly.

### Result before QLIN-12

- attempts: 11
- evidence score: 1.0
- concept mastered: false
- current question: QLIN-12

This demonstrated that perfect performance on the first eleven
activities does not prematurely mark the concept as mastered.

### QLIN-12 result

QLIN-12 was graded successfully through the live STACK
evaluation path.

After the successful QLIN-12 attempt:

- attempts: 12
- evidence score: 1.0
- positive evidence count: 12
- concept mastered: true
- session complete: true
- action: `complete_concept`

This confirmed that the required mastery item controls final
concept completion.

## Validation 2: Failed Mastery Check

### Learner history

The learner answered QLIN-01 through QLIN-11 correctly and then
failed QLIN-12.

### Result

- attempts: 12
- positive evidence count: 11
- negative evidence count: 1
- evidence score: approximately 0.8462
- concept mastered: false
- session complete: false

The failed required mastery item prevented concept mastery even
though the learner had previously achieved an evidence score of
1.0.

## Validation 3: Targeted Retry After Mastery Failure

The first implementation selected the least-attempted question
after QLIN-12 failure. Because all twelve activities had one
attempt, curriculum order broke the tie and sent the learner back
to QLIN-01.

The adaptive policy was revised so that unmet required mastery
evidence is prioritized before generic repetition.

### Validated result after the policy revision

After failing QLIN-12:

- concept mastered: false
- action: `target_practice`
- current question: QLIN-12
- session complete: false

The decision reason reports that required mastery evidence remains
unmet and therefore the mastery question is retried before generic
repetition.

This prevents an otherwise successful learner from unnecessarily
restarting the entire progression.

## Validation 4: Failure Followed by Recovery

### Learner history

1. QLIN-01 through QLIN-11: correct
2. First QLIN-12 attempt: incorrect
3. QLIN-12 retry: correct

### State after failed QLIN-12

- attempts: 12
- evidence score: approximately 0.8462
- concept mastered: false
- current question: QLIN-12

### State after successful retry

- attempts: 13
- evidence score: approximately 0.8667
- positive evidence count: 12
- negative evidence count: 1
- concept mastered: true
- session complete: true
- action: `complete_concept`

The failed attempt remains part of the evidence history rather
than being erased when the learner later succeeds.

This preserves information about learner struggle while still
allowing recovery and mastery.

## Validation 5: Deterministic Replay

Two fresh learners were given identical outcome histories:

1. QLIN-01 through QLIN-11: correct
2. first QLIN-12 attempt: incorrect
3. second QLIN-12 attempt: correct

Both learners produced identical fourteen-state traces.

The traces agreed on:

- question sequence
- adaptive action
- attempt count
- mastery state
- retry behavior
- session completion

Final replay results:

- identical traces: true
- trace length: 14
- final mastery: true
- final session complete: true

This provides evidence that the pathway behaves deterministically
for identical learner histories.

## Automated Regression Coverage

The adaptive learning session test suite now protects the
following Ghana behaviors:

- QLIN-12 is required before mastery.
- Failed QLIN-12 does not grant mastery.
- Failed QLIN-12 is retried instead of restarting at QLIN-01.
- A later successful QLIN-12 retry permits mastery.
- Identical learner histories produce identical adaptive traces.

At the latest targeted validation checkpoint:

`14 passed`

for:

`tests/test_adaptive_learning_session_engine.py`

## Current Interpretation

The Ghana simultaneous-equations slice has been validated at four
connected levels:

1. curriculum sequencing,
2. evidence and mastery logic,
3. adaptive session behavior,
4. deterministic replay.

The results support the claim that the prototype can enforce a
curriculum-specific mastery requirement, preserve evidence from
failed attempts, permit recovery, and produce reproducible
adaptive decisions for identical learner histories.

## Limitations

These validations are software and simulation validations, not
student-learning outcome evidence.

They demonstrate that the implemented adaptive logic behaves as
specified. They do not yet demonstrate that the pathway improves
student achievement, reduces misconceptions, or produces better
learning outcomes than an alternative instructional sequence.

Those questions require learner data or a future empirical study.
