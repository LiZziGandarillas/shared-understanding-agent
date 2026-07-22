"""
Clarification Engine — MVP module.

Decides what to ask next. Compares the current Shared Understanding
Model against the minimum thresholds and generates the next question
for the least-covered category.

Input: current Shared Understanding Model + conversation history.
Output: next question tagged by category, or a "covered" signal.
Depends on: Shared Understanding Model, Bedrock.
Feeds into: Conversation Engine.

NOTE: like conversation_engine.py, the actual question phrasing will
come from Bedrock. For now `next_question()` returns a template
question per category so the pipeline is testable end-to-end today.
"""
from __future__ import annotations
from dataclasses import dataclass

from shared_understanding_model import SharedUnderstandingModel

# Fallback template questions — used until the LLM-generated version
# replaces this (same seam idea as MockLLMClient in conversation_engine.py).
TEMPLATE_QUESTIONS: dict[str, str] = {
    "actors": "Who are the different types of users that will interact with this system, and what can each of them do?",
    "business_rules": "Are there any rules, policies, or eligibility criteria that determine what's allowed here?",
    "entities": "What are the key pieces of data this system needs to track, and what details matter about each one?",
    "constraints": "Are there any technical, legal, or operational limits this system must respect?",
    "dependencies": "Does this system need to talk to any other system or feature?",
    "edge_cases": "What should happen in an unusual or non-standard situation — for example, a duplicate, a failure, or a conflict?",
    "goals": "How will you know this system is working correctly — what does success look like?",
}


@dataclass
class ClarificationResult:
    covered: bool
    category: str | None = None
    question: str | None = None


class ClarificationEngine:
    def __init__(self, model: SharedUnderstandingModel):
        self.model = model

    def next_question(self) -> ClarificationResult:
        category = self.model.least_covered_category()
        if category is None:
            return ClarificationResult(covered=True)
        return ClarificationResult(
            covered=False,
            category=category,
            question=TEMPLATE_QUESTIONS[category],
        )


if __name__ == "__main__":
    model = SharedUnderstandingModel()
    engine = ClarificationEngine(model)
    result = engine.next_question()
    print(f"Category: {result.category}")
    print(f"Question: {result.question}")
