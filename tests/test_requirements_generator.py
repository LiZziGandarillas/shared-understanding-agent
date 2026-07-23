from shared_understanding_model import SharedUnderstandingModel, Actor, Goal, BusinessRule
from requirements_generator import generate_requirements_md, _article_for


def test_article_for_picks_an_before_vowels():
  assert _article_for("administrator") == "an"
  assert _article_for("student") == "a"


def test_empty_model_still_generates_valid_markdown_with_placeholders():
  model = SharedUnderstandingModel()
  output = generate_requirements_md(model)
  assert "# Requirements" in output
  assert "No actors captured yet" in output


def test_user_stories_use_correct_article():
  model = SharedUnderstandingModel()
  model.actors.append(Actor(name="Admin", role="administrator"))
  model.goals.append(Goal(goal="manage students"))
  output = generate_requirements_md(model)
  assert "As an **administrator**" in output


def test_open_questions_section_reflects_gaps():
  model = SharedUnderstandingModel()
  model.business_rules.append(BusinessRule(rule="a rule", source_turn=0))
  output = generate_requirements_md(model)
  assert "Missing business rule" in output
