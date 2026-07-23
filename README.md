# Shared Understanding Agent

> An AI collaborator for building shared understanding before software specification.

🚧 In active development for Hackathon Kiro AWS 2026 (July 20-27, 2026).

## The Problem
Most rework in Software Engineering doesn't originate during coding —
it originates earlier, when different stakeholders build different
interpretations of the same problem.

## Hypothesis
If an AI agent systematically guides the requirements clarification
stage through structured questions, it will be possible to build a
more complete shared understanding before formal software
specification — reducing omissions, ambiguities, and downstream rework.

## Research Motivation
This prototype is not intended to replace software engineers or
product owners. It explores whether AI can facilitate the
construction of shared understanding before software specification.
This prototype represents a first step in a broader research
interest in Human-AI Collaboration in Software Engineering.

## Architecture
Seven modules, each with a single responsibility, connected in one
pipeline:

```
Shared Understanding Model (3)
        ↓
Conversation Engine (1) ←→ Clarification Engine (2)
        ↓
Open Questions (5) ← Decision Log (4, enriches 3)
        ↓
Requirements Generator (6)
        ↓
Kiro Integration (7)
```

| # | Module | Responsibility |
|---|---|---|
| 1 | **Conversation Engine** | Manages the dialogue turn with Bedrock; keeps a structured, timestamped history. |
| 2 | **Clarification Engine** | Decides what to ask next by comparing the model against minimum thresholds. |
| 3 | **Shared Understanding Model** | Central data structure: actors, business rules, entities, constraints, dependencies, edge cases, goals. |
| 4 | **Decision Log** | Records every resolved item with traceability (who answered, what kind of knowledge, confidence). |
| 5 | **Open Questions** | Computes remaining gaps against thresholds; never reports "done" if gaps remain. |
| 6 | **Requirements Generator** | Synthesizes the model into `requirements.md` (User Stories, Business Rules, Edge Cases, Open Questions, Summary). |
| 7 | **Kiro Integration** | Hands `requirements.md` to Kiro to produce the formal EARS spec. |

**Stack:** Python + boto3 (Bedrock SDK) · Streamlit (demo UI, in progress)
· JSON on disk (Shared Understanding Model persistence) · AWS Amplify
(demo hosting) · Claude / Amazon Nova via Bedrock.

## How to Run It
```bash
# 1. Install dependencies
pip install boto3 pytest

# 2. Configure AWS credentials (IAM user with Bedrock access)
aws configure

# 3. Run the test suite (no AWS needed)
python -m pytest tests/ -v

# 4. Run a real clarification session against Bedrock
python src/run_real_session.py
```

The last command starts an interactive session: it asks one question at
a time in the terminal, and once every Shared Understanding Model
category meets its minimum threshold, it saves the result to
`demo/requirements_with_agent.md`.

## Before / After Comparison
To test the hypothesis, the same initial statement was given directly to
Kiro (no agent involved) and, separately, run through the full agent
pipeline first. Full protocol, methodology, and qualitative findings are
in [`demo/before_after_protocol.md`](demo/before_after_protocol.md).

**Key finding (baseline, without agent):** Kiro's own spec, generated
directly from the initial statement, defined only an "administrator"
actor and never asked whether students interact with the system
directly — a significant product decision left implicit. It also never
considered any external dependency. These are exactly the kind of gaps
the Clarification Engine is designed to surface before specification.

| Metric | Without agent | With agent |
|---|---|---|
| Actors | 1 | — |
| Business Rules | 5 | — |
| Edge Cases | 4 | — |
| Constraints | 2 | — |
| Open Questions detected | 0 | — |

_(Full table updated in `demo/before_after_protocol.md` once the "with
agent" run is complete.)_

## Current Limitations
- Single stakeholder conversation — no multi-participant sessions yet.
- No conflict resolution between stakeholders.
- No domain ontology.
- No empirical validation yet — the before/after comparison is
  illustrative, not a controlled study.
- No quantitative evaluation beyond manual category counts.
- The extraction step (turning a free-text answer into structured data)
  relies on prompting a general-purpose model; it has not been
  systematically evaluated for accuracy.

## Future Research
Multi-stakeholder conversations, conflict detection between
stakeholders, validation of a coverage dashboard, an empirical study
with real teams, and integration with Software Engineering metrics
(e.g. correlating shared-understanding coverage with downstream rework).

A related direction already identified but not implemented in this
hackathon: an **Assumption Detector** that flags hedged language
("I assume...", "probably...") as low-confidence assumptions rather than
confirmed facts — connecting directly to the Decision Log's confidence
field.

## Repository Structure
```
src/
  conversation_engine.py        # Module 1
  clarification_engine.py       # Module 2
  shared_understanding_model.py # Module 3
  decision_log.py               # Module 4
  open_questions.py             # Module 5
  requirements_generator.py     # Module 6
  bedrock_llm_client.py         # Bedrock implementation of the LLM client
  bedrock_extractor.py          # Bedrock implementation of the extractor
  orchestrator.py               # Ties everything into a clarification session
  prompts.py                    # Single source of truth for prompts / test scenario
  run_real_session.py           # Entry point: real interactive session with Bedrock
kiro_integration/                # Module 7
demo/
  requirements_without_agent.md  # Baseline spec (Kiro, no agent)
  requirements_with_agent.md     # Spec produced via the full pipeline (pending)
  before_after_protocol.md       # Comparison methodology, metrics, findings
tests/                           # pytest suite for all pure-logic modules
```
