"""
Conversation Engine — MVP module.

Manages the dialogue turn: receives the initial problem statement,
maintains conversation history, sends each turn to Bedrock, and
receives the next clarifying question or synthesis.

Input: initial statement + user responses per turn.
Output: structured history (role, text, timestamp).
Depends on: Bedrock.
Feeds into: Clarification Engine, Shared Understanding Model.

NOTE: Bedrock is not wired up yet (pending AWS account activation).
`call_llm()` is the single seam to replace with a real boto3 call —
everything else in this module is already final.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol


@dataclass
class Turn:
  role: str
  text: str
  timestamp: str = field(
    default_factory=lambda: datetime.now(timezone.utc).isoformat()
  )


class LLMClient(Protocol):
  """Minimal interface the Conversation Engine needs from an LLM backend.
  A real BedrockLLMClient (boto3) will implement this same shape."""

  def complete(self, system_prompt: str, history: list[Turn]) -> str: ...


class MockLLMClient:
  """Stand-in used until Bedrock access is confirmed. Returns a canned
  question so the rest of the pipeline (Clarification Engine, etc.) can
  be developed and tested end-to-end without AWS."""

  def complete(self, system_prompt: str, history: list[Turn]) -> str:
    return (
      "[MOCK] Who are the different types of users that will interact "
      "with this system, and what can each of them do?"
    )


class ConversationEngine:
  def __init__(self, llm_client: LLMClient, system_prompt: str):
    self.llm_client = llm_client
    self.system_prompt = system_prompt
    self.history: list[Turn] = []

  def start(self, initial_statement: str) -> Turn:
    self.history.append(Turn(role="user", text=initial_statement))
    return self._next_assistant_turn()

  def respond(self, user_text: str) -> Turn:
    self.history.append(Turn(role="user", text=user_text))
    return self._next_assistant_turn()

  def _next_assistant_turn(self) -> Turn:
    reply = self.llm_client.complete(self.system_prompt, self.history)
    turn = Turn(role="assistant", text=reply)
    self.history.append(turn)
    return turn


if __name__ == "__main__":
  engine = ConversationEngine(MockLLMClient(), system_prompt="(see docs/prompts/initial_clarification_prompt.md)")
  first_question = engine.start("Necesito un sistema para gestionar estudiantes.")
  print("Assistant:", first_question.text)
