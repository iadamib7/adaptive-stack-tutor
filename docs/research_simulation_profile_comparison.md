# Ghana Adaptive Pathway Simulation Comparison

## Purpose

This document summarizes deterministic learner-profile
simulations for the Ghana Basic 9 adaptive pathway.

The simulations are intended to validate whether the software
produces different, reproducible instructional trajectories when
learners exhibit different response patterns.

These results are software-validation evidence. They are not
evidence of learning gains from real students.

## Simulation Profiles

Five deterministic learner profiles were evaluated:

- **Strong learner**: answers every activity correctly.
- **Mixed learner**: initially receives partial credit on
  non-mastery activities, then succeeds on later attempts.
- **Struggling learner**: continues to answer activities
  incorrectly.
- **Mastery-recovery learner**: performs correctly throughout
  the pathway, fails the final QLIN-12 mastery check once, and
  then succeeds on the immediate retry.
- **Graph-struggle learner**: succeeds on earlier relation and
  table activities but initially receives partial credit on
  graph and intersection activities.

## Quantitative Comparison

| Profile | Steps | Unique Questions | Repeated Attempts | Required Mastery Attempts | Final Evidence | Completed | Stalled |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Strong | 16 | 16 | 0 | 3 | 1.0 | Yes | No |
| Mixed | 25 | 16 | 9 | 3 | 0.75 | Yes | No |
| Struggling | 7 | 2 | 5 | 6 | 0.0 | No | Yes |
| Mastery Recovery | 17 | 16 | 1 | 4 | 0.866667 | Yes | No |
| Graph Struggle | 20 | 16 | 4 | 4 | 0.75 | Yes | No |

## Strong Learner

The strong profile completed the curriculum in
**16 steps** with
**0 repeated attempts** and a final
evidence score of **1.0**.

This is the shortest successful pathway in the simulation and
acts as a reference trajectory for a learner who consistently
demonstrates successful performance.

## Mixed Learner

The mixed profile required **25 steps**,
including **9 repeated attempts**.

Its final evidence score was
**0.75**, and the pathway eventually
completed successfully.

This trace demonstrates that the adaptive system does not treat
partial evidence in the same way as consistently correct
performance. Additional practice is selected before completion.

## Struggling Learner

The struggling profile stopped after
**7 steps** and did not complete the
curriculum.

It attempted only
**2 unique questions**
and accumulated **5 repeated
attempts** before the simulator's deterministic loop safeguard
classified the pathway as stalled.

This result demonstrates a current system limitation: persistent
failure within a prerequisite-free foundation concept can lead to
repeated practice rather than meaningful remediation to an
earlier concept.

The result should therefore be interpreted as diagnostic evidence
for future adaptive-policy development, not as evidence that the
current remediation strategy is sufficient.

## Mastery-Recovery Learner

The mastery-recovery profile completed the curriculum in
**17 steps**.

It differs from the strong learner by exactly one additional
attempt because the first QLIN-12 mastery-check attempt fails.

The adaptive policy then immediately returns the learner to the
unmet required mastery activity. After the learner succeeds on
the retry, the concept is completed.

The final evidence score is
**0.866667** rather than 1.0 because
the failed mastery attempt remains in the learner's evidence
history.

This behavior demonstrates three important properties:

1. required mastery evidence is enforced,
2. failed mastery checks trigger targeted retry,
3. successful recovery does not erase prior negative evidence.

## Graph-Struggle Learner

The graph-struggle profile completed the pathway in
**20 steps** with
**4 repeated attempts**.

The learner performs successfully on early table and relation
activities but initially receives partial credit on graph and
intersection activities.

This creates a different pathway from both the strong and mixed
profiles and provides a focused example of representation-specific
difficulty affecting the adaptive sequence.

## Deterministic Adaptivity

Each profile was simulated twice using the same response history.

For every profile, the repeated simulation produced the same
normalized adaptive trace.

The profiles also produced different traces from one another.

This provides software-level evidence for two properties:

- **reproducibility**: identical learner histories result in
  identical adaptive decisions;
- **differentiation**: different response histories can result in
  different pathway lengths and question-selection patterns.

## Research Interpretation

The strongest claim currently supported by these simulations is
that the prototype implements deterministic, history-sensitive
adaptive sequencing.

The results demonstrate that the software can:

- distinguish between different simulated performance patterns;
- require explicit mastery evidence before concept completion;
- preserve failed-attempt evidence;
- support recovery after mastery failure;
- extend practice when evidence remains below the mastery
  threshold;
- produce reproducible decisions for identical learner histories.

The simulations do **not** demonstrate that the adaptive system
improves mathematics achievement or student learning.

Establishing learning effectiveness would require empirical data
from actual learners and an appropriate evaluation design.

## Current Limitation Identified

The struggling profile exposes an important future improvement
area.

When persistent failure occurs in a foundation concept without an
available prerequisite concept, the current policy can repeatedly
select the same practice activity.

A stronger future remediation strategy could introduce:

- alternate questions targeting the same prerequisite skill;
- misconception-specific interventions;
- worked examples or scaffolded hints;
- lower-complexity prerequisite activities;
- teacher or tutor escalation after repeated failure.

This limitation is useful research evidence because the simulation
is identifying where the adaptive policy behaves differently from
the desired instructional behavior.

## Reproducibility Artifacts

The underlying simulation evidence is stored in:

`resources/generated/research/adaptive_pathway_simulation_summary.csv`

and:

`resources/generated/research/adaptive_pathway_simulation_traces.json`

Each profile also includes a SHA-256 fingerprint of its normalized
trace so repeated simulation outputs can be checked for exact
reproducibility.
