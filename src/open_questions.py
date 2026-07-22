"""
Open Questions — MVP module (low cost, high value).

At closing time, computes which categories remain below the minimum
threshold and lists them as unresolved questions. Never reports
"all done" if gaps remain.

Depends on: Shared Understanding Model, thresholds.
"""
from __future__ import annotations
from dataclasses import dataclass

from shared_understanding_model import SharedUnderstandingModel, THRESHOLDS

CATEGORY_LABELS = {
  "actors": "Actor",
  "business_rules": "Business rule",
  "entities": "Entity",
  "constraints": "Constraint",
  "dependencies": "Dependency",
  "edge_cases": "Edge case",
  "goals": "Goal / Acceptance criteria",
}


@dataclass
class OpenQuestion:
  category: str
  missing_count: int
  message: str


def compute_open_questions(model: SharedUnderstandingModel) -> list[OpenQuestion]:
  """Diff between threshold and what's captured. Empty list == fully covered."""
  questions: list[OpenQuestion] = []
  for category, minimum in THRESHOLDS.items():
    current = model.count(category)
    if current < minimum:
      missing = minimum - current
      label = CATEGORY_LABELS[category]
      questions.append(
        OpenQuestion(
          category=category,
          missing_count=missing,
          message=f"Missing {label.lower()}(s): need {missing} more "
          f"(have {current}/{minimum}).",
        )
      )
  return questions


def is_fully_covered(model: SharedUnderstandingModel) -> bool:
  return len(compute_open_questions(model)) == 0


def render_open_questions_markdown(model: SharedUnderstandingModel) -> str:
  """Used by Requirements Generator to embed the Open Questions section."""
  questions = compute_open_questions(model)
  if not questions:
    return "## Open Questions\n\nNone — all categories meet the minimum coverage threshold.\n"

  lines = ["## Open Questions\n"]
  for q in questions:
    lines.append(f"- **{q.message}**")
  return "\n".join(lines) + "\n"


if __name__ == "__main__":
  model = SharedUnderstandingModel()
  print(render_open_questions_markdown(model))
  print("Fully covered?", is_fully_covered(model))
