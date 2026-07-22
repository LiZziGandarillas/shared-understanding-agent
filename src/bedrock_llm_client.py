"""
Bedrock LLM Client — implements the LLMClient protocol expected by
conversation_engine.py.

Swap it in like this:

    from bedrock_llm_client import BedrockLLMClient
    engine = ConversationEngine(BedrockLLMClient(), system_prompt=SYSTEM_PROMPT)

Model defaults to Nova Micro (cheapest, good for iterating on prompts).
Switch to Claude for the final demo by passing model_id explicitly.
"""
from __future__ import annotations
import json
import boto3

from conversation_engine import Turn

REGION = "us-east-1"

NOVA_MICRO = "amazon.nova-micro-v1:0"
NOVA_LITE = "amazon.nova-lite-v1:0"

CLAUDE_DEMO_MODEL = "anthropic.claude-3-5-sonnet-20241022-v2:0"

class BedrockLLMClient:
  def __init__(self, model_id: str = NOVA_MICRO, region: str = REGION):
      self.model_id = model_id
      self.client = boto3.client("bedrock-runtime", region_name=region)

  def complete(self, system_prompt: str, history: list[Turn]) -> str:
      messages = [
          {"role": turn.role, "content": [{"text": turn.text}]}
          for turn in history
          if turn.role in ("user", "assistant")
      ]

      body = {
          "messages": messages,
          "system": [{"text": system_prompt}],
          "inferenceConfig": {"maxTokens": 500, "temperature": 0.3},
      }

      response = self.client.invoke_model(
          modelId=self.model_id,
          body=json.dumps(body),
      )
      result = json.loads(response["body"].read())
      return result["output"]["message"]["content"][0]["text"]


if __name__ == "__main__":
  from conversation_engine import ConversationEngine

  SYSTEM_PROMPT = (
      "You are a requirements clarification assistant. Ask exactly ONE "
      "short, specific question at a time to uncover actors, business "
      "rules, entities, constraints, dependencies, edge cases, and goals "
      "for the system the user describes. Never assume an answer the "
      "user hasn't given."
  )

  TEST_SCENARIO = (
      "Sistema para gestionar estudiantes: permite registrar estudiantes, "
      "inscribirlos en cursos, y ver su historial de calificaciones."
  )

  engine = ConversationEngine(BedrockLLMClient(), system_prompt=SYSTEM_PROMPT)
  first_question = engine.start(TEST_SCENARIO)
  print("Assistant:", first_question.text)
