# Adaptive STACK Tutor

Adaptive STACK Tutor is a curriculum-independent, deterministic adaptive mathematics assessment and tutoring system built around STACK.

The system accepts instructor-authored mathematics question banks, evaluates learner responses through STACK, converts STACK grading evidence into learner-state updates, and determines what the learner should do next.

The current research prototype supports response-dependent progression, targeted remediation, reassessment, historical learner evidence, multi-format question-bank import, instructor metadata overrides, and a browser-based adaptive learning interface.

---

## Research Goal

The project investigates the following question:

> How can response evidence from existing STACK question banks be used to construct useful adaptive learning pathways without requiring each question bank to be redesigned for one specific curriculum?

The goal is to build an adaptive layer that can operate across different mathematics resources rather than being tied to a single national curriculum, course, or manually authored adaptive sequence.

---

## What Makes the System Adaptive?

In this project, adaptation means that the learner can be asked to do something different next because of evidence from previous responses.

For example:

```text
Learner A

Question A
    |
 Correct
    |
    v
Question B
```

```text
Learner B

Question A
    |
Difficulty detected
    |
    v
Support Question
    |
 Correct
    |
    v
Question A Reassessment
    |
    v
Continue
```

Different feedback alone is not considered adaptation.

The actual learning pathway must change.

---

## Core Design Principles

### 1. STACK Remains Authoritative

STACK performs the mathematical evaluation.

The adaptive layer does not replace:

- STACK answer tests
- Potential Response Trees (PRTs)
- authored feedback
- answer notes
- scoring logic
- mathematical evaluation

Instead, Adaptive STACK Tutor consumes evidence returned by STACK after a learner response has been evaluated.

This preserves the mathematical grading behavior of instructor-authored STACK questions.

### 2. Adaptation Is Deterministic

The current prototype intentionally uses deterministic adaptive logic rather than machine-learning-based routing.

Given the same:

- question bank
- learner state
- response evidence
- metadata
- available questions

the system produces the same adaptive decision.

This makes the adaptive behavior reproducible, explainable, auditable, and testable.

### 3. The Engine Is Curriculum-Independent

The adaptive engine does not require one hard-coded national curriculum.

Instead, it operates using information available within an instructor-authored question bank together with optional adaptive metadata.

Metadata can describe:

- skills
- categories
- difficulty
- support relationships
- diagnostic relationships

Instructor-provided metadata takes precedence over automatically generated metadata.

### 4. Conservative Inference

The system avoids inventing unsupported misconception labels or curriculum relationships.

Automatically inferred relationships are treated as adaptive heuristics rather than formal claims about learner cognition or curriculum prerequisites.

### 5. Existing Question Banks Remain Useful

A major goal is to reduce the amount of manual restructuring required before an existing mathematics question bank can participate in adaptive assessment.

---

## Supported Question-Bank Formats

The adaptive upload pipeline currently supports:

- Moodle / STACK XML (`.xml`)
- Excel (`.xlsx`)
- Excel Macro-Enabled Workbook (`.xlsm`)
- CSV (`.csv`)
- Microsoft Word (`.docx`)
- text-based PDF (`.pdf`)

STACK-native XML banks preserve their authored STACK grading behavior.

Structured non-STACK documents can be converted into an internal question-bank representation before adaptive processing.

---

## Adaptive Runtime

The high-level runtime is:

```text
Instructor Question Bank
        |
        v
Question-Bank Import
        |
        v
Bank Profiling
        |
        v
Adaptive Graph
        |
        v
Adaptive Session Service
        |
        v
STACK Evaluation
        |
        v
Score / PRT Evidence
        |
        v
Learner-State Update
        |
        v
Deterministic Selection
        |
        +----> Continue
        |
        +----> Remediate
        |
        +----> Reassess
```

The adaptive layer operates after mathematical evaluation rather than replacing STACK itself.

---

## Question-Bank Profiling

Uploaded question banks are analyzed to create a bank-local adaptive representation.

Depending on the available source information, the system can use:

- question identifiers
- categories
- tags
- skills
- STACK answer notes
- diagnostic relationships
- support relationships
- structural difficulty
- learner question history

Explicit instructor metadata can override automatically generated metadata.

Structural complexity is used only as a cold-start heuristic for question difficulty.

It is not equivalent to calibrated psychometric item difficulty or an Item Response Theory parameter.

---

## Adaptive Graph Construction

The adaptive graph represents possible relationships and transitions among questions in the uploaded bank.

Transitions can support:

- normal progression
- targeted support
- remediation
- reassessment

The graph is built from available question-bank information rather than requiring one manually encoded national curriculum pathway.

This allows the same adaptive runtime to operate over different instructor-authored resources.

---

## Deterministic Question Selection

The selector chooses among available candidate questions using deterministic signals.

These can include:

- learner-response evidence
- difficulty match
- diagnostic relevance
- support relevance
- novelty
- repetition avoidance

When multiple candidate questions receive the same selection score, question identifiers provide deterministic tie-breaking.

Identical learner state and bank state therefore produce reproducible selection behavior.

---

## Automatic Remediation

When a learner response provides evidence of difficulty, the system can route the learner to an appropriate support question.

Support selection can use:

- explicit instructor-defined metadata
- STACK PRT answer-note relationships
- conservative content similarity
- bank-local question relationships

A successful support response can return the learner to the original question for reassessment.

```text
Original Question
        |
        v
Difficulty Evidence
        |
        v
Support Question
        |
        v
Successful Support
        |
        v
Original Question Reassessment
        |
        v
Continue
```

This remediation-reassessment loop is one of the central adaptive behaviors implemented by the current prototype.

---

## STACK Evidence Handling

STACK grading evidence is normalized before reaching the adaptive engine.

The runtime distinguishes between:

- a genuine numeric score of `0`
- an unavailable PRT score
- an available overall STACK score

If numeric PRT scores are available, they can contribute directly to adaptive evidence.

If individual PRT scores are unavailable but STACK supplies a valid overall score, the adaptive evidence layer can use that score as fallback evidence.

If no numeric score evidence exists, the result is not silently interpreted as a learner score of zero.

This prevents missing STACK data from being incorrectly treated as learner failure.

---

## Potential Response Tree Evidence

STACK Potential Response Trees provide richer information than a simple correct/incorrect result.

The adaptive system can preserve and use information associated with:

- PRT scores
- answer notes
- grading outcomes
- authored response paths

This allows the adaptive layer to respond to evidence already encoded by the original STACK question author.

The system does not fabricate unsupported misconception labels from these results.

---

## Historical Learner Evidence

Historical STACK responses can also be imported into the adaptive system.

Historical interaction data can contribute information about:

- previous attempts
- prior performance
- repeated questions
- question familiarity
- learner history

This means an adaptive session does not necessarily begin with an entirely empty learner state.

Previous interaction evidence can influence later question selection.

---

## Live Adaptive Demo

The project includes a browser-based adaptive research interface.

Start the FastAPI application with:

```bash
python -m uvicorn backend.app.main:app --reload --port 8020
```

Then open:

```text
http://127.0.0.1:8020/adaptive-demo
```

The API health endpoint is available at:

```text
http://127.0.0.1:8020/health
```

A running STACK evaluation service is required for live STACK mathematical grading.

The adaptive demo allows an instructor or researcher to:

1. enter a learner identifier
2. upload a supported question bank
3. optionally provide adaptive metadata
4. start an adaptive session
5. answer rendered STACK questions
6. observe response-dependent progression
7. experience support and remediation when triggered
8. return to an earlier question for reassessment

The learner-facing interface intentionally hides internal routing information.

It does not expose:

- raw internal decision types
- internal question identifiers
- raw PRT identifiers
- remediation target identifiers
- reassessment bookkeeping

Instead, learner-facing messages describe only the instructional action.

Examples include:

- `Correct. Here is your next question.`
- `Here is a support question based on your previous response.`
- `Good progress. Now try the earlier question again.`

---

## API

The FastAPI application includes routes for:

- adaptive sessions
- adaptive question-bank uploads
- the adaptive browser demo
- learner sessions
- questions
- attempts
- content
- STACK-backed live sessions

The current application version is:

```text
0.4.0
```

---

## Main Implementation

The current curriculum-independent adaptive implementation is centered on:

```text
backend/app/learning/adaptive_engine/
backend/app/api/adaptive_sessions.py
backend/app/api/adaptive_uploads.py
backend/app/api/adaptive_demo.py
backend/app/integrations/stack_api/
backend/app/web/adaptive_demo.html
```

Important adaptive-engine modules include:

```text
adaptive_graph_builder.py
bank_profile.py
document_import.py
engine.py
historical_responses.py
metadata.py
models.py
selector.py
session_service.py
stack_evidence.py
```

---

## Repository Structure

```text
adaptive-stack-tutor/
|
+-- backend/
|   +-- app/
|       +-- api/
|       |   +-- adaptive_demo.py
|       |   +-- adaptive_sessions.py
|       |   +-- adaptive_uploads.py
|       |   +-- ...
|       |
|       +-- integrations/
|       |   +-- stack_api/
|       |   +-- stack_xml/
|       |
|       +-- learning/
|       |   +-- adaptive_engine/
|       |   +-- ...
|       |
|       +-- services/
|       |
|       +-- web/
|           +-- adaptive_demo.html
|
+-- docs/
+-- examples/
+-- resources/
+-- tests/
+-- requirements.txt
+-- README.md
```

The repository also preserves earlier curriculum-specific experiments developed during the evolution of the research project.

Those resources remain useful historical research evidence but are separate from the current curriculum-independent adaptive runtime.

---

## Testing

The current adaptive checkpoint has been verified with:

```text
155 passed in 4.83s
```

The tested adaptive behaviors include:

- adaptive session behavior
- deterministic question selection
- adaptive graph construction
- question-bank profiling
- document import
- STACK evaluation normalization
- PRT evidence extraction
- missing PRT score handling
- overall-score fallback behavior
- multi-PRT evaluation
- automatic remediation
- content-aware support routing
- reassessment behavior
- historical learner responses
- adaptive upload endpoints
- adaptive browser-interface behavior

Run the test suite with:

```bash
python -m pytest tests -q
```

---

## Current Prototype Capabilities

The current research prototype demonstrates:

- curriculum-independent question-bank ingestion
- deterministic adaptive question selection
- adaptive graph construction
- live STACK response evaluation
- STACK PRT evidence integration
- adaptive learner-state updates
- response-dependent progression
- support-question selection
- automatic remediation
- reassessment
- historical response ingestion
- multi-format instructor document import
- instructor metadata overrides
- browser-based adaptive interaction
- reproducible automated testing

---

## Research Boundaries and Limitations

The current prototype should not be interpreted as a complete psychometric adaptive-testing system.

### Difficulty

Automatically generated structural difficulty is a cold-start heuristic.

It is not:

- calibrated item difficulty
- an Item Response Theory difficulty parameter
- an empirical population difficulty estimate

### Learner Ability

The current learner state is deterministic and evidence-based.

It is not an Item Response Theory latent ability estimate.

### Support Relationships

Automatically inferred support relationships are heuristics.

They should not be interpreted as formal prerequisite relationships unless explicitly supplied by an instructor or supported by the source question bank.

### Content Similarity

Content similarity can help identify candidate support questions.

It does not prove pedagogical equivalence.

### Diagnostics

STACK-authored evidence is preserved.

The adaptive layer avoids inventing misconception labels unsupported by the source question bank.

### Curriculum Independence

Curriculum independence means that the adaptive runtime does not require one hard-coded curriculum.

It does not mean that the system automatically reconstructs a complete formal curriculum model from arbitrary documents.

---

## Earlier Curriculum-Specific Research

Earlier stages of the project explored deterministic adaptive pathways using curriculum-specific resources.

Those validation documents are preserved in:

```text
docs/research_simulation_profile_comparison.md
docs/research_validation_ghana_simultaneous_equations.md
```

These documents contain earlier Ghana Basic 9 pathway experiments.

They remain part of the research history of the project but are separate from the architecture of the current curriculum-independent adaptive runtime.

---

## Future Research

Possible future extensions include:

- empirical evaluation with real learner interaction data
- educator evaluation of inferred support relationships
- improved mathematical question-similarity methods
- richer learner-state estimation
- psychometric calibration
- Item Response Theory
- empirical question-difficulty estimation
- learning analytics dashboards
- instructor authoring tools
- cross-bank adaptive evaluation
- comparison between fixed and adaptive learning pathways
- larger-scale evaluation using Open STACK Question Banks

These are future research directions and are not claimed as completed capabilities of the current deterministic prototype.

---

## Research Context

Adaptive STACK Tutor was developed as part of research into improving mathematics formative assessment using STACK-enabled resources.

The project investigates how existing mathematics question banks and learner-response evidence can be transformed into actionable adaptive pathways while preserving the mathematical grading logic authored in STACK.

The broader objective is to develop a reusable adaptive assessment workflow that can operate across different mathematics resources rather than being tied to one course, curriculum, or manually authored adaptive sequence.

---

## Technology

The project uses:

- Python
- FastAPI
- Pydantic
- STACK
- Moodle / STACK XML
- SQLite
- SQLAlchemy
- OpenPyXL
- PyPDF
- HTML
- CSS
- JavaScript
- Pytest

---

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the FastAPI server:

```bash
python -m uvicorn backend.app.main:app --reload --port 8020
```

Open the adaptive research interface:

```text
http://127.0.0.1:8020/adaptive-demo
```

---

## Current Research Checkpoint

The current curriculum-independent adaptive implementation was committed as:

```text
bae0602 Build curriculum-independent adaptive STACK tutor
```

At this checkpoint:

```text
155 adaptive tests passed
```

The checkpoint includes:

- adaptive runtime
- question-bank profiling
- adaptive graph construction
- document import
- STACK evidence handling
- remediation
- reassessment
- historical response support
- adaptive upload APIs
- adaptive browser demo

---

## License

The adaptive software developed in this repository is original project work.

External STACK question banks, curriculum materials, and educational resources remain subject to their respective licenses.

Third-party resources are not redistributed unless their licenses permit redistribution.

---

## Author

**Ibrahim Adam**

California Institute of Technology

B.S. Computer Science

Caltech Summer Undergraduate Research Fellowship (SURF)

---

## Acknowledgements

This project draws on research and development related to:

- STACK Computer-Aided Assessment
- Open STACK Question Banks
- adaptive learning
- mathematics education
- formative assessment
- learner modeling
- learning analytics
- educational data mining
- explainable educational decision systems

The project has been developed with guidance from mentors and researchers interested in improving adaptive mathematics learning and assessment.
