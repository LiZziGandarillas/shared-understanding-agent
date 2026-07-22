"""
Shared Understanding Model — MVP module (foundation of the system).

Central structure where the understanding of the problem accumulates,
organized by category: actors, business_rules, entities, constraints,
dependencies, edge_cases, goals.

Feeds into: Clarification Engine, Requirements Generator, Decision Log.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal
import json

THRESHOLDS: dict[str, int] = {
  "actors": 2,
  "business_rules": 3,
  "entities": 2,
  "constraints": 1,
  "dependencies": 1,
  "edge_cases": 2,
  "goals": 1,
}


@dataclass
class Actor:
  name: str
  role: str
  permissions: list[str] = field(default_factory=list)


@dataclass
class BusinessRule:
  rule: str
  source_turn: int


@dataclass
class Entity:
  name: str
  attributes: list[str] = field(default_factory=list)


@dataclass
class Constraint:
  constraint: str
  type: Literal["technical", "legal", "operational"] = "technical"


@dataclass
class Dependency:
  system: str
  description: str = ""


@dataclass
class EdgeCase:
  scenario: str
  resolved: bool = False


@dataclass
class Goal:
  goal: str
  acceptance_criteria: str = ""


@dataclass
class SharedUnderstandingModel:
  """Accumulates everything learned about the problem, by category."""

  actors: list[Actor] = field(default_factory=list)
  business_rules: list[BusinessRule] = field(default_factory=list)
  entities: list[Entity] = field(default_factory=list)
  constraints: list[Constraint] = field(default_factory=list)
  dependencies: list[Dependency] = field(default_factory=list)
  edge_cases: list[EdgeCase] = field(default_factory=list)
  goals: list[Goal] = field(default_factory=list)

  def count(self, category: str) -> int:
    return len(getattr(self, category))

  def is_covered(self, category: str) -> bool:
    return self.count(category) >= THRESHOLDS[category]

  def coverage_summary(self) -> dict[str, dict[str, int | bool]]:
    return {
      cat: {
        "count": self.count(cat),
        "minimum": THRESHOLDS[cat],
        "covered": self.is_covered(cat),
      }
      for cat in THRESHOLDS
    }

  def least_covered_category(self) -> str | None:
    """Returns the category furthest from its threshold, or None if all covered."""
    gaps = {
      cat: THRESHOLDS[cat] - self.count(cat)
      for cat in THRESHOLDS
      if not self.is_covered(cat)
    }
    if not gaps:
      return None
    return max(gaps, key=gaps.get)

  def to_dict(self) -> dict:
    return asdict(self)

  @classmethod
  def from_dict(cls, data: dict) -> "SharedUnderstandingModel":
    return cls(
      actors=[Actor(**a) for a in data.get("actors", [])],
      business_rules=[BusinessRule(**b) for b in data.get("business_rules", [])],
      entities=[Entity(**e) for e in data.get("entities", [])],
      constraints=[Constraint(**c) for c in data.get("constraints", [])],
      dependencies=[Dependency(**d) for d in data.get("dependencies", [])],
      edge_cases=[EdgeCase(**ec) for ec in data.get("edge_cases", [])],
      goals=[Goal(**g) for g in data.get("goals", [])],
    )

  def save(self, path: str | Path) -> None:
    Path(path).write_text(
      json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
    )

  @classmethod
  def load(cls, path: str | Path) -> "SharedUnderstandingModel":
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return cls.from_dict(data)


if __name__ == "__main__":
  model = SharedUnderstandingModel()
  model.actors.append(Actor(name="Student", role="student", permissions=["enroll", "view_grades"]))
  model.business_rules.append(BusinessRule(rule="A student cannot enroll if the course is full", source_turn=1))

  print("Coverage summary:")
  for cat, info in model.coverage_summary().items():
    print(f"  {cat}: {info}")
  print("Least covered category:", model.least_covered_category())
