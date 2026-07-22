"""
Requirements Generator — MVP module.

Generates requirements.md from the Shared Understanding Model, Open
Questions, and (optionally) the Decision Log. Includes User Stories,
Business Rules, Edge Cases, Assumptions, Open Questions, and a
one-page Shared Understanding Summary.

Input: Shared Understanding Model + Open Questions + Decision Log (optional).
Output: requirements.md.
Feeds into: Kiro Integration.
"""
from __future__ import annotations
from pathlib import Path

from shared_understanding_model import SharedUnderstandingModel
from open_questions import render_open_questions_markdown, is_fully_covered


def _render_actors(model: SharedUnderstandingModel) -> str:
  if not model.actors:
      return "_No actors captured yet._\n"
  lines = []
  for actor in model.actors:
      perms = ", ".join(actor.permissions) if actor.permissions else "not specified"
      lines.append(f"- **{actor.name}** ({actor.role}) — can: {perms}")
  return "\n".join(lines) + "\n"


def _article_for(word: str) -> str:
  return "an" if word[:1].lower() in "aeiou" else "a"


def _render_user_stories(model: SharedUnderstandingModel) -> str:
  """Derives simple user stories from actors + goals. This is a synthesis
  view over data we already have — no new logic, no LLM call needed."""
  if not model.actors or not model.goals:
      return "_Not enough information yet to derive user stories (needs at least one actor and one goal)._\n"

  lines = []
  for actor in model.actors:
      article = _article_for(actor.role)
      for goal in model.goals:
          lines.append(
              f"- As {article} **{actor.role}**, I want to {goal.goal.lower()}, "
              f"so that {goal.acceptance_criteria or 'the intended outcome is achieved'}."
          )
  return "\n".join(lines) + "\n"


def _render_business_rules(model: SharedUnderstandingModel) -> str:
  if not model.business_rules:
      return "_No business rules captured yet._\n"
  return "\n".join(f"- {br.rule}" for br in model.business_rules) + "\n"


def _render_edge_cases(model: SharedUnderstandingModel) -> str:
  if not model.edge_cases:
      return "_No edge cases captured yet._\n"
  lines = []
  for ec in model.edge_cases:
      status = "resolved" if ec.resolved else "unresolved"
      lines.append(f"- {ec.scenario} _({status})_")
  return "\n".join(lines) + "\n"


def _render_shared_understanding_summary(model: SharedUnderstandingModel) -> str:
  """One-page synthesis: Main Goal, Actors, Business Context,
  Critical Constraints, Remaining Risks."""
  main_goal = model.goals[0].goal if model.goals else "_not defined yet_"
  actor_names = ", ".join(a.name for a in model.actors) or "_none captured_"
  constraint_list = (
      "; ".join(c.constraint for c in model.constraints) or "_none captured_"
  )
  remaining_risks = (
      "None — all categories meet the minimum coverage threshold."
      if is_fully_covered(model)
      else "See Open Questions section below."
  )

  return (
      f"- **Main Goal:** {main_goal}\n"
      f"- **Actors:** {actor_names}\n"
      f"- **Business Context:** {len(model.business_rules)} business rule(s), "
      f"{len(model.entities)} entity type(s) captured.\n"
      f"- **Critical Constraints:** {constraint_list}\n"
      f"- **Remaining Risks:** {remaining_risks}\n"
  )


def generate_requirements_md(model: SharedUnderstandingModel) -> str:
  sections = [
      "# Requirements\n",
      "## Shared Understanding Summary\n",
      _render_shared_understanding_summary(model),
      "\n## Actors & Roles\n",
      _render_actors(model),
      "\n## User Stories\n",
      _render_user_stories(model),
      "\n## Business Rules\n",
      _render_business_rules(model),
      "\n## Edge Cases\n",
      _render_edge_cases(model),
      "\n",
      render_open_questions_markdown(model),
  ]
  return "".join(sections)


def save_requirements_md(model: SharedUnderstandingModel, path: str | Path) -> None:
  Path(path).write_text(generate_requirements_md(model), encoding="utf-8")


if __name__ == "__main__":
  from shared_understanding_model import Actor, BusinessRule, Goal, EdgeCase

  model = SharedUnderstandingModel()
  model.actors.append(Actor(name="Student", role="student", permissions=["enroll", "view own grades"]))
  model.actors.append(Actor(name="Administrator", role="administrator", permissions=["manage students", "manage courses"]))
  model.business_rules.append(BusinessRule(rule="A student cannot enroll if the course is full", source_turn=1))
  model.goals.append(Goal(goal="Track student enrollment and grades accurately", acceptance_criteria="all enrollments and grades are queryable per student"))
  model.edge_cases.append(EdgeCase(scenario="Student tries to enroll in a course they're already enrolled in", resolved=True))

  print(generate_requirements_md(model))
