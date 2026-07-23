from orchestrator import run_clarification_session, MockExtractor


def test_full_session_covers_every_category_with_mock_extractor():
  canned_answers = {
    "actors": ["Administrator", "Student"],
    "business_rules": ["Rule one", "Rule two", "Rule three"],
    "entities": ["Course", "Enrollment"],
    "constraints": ["Some constraint"],
    "dependencies": ["No external dependency"],
    "edge_cases": ["Edge case one", "Edge case two"],
    "goals": ["Some goal"],
  }

  def answer_provider(category: str, question: str) -> str:
    remaining = canned_answers.get(category, [])
    return remaining.pop(0) if remaining else ""

  model, log, history = run_clarification_session(
    "Some initial statement", answer_provider, MockExtractor()
  )

  for category in ["actors", "business_rules", "entities", "constraints",
                    "dependencies", "edge_cases", "goals"]:
    assert model.is_covered(category), f"{category} was not covered"


def test_answers_land_in_the_category_that_was_actually_asked():
  """Regression test for the category-desync bug: when Clarification
  Engine reorders which category it asks about turn to turn, the answer
  must be recorded against THAT category — not whatever category a
  fixed-order answer list assumed would be asked next."""
  received_categories: list[str] = []

  canned_answers = {
    "actors": ["Administrator", "Student"],
    "business_rules": ["Rule one", "Rule two", "Rule three"],
    "entities": ["Course", "Enrollment"],
    "constraints": ["Some constraint"],
    "dependencies": ["No external dependency"],
    "edge_cases": ["Edge case one", "Edge case two"],
    "goals": ["Some goal"],
  }

  def answer_provider(category: str, question: str) -> str:
    received_categories.append(category)
    remaining = canned_answers.get(category, [])
    return remaining.pop(0) if remaining else ""

  model, log, history = run_clarification_session(
    "Some initial statement", answer_provider, MockExtractor()
  )

  assert received_categories[0] == "business_rules"

  business_rule_texts = {br.rule for br in model.business_rules}
  assert business_rule_texts == {"Rule one", "Rule two", "Rule three"}


def test_conversation_history_alternates_assistant_and_user_turns():
  def answer_provider(category: str, question: str) -> str:
    return "some answer"

  model, log, history = run_clarification_session(
    "Initial statement", answer_provider, MockExtractor(), max_turns=3
  )

  assert history[0].role == "user"
  assert history[0].text == "Initial statement"
  for i in range(1, len(history) - 1, 2):
    assert history[i].role == "assistant"
    assert history[i + 1].role == "user"
