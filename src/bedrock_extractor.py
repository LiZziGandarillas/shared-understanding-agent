"""
Bedrock Extractor — implements the Extractor protocol expected by
orchestrator.py.

Turns a free-text answer (e.g. "A student cannot enroll if the course
is full") into a structured entry for the corresponding Shared
Understanding Model category, by asking Bedrock to return JSON matching
that category's schema.

Swap it in like this:

  from bedrock_extractor import BedrockExtractor
  model, log, history = run_clarification_session(
    TEST_SCENARIO, real_answer_provider, BedrockExtractor()
  )

If the model returns malformed JSON, extract() returns None (same
contract as MockExtractor) — the orchestrator already skips a turn
when nothing usable was extracted, so callers don't need special
handling.
"""
from __future__ import annotations
import json
import boto3

from shared_understanding_model import (
  Actor,
  BusinessRule,
  Entity,
  Constraint,
  Dependency,
  EdgeCase,
  Goal,
)

REGION = "us-east-1"
MODEL_ID = "amazon.nova-micro-v1:0"

EXTRACTION_INSTRUCTIONS: dict[str, str] = {
  "actors": (
    'Extract a JSON object: {"name": str, "role": str, "permissions": [str]}. '
    'Example: {"name": "Administrator", "role": "administrator", "permissions": ["manage students"]}'
  ),
  "business_rules": (
    'Extract a JSON object: {"rule": str}. '
    'Example: {"rule": "A student cannot enroll if the course is full"}'
  ),
  "entities": (
    'Extract a JSON object: {"name": str, "attributes": [str]}. '
    'Example: {"name": "Course", "attributes": ["name", "code", "max_capacity"]}'
  ),
  "constraints": (
    'Extract a JSON object: {"constraint": str, "type": "technical"|"legal"|"operational"}. '
    'Example: {"constraint": "Must comply with data privacy regulations", "type": "legal"}'
  ),
  "dependencies": (
    'Extract a JSON object: {"system": str, "description": str}. '
    'Example: {"system": "None", "description": "No external integration for the MVP"}'
  ),
  "edge_cases": (
    'Extract a JSON object: {"scenario": str}. '
    'Example: {"scenario": "Student tries to enroll in a full course"}'
  ),
  "goals": (
    'Extract a JSON object: {"goal": str, "acceptance_criteria": str}. '
    'Example: {"goal": "Track enrollment accurately", "acceptance_criteria": "all enrollments are queryable"}'
  ),
}

_CATEGORY_TO_CLASS = {
  "actors": Actor,
  "business_rules": BusinessRule,
  "entities": Entity,
  "constraints": Constraint,
  "dependencies": Dependency,
  "edge_cases": EdgeCase,
  "goals": Goal,
}


class BedrockExtractor:
  def __init__(self, model_id: str = MODEL_ID, region: str = REGION):
    self.model_id = model_id
    self.client = boto3.client("bedrock-runtime", region_name=region)

  def extract(self, category: str, question: str, answer: str) -> object | None:
    if not answer.strip() or category not in EXTRACTION_INSTRUCTIONS:
      return None

    system_prompt = (
      "You extract structured data from a single user answer in a "
      "requirements-clarification conversation. Respond with ONLY the "
      "JSON object described below — no extra text, no markdown fences.\n\n"
      f"{EXTRACTION_INSTRUCTIONS[category]}"
    )

    body = {
      "messages": [
        {
          "role": "user",
          "content": [{"text": f"Question asked: {question}\nUser answer: {answer}"}],
        }
      ],
      "system": [{"text": system_prompt}],
      "inferenceConfig": {"maxTokens": 300, "temperature": 0},
    }

    response = self.client.invoke_model(modelId=self.model_id, body=json.dumps(body))
    result = json.loads(response["body"].read())
    raw_text = result["output"]["message"]["content"][0]["text"]

    try:
      parsed = json.loads(raw_text)
      entry_class = _CATEGORY_TO_CLASS[category]
      return entry_class(**parsed)
    except (json.JSONDecodeError, TypeError, KeyError):
      return None


if __name__ == "__main__":
  extractor = BedrockExtractor()
  result = extractor.extract(
    category="business_rules",
    question="Are there any rules, policies, or eligibility criteria that determine what's allowed here?",
    answer="A student cannot enroll if the course is full",
  )
  print("Extracted:", result)
