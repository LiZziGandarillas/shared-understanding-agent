"""
Run a REAL clarification session against Bedrock — the user answers
live via terminal input, and the result is saved as
demo/requirements_with_agent.md (the "with agent" side of the
before/after protocol).

Run from the repo root:
    python src/run_real_session.py

Requires:
- AWS credentials configured (aws configure)
- Bedrock quota not currently throttling (see test_bedrock_connection.py)
"""
from pathlib import Path

from bedrock_llm_client import BedrockLLMClient
from bedrock_extractor import BedrockExtractor
from orchestrator import run_clarification_session
from requirements_generator import generate_requirements_md
from prompts import TEST_SCENARIO

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "demo" / "requirements_with_agent.md"


def interactive_answer_provider(category: str, question: str) -> str:
  print(f"\n[{category}] {question}")
  return input("> ").strip()


def main() -> None:
  print("Starting clarification session (Bedrock, live).")
  print(f"Initial statement: {TEST_SCENARIO}\n")

  model, decision_log, history = run_clarification_session(
    TEST_SCENARIO,
    get_answer=interactive_answer_provider,
    extractor=BedrockExtractor(),
    llm_client=BedrockLLMClient(),
  )

  requirements_md = generate_requirements_md(model)
  OUTPUT_PATH.write_text(requirements_md, encoding="utf-8")

  print(f"\nSaved: {OUTPUT_PATH}")
  print(f"Decisions recorded: {len(decision_log.decisions)}")
  print("\n=== Coverage summary ===")
  for category, info in model.coverage_summary().items():
    print(f"  {category}: {info}")


if __name__ == "__main__":
  main()
