"""
Decision Log — committed module (Thu-Fri), enriches the Shared
Understanding Model.

Records each resolution of a Shared Understanding Model entry with
traceability metadata.

`source` (who answered) is distinct from `decision_source` (what kind
of knowledge it is) — this split enables finer-grained traceability.

Feeds into: Requirements Generator (optional appendix), Dashboard (if built).
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import date
from pathlib import Path
from typing import Literal
import json
import uuid

Category = Literal["business_rule", "actor", "assumption", "constraint"]
Source = Literal["product_owner", "inferred"]
DecisionSource = Literal[
    "user_explicit", "inference", "business_rule", "assumption", "external_constraint"
]
Confidence = Literal["high", "medium", "low"]


@dataclass
class Decision:
  category: Category
  question: str
  answer: str
  reason: str
  source: Source
  decision_source: DecisionSource
  confidence: Confidence
  decision_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
  date_recorded: str = field(default_factory=lambda: date.today().isoformat())


class DecisionLog:
  def __init__(self):
    self.decisions: list[Decision] = []

  def record(
    self,
    category: Category,
    question: str,
    answer: str,
    reason: str,
    source: Source,
    decision_source: DecisionSource,
    confidence: Confidence,
  ) -> Decision:
    decision = Decision(
      category=category,
      question=question,
      answer=answer,
      reason=reason,
      source=source,
      decision_source=decision_source,
      confidence=confidence,
    )
    self.decisions.append(decision)
    return decision

  def by_category(self, category: Category) -> list[Decision]:
    return [d for d in self.decisions if d.category == category]

  def low_confidence(self) -> list[Decision]:
    """Useful for a future Dashboard / for flagging assumptions worth
    double-checking before finalizing requirements."""
    return [d for d in self.decisions if d.confidence == "low"]

  def to_dict(self) -> dict:
    return {"decisions": [asdict(d) for d in self.decisions]}

  @classmethod
  def from_dict(cls, data: dict) -> "DecisionLog":
    log = cls()
    log.decisions = [Decision(**d) for d in data.get("decisions", [])]
    return log

  def save(self, path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
    )

  @classmethod
  def load(cls, path: str | Path) -> "DecisionLog":
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return cls.from_dict(data)


if __name__ == "__main__":
  log = DecisionLog()
  log.record(
    category="business_rule",
    question="What happens if a course is at full capacity?",
    answer="Enrollment is rejected until a spot opens up.",
    reason="Explicitly stated by the user during clarification.",
    source="product_owner",
    decision_source="user_explicit",
    confidence="high",
  )
  log.record(
    category="assumption",
    question="(not asked — inferred from context)",
    answer="Only administrators can register students, not students themselves.",
    reason="User described the flow entirely from the administrator's perspective.",
    source="inferred",
    decision_source="assumption",
    confidence="low",
  )

  print(f"Total decisions: {len(log.decisions)}")
  print(f"Low confidence (worth double-checking): {len(log.low_confidence())}")
  for d in log.low_confidence():
    print(f"  - [{d.decision_id}] {d.answer}")
