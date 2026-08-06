# Adaptive STACK Tutor

A curriculum-driven, explainable adaptive mathematics learning framework that uses learner evidence—not simply question correctness—to guide personalized learning pathways from foundational concepts to more advanced mathematics.

Adaptive STACK Tutor is being developed primarily for the **Ghanaian educational context**, while remaining curriculum-agnostic so that additional curriculum frameworks can be supported without redesigning the adaptive learning engine.

The project combines curriculum modeling, adaptive learning, learner modeling, educational decision-making, and STACK assessment technology to provide personalized mathematics learning experiences.

---

# Vision

The long-term vision is to build an adaptive mathematics platform that:

- supports students transitioning from Junior High School (JHS) to Senior High School (SHS);
- identifies learner misconceptions through formative assessment;
- recommends targeted remediation based on curriculum concepts;
- personalizes learning pathways using learner evidence;
- integrates with external STACK/Open STACK Question Banks (OSQB);
- supports future educational research in adaptive learning, learning analytics, psychometrics, and Item Response Theory (IRT);
- remains flexible enough to support multiple national curricula.

Although the initial implementation uses curriculum resources from Kenya during development, the architecture is intentionally designed so that Ghanaian curriculum profiles can be incorporated without modifying the adaptive engine itself.

---

# Why This Project Exists

Many learners enter Senior High School with different levels of mathematical preparation.

Some students are ready to progress immediately.

Others require additional support with prerequisite concepts before they can successfully learn more advanced mathematics.

Traditional online learning systems often present every learner with exactly the same sequence of questions regardless of their understanding.

Adaptive STACK Tutor instead attempts to answer a different educational question:

> **What should this learner study next?**

Rather than adapting only at the question level, the system adapts at the curriculum concept level.

---

# Educational Philosophy

Adaptive STACK Tutor is built around one central idea:

**Questions are not the learning objective.**

**Questions provide evidence of understanding.**

Each learner response contributes evidence about a curriculum concept.

The adaptive engine uses accumulated evidence to determine whether the learner should:

- continue practising the current concept;
- receive targeted remediation;
- revisit prerequisite concepts;
- complete a mastery check;
- progress to the next curriculum concept.

Because the adaptive engine reasons about concepts rather than individual questions, it remains independent of any specific question bank or curriculum implementation.

---

# Research Question

> **How can an explainable deterministic adaptive learning engine use curriculum structure, learner evidence, prerequisite relationships, and diagnostic outcomes to construct personalized mathematics learning pathways?**

Future research will investigate:

- Item Response Theory (IRT);
- learning analytics;
- learner modeling;
- probabilistic decision-making;
- adaptive difficulty estimation;
- educational data mining.

---

# Current Architecture

```text
Student
        │
        ▼
FastAPI Session API
        │
        ▼
Adaptive Session Service
        │
        ▼
STACK Evaluation Adapter
        │
        ▼
Adaptive Learning Session Engine
        │
        ▼
Concept Decision Engine
        │
        ▼
Concept Evidence Tracker
        │
        ▼
Curriculum Mapping
        │
        ▼
Curriculum Repository
        │
        ▼
STACK Question Bank
```

Each component has a single responsibility and can evolve independently.

---

# Adaptive Learning Workflow

```text
Learner begins a curriculum concept
            │
            ▼
System selects an evidence question
            │
            ▼
Learner submits an answer
            │
            ▼
STACK evaluates the mathematics
            │
            ▼
Score, feedback and answer notes returned
            │
            ▼
Concept evidence updated
            │
            ▼
Decision engine evaluates learner progress
            │
            ▼
System selects the next educational action
            │
            ▼
Next question or concept is presented
```

---

# Current Features

The current prototype includes:

- Curriculum Repository
- Curriculum Mapping Repository
- Curriculum Concept Loader
- Question Repository
- Automatic symbolic answer evaluation using SymPy
- STACK XML parser
- STACK inventory generator
- Sequencing template generator
- Sequencing map validator
- Deterministic sequencing engine
- Concept evidence tracking
- Concept decision engine
- Adaptive learning session engine
- STACK evaluation adapter
- Adaptive session service
- FastAPI REST API
- SQLite persistence
- Automated testing framework

---

# Repository Structure

```text
backend/
    api/
    database/
    integrations/
        stack_api/
        stack_xml/
    learning/
        concept_decision/
        concept_evidence/
        curriculum/
        curriculum_mapping/
        recommendation/
        sequencing/
        session/
        student_model/
    services/

datasets/

examples/

resources/

tests/
```

---

# Current Development Status

## Completed

- Curriculum repository
- Curriculum mapping
- Student model
- Symbolic mathematical answer evaluation
- SQLite persistence
- STACK XML parser
- Question inventory generation
- Deterministic sequencing engine
- Sequencing validator
- Concept evidence tracker
- Concept decision engine
- Adaptive learning session engine
- STACK evaluation adapter
- Adaptive session service
- FastAPI session API
- Comprehensive automated testing

---

## Currently In Progress

- Live STACK API integration
- HTTP STACK evaluation client
- XML → STACK request conversion
- Real PRT evaluation
- Live feedback integration

---

## Planned Future Work

- Ghana curriculum profile
- Multiple curriculum support
- Teacher authoring interface
- Learning analytics dashboard
- Explainable learner progress visualization
- Item Response Theory (IRT)
- Adaptive difficulty estimation
- Mobile application
- Progressive Web App (PWA)
- Digital textbook integration

---

# Testing

The project follows a Test-Driven Development (TDD) workflow.

Current automated tests cover:

- symbolic mathematics evaluation;
- curriculum loading;
- curriculum mapping;
- sequencing validation;
- sequencing generation;
- STACK XML parsing;
- STACK inventory generation;
- question repositories;
- concept evidence tracking;
- concept decision engine;
- adaptive learning session engine;
- STACK evaluation adapter;
- adaptive session service;
- FastAPI session endpoints.

Run the complete test suite:

```bash
python -m pytest -v
```

Current status:

**126 automated tests passing**

---

# Open Research Development

Adaptive STACK Tutor is being developed as an open research software project.

The goal is to encourage collaboration among:

- mathematics educators;
- computer scientists;
- learning scientists;
- educational researchers;
- software engineers.

Future contributions will be accepted through Pull Requests after review.

---

# Licensing

The adaptive learning framework developed in this repository is original work.

Some external curriculum resources and STACK question banks used during research are provided under their respective licenses and are **not redistributed** in this repository unless permitted by their owners.

Third-party educational resources remain the property of their respective authors.

---

# Author

**Ibrahim Adam**

California Institute of Technology

B.S. Computer Science

Caltech Summer Undergraduate Research Fellowship (SURF)

---

# Acknowledgements

This project draws upon research and discussions surrounding:

- Adaptive Learning
- STACK Computer-Aided Assessment
- Open STACK Question Banks (OSQB)
- Learning Analytics
- Curriculum Modeling
- Educational Data Mining
- Explainable Educational Decision Systems

The project is being developed in collaboration with mentors and researchers interested in advancing adaptive mathematics education.