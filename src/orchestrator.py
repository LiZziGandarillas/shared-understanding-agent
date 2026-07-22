"""
Orchestrator — ties the pipeline together into a real clarification loop.

Loop: Clarification Engine picks the next question -> Conversation Engine
poses it and logs the turn -> the user answers -> an Extractor turns that
free-text answer into a structured entry in the Shared Understanding
Model -> repeat until every category meets its threshold.

Extraction (turning "the course has a max of 30 students" into a
structured Constraint) needs an LLM. Until Bedrock's daily quota frees
up, `MockExtractor` stands in — same seam pattern as MockLLMClient in
conversation_engine.py. Swap it for a BedrockExtractor later; nothing
else in this file changes.
"""
from __future__ import annotations
from typing import Callable, Protocol

from shared_understanding_model import (
  SharedUnderstandingModel,
  Actor,
  BusinessRule,
  Entity,
  Constraint,
  Dependency,
  EdgeCase,
  Goal,
)
from clarification_engine import ClarificationEngine
from conversation_engine import ConversationEngine, MockLLMClient, Turn
from decision_log import DecisionLog
from open_questions import render_open_questions_markdown
from requirements_generator import generate_requirements_md

SYSTEM_PROMPT = (
  "You are a requirements clarification assistant. Ask exactly ONE "
  "short, specific question at a time to uncover actors, business "
  "rules, entities, constraints, dependencies, edge cases, and goals "
  "for the system the user describes. Never assume an answer the "
  "user hasn't given."
)

AnswerProvider = Callable[[str, str], str]


class Extractor(Protocol):
  """Turns a free-text answer into a structured update for the given
  category. Returns None if nothing usable could be extracted."""

  def extract(self, category: str, question: str, answer: str) -> object | None: ...


class MockExtractor:
  """Naive keyword-based extraction — good enough to exercise the full
  pipeline before Bedrock is wired up. Not meant to be smart."""

  def extract(self, category: str, question: str, answer: str) -> object | None:
    if not answer.strip():
      return None

    if category == "actors":
      role = answer.split(",")[0].strip().lower()
      return Actor(name=role.capitalize(), role=role, permissions=[])
    if category == "business_rules":
      return BusinessRule(rule=answer.strip(), source_turn=0)
    if category == "entities":
      name = answer.split(",")[0].strip()
      return Entity(name=name, attributes=[])
    if category == "constraints":
      return Constraint(constraint=answer.strip(), type="technical")
    if category == "dependencies":
      return Dependency(system=answer.strip(), description="")
    if category == "edge_cases":
      return EdgeCase(scenario=answer.strip(), resolved=False)
    if category == "goals":
      return Goal(goal=answer.strip(), acceptance_criteria="")
    return None


def _add_to_model(model: SharedUnderstandingModel, category: str, entry: object) -> None:
  getattr(model, category).append(entry)


def run_clarification_session(
  initial_statement: str,
  get_answer: AnswerProvider,
  extractor: Extractor,
  max_turns: int = 20,
) -> tuple[SharedUnderstandingModel, DecisionLog, list[Turn]]:
  """Runs the full loop until every category is covered or max_turns is hit.
  `get_answer(category, question)` supplies the user's reply — a real
  terminal prompt in interactive use, or category-aware canned answers
  in a scripted demo. The category must be passed (not just the question
  text) because Clarification Engine reorders categories dynamically as
  the model fills up — a flat, fixed-order answer list would desync."""
  model = SharedUnderstandingModel()
  decision_log = DecisionLog()
  conversation = ConversationEngine(MockLLMClient(), system_prompt=SYSTEM_PROMPT)
  conversation.history.append(Turn(role="user", text=initial_statement))

  clarifier = ClarificationEngine(model)

  for _ in range(max_turns):
    result = clarifier.next_question()
    if result.covered:
      break

    conversation.history.append(Turn(role="assistant", text=result.question))
    answer = get_answer(result.category, result.question)
    conversation.history.append(Turn(role="user", text=answer))

    entry = extractor.extract(result.category, result.question, answer)
    if entry is not None:
      _add_to_model(model, result.category, entry)
      decision_log.record(
        category="business_rule" if result.category == "business_rules" else "assumption",
        question=result.question,
        answer=answer,
        reason="Captured during the clarification conversation.",
        source="product_owner",
        decision_source="user_explicit",
        confidence="medium",
      )

  return model, decision_log, conversation.history


if __name__ == "__main__":
  TEST_SCENARIO = (
    "Sistema para gestionar estudiantes: permite registrar estudiantes, "
    "inscribirlos en cursos, y ver su historial de calificaciones."
  )

  canned_answers: dict[str, list[str]] = {
    "actors": [
      "Administrator, who manages students and courses",
      "Student, who can view their own grades",
    ],
    "business_rules": [
      "A student cannot enroll if the course is full",
      "A student cannot enroll twice in the same course",
      "Grades must be between 0 and 100",
    ],
    "entities": [
      "Course, with a name, code and max capacity",
      "Enrollment, linking a student to a course",
    ],
    "constraints": [
      "The system must comply with student data privacy regulations",
    ],
    "dependencies": [
      "No external system integration for the MVP",
    ],
    "edge_cases": [
      "What happens if the course is already full when enrolling",
      "What happens if a student tries to enroll twice",
    ],
    "goals": [
      "Success means every enrollment and grade is queryable per student",
    ],
  }

  def scripted_answer_provider(category: str, question: str) -> str:
    remaining = canned_answers.get(category, [])
    return remaining.pop(0) if remaining else ""

  model, decision_log, history = run_clarification_session(
    TEST_SCENARIO, scripted_answer_provider, MockExtractor()
  )

  print("=== Conversation ===")
  for turn in history:
    print(f"[{turn.role}] {turn.text}")

  print("\n=== Coverage ===")
  for cat, info in model.coverage_summary().items():
    print(f"  {cat}: {info}")

  print("\n=== Open Questions ===")
  print(render_open_questions_markdown(model))

  print("=== Decision Log ===")
  print(f"Total decisions recorded: {len(decision_log.decisions)}")

  print("=== requirements.md ===")
  print(generate_requirements_md(model))
