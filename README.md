# Adaptive STACK Tutor

An explainable adaptive mathematics learning platform that personalizes learning pathways for students transitioning from **Junior High School (JHS)** to **Senior High School (SHS)** in Ghana.

The project investigates how adaptive learning, learner modeling, and educational decision-making can be combined to help students strengthen prerequisite mathematical concepts before progressing to more advanced topics.

Unlike traditional learning platforms that present every learner with the same sequence of questions, Adaptive STACK Tutor aims to determine **what each learner should study next** based on their responses, learning history, and demonstrated understanding.

---

# Vision

The long-term vision is to build an adaptive learning platform that can:

- connect to external STACK/Open STACK Question Banks (OSQB);
- provide personalized mathematics practice;
- identify learner misconceptions;
- recommend appropriate remediation;
- guide learners from JHS mathematics into introductory SHS mathematics;
- support future research in adaptive learning, learning analytics, and Item Response Theory (IRT).

The final platform is intended to run on **phones, tablets, laptops, and desktop computers** using a responsive web interface.

---

# Research Motivation

Many students enter Senior High School with different levels of mathematical preparation.

Some learners are ready to progress immediately, while others require additional support with prerequisite concepts before moving forward.

This project investigates how a deterministic adaptive learning system can support learners by deciding:

- what question should come next;
- when to increase difficulty;
- when to review prerequisite concepts;
- when to provide targeted remediation;
- when the learner is ready to progress to a new concept.

---

# Current Research Question

> **How can an explainable deterministic sequencing engine use learner responses, question metadata, prerequisite relationships, and diagnostic outcomes to construct adaptive mathematics learning pathways for students transitioning from JHS to SHS?**

Future work will investigate how Item Response Theory (IRT), learning analytics, and statistical item difficulty can further improve adaptive decision-making.

---

# Current System

The current prototype includes:

- FastAPI backend
- Metadata-driven question repository
- Automatic symbolic answer evaluation using SymPy
- Learner progress tracking
- SQLite persistence
- Adaptive recommendation prototype
- Streamlit development dashboard
- Question-bank gateway contract
- Mock STACK/OSQB adapter
- Automated test suite

Current architecture:

```text
Learner
    ↓
Development Dashboard
    ↓
FastAPI Backend
    ↓
Adaptive Learning Service
    ↓
Question Repository
    ↓
SQLite Database
```

---

# Development Roadmap

## Completed

- FastAPI backend
- Question repository
- Student model
- Automatic answer evaluation
- Progress persistence
- Adaptive recommendation prototype
- Question-bank gateway
- Mock STACK adapter
- Automated testing

## Currently Building

- Deterministic Sequencing Engine
- Educational sequencing rules
- Learner-state model
- Question linking
- Curriculum mapping

## Future Work

- STACK/OSQB API integration
- Ghanaian curriculum mapping
- Potential Response Tree (PRT) integration
- Item Response Theory (IRT)
- HTML/CSS/JavaScript frontend
- Teacher analytics dashboard
- Progressive Web App (PWA)
- Digital textbook integration

---

# Adaptive Learning Philosophy

The project focuses on building the adaptive engine rather than manually creating mathematics questions.

Questions will ultimately come from an external question bank.

The primary research contribution is the adaptive decision process that determines:

- what happens after a learner answers correctly;
- what happens after a learner answers incorrectly;
- when remediation should occur;
- when learners should return from remediation;
- when learners should progress to more advanced concepts.

---

# Testing

The project follows a test-driven development workflow.

Current tests cover:

- automatic mathematical answer evaluation;
- learner progress updates;
- attempt history;
- question filtering;
- metadata handling;
- mock question-bank adapter;
- recommendation logic.

Run all tests using:

```bash
python -m pytest -v
```

---

# Repository Status

Current test status:

**23 tests passing**

The test suite grows together with the adaptive engine as new educational sequencing rules are implemented.

---

# Open Development

This project is being developed publicly to encourage collaboration from educators, researchers, and software engineers interested in adaptive learning.

Contributions will eventually be accepted through Pull Requests.

All proposed changes will be reviewed before they are merged into the main branch.

---

# Ownership

Copyright © 2026 Ibrahim Adam.

This project was created and is maintained by **Ibrahim Adam**.

Although the repository will evolve as an open collaborative research project, the project owner retains responsibility for reviewing, approving, and merging all contributions into the official codebase.

A project license will be selected after the research architecture and external API integrations have matured.

---

# Author

**Ibrahim Adam**

California Institute of Technology

Computer Science

Caltech Summer Undergraduate Research Fellowship
