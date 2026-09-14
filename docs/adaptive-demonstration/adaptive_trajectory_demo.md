# Adaptive Pathway Demonstration

## Purpose

This demonstration verifies that the Adaptive STACK Tutor does not
present every learner with a fixed linear question sequence.

Three simulated learners used the same instructor-uploaded question
bank and the same generated bank-local adaptive structure. Each learner
started from the same entry question but followed a different response
pattern.

The observed next-question selections were recorded directly from the
running adaptive system after STACK grading and learner-state updates.

## Experimental setup

Date: September 14, 2026

Implementation branch:

`feature/adaptive-task-runtime`

Interface-separation commit:

`578248c`

All learners used:

- the same uploaded question bank;
- the same instructor-reviewed adaptive metadata;
- the same adaptive selection algorithm; and
- the same initial question,
  `stack-688a9ac66966c29f`.

The learners differed only in their responses.

## Learner A: consistently correct responses

Response pattern:

`Correct -> Correct -> Correct -> Correct`

Observed trajectory:

`stack-688a9ac66966c29f`

-> `stack-1e6fc87a878b69f5`
   Give example proving not function

-> `stack-b635827bd78031b6`
   Relations Cartesian Products

-> `stack-0b8e0ab37fd5fce0`
   Finding the distance between point A and point B on a number line

-> `stack-272b0ca62fdce9c1`
   Rational expression_7a

## Learner B: lower-success response pattern

Response pattern:

`Incorrect -> Incorrect -> Correct -> Incorrect -> Incorrect`

Observed trajectory:

`stack-688a9ac66966c29f`

-> `stack-4d4b87ad8c595a5a`
   Solve the exponential equation

-> `stack-688a9ac66966c29f`

-> `stack-1e6fc87a878b69f5`
   Give example proving not function

-> `stack-0b8e0ab37fd5fce0`
   Finding the distance between point A and point B on a number line

-> `stack-287fa69fe7bfa84f`
   Evaluate hyperbolic functions

## Learner C: mixed response pattern

Response pattern:

`Correct -> Incorrect -> Correct -> Incorrect`

Observed trajectory:

`stack-688a9ac66966c29f`

-> `stack-1e6fc87a878b69f5`
   Give example proving not function

-> `stack-0b8e0ab37fd5fce0`
   Finding the distance between point A and point B on a number line

-> `stack-272b0ca62fdce9c1`
   Rational expression_7a

-> `stack-287fa69fe7bfa84f`
   Evaluate hyperbolic functions

## Direct evidence of response-dependent branching

The clearest controlled comparison occurs immediately after the common
entry question.

Learner A:

`stack-688a9ac66966c29f`
+ score `1.0`
-> `stack-1e6fc87a878b69f5`

Learner B:

`stack-688a9ac66966c29f`
+ score `0.0`
-> `stack-4d4b87ad8c595a5a`

Therefore, two learners with the same question bank and the same
starting question were sent to different next questions after producing
different response evidence.

A second branching comparison occurs after
`stack-1e6fc87a878b69f5`.

Learner A:

score `1.0`
-> `stack-b635827bd78031b6`

Learner C:

score `0.0`
-> `stack-0b8e0ab37fd5fce0`

This shows that response-dependent branching is not limited to the
initial transition.

## Interpretation

The results demonstrate response-dependent adaptive sequencing rather
than traversal of a fixed predetermined order.

After each learner response:

1. STACK evaluates the submitted answer.
2. The score and PRT outcome are converted into response evidence.
3. The learner state is updated.
4. Eligible questions are determined from bank-local relationships and
   current response evidence.
5. Candidate questions are ranked deterministically.
6. The highest-ranked question becomes the next learner question.

The selector is deterministic but not linear. Identical learner states
produce identical decisions, while different response histories can
produce different learner states and therefore different question
sequences.

The observed trajectories also demonstrate that paths may diverge,
later converge on a shared question, and diverge again. Adaptiveness
therefore does not require every learner to remain on a permanently
unique path.

## Evidence files

Raw transition data:

`docs/adaptive-demonstration/adaptive_trajectory_evidence.csv`

Screenshots:

`docs/adaptive-demonstration/screenshots/`

## Important limitation

This demonstration verifies system behavior and adaptive routing. It
does not by itself establish improved learning outcomes or pedagogical
effectiveness. Evaluation with learners and instructors remains future
work.
