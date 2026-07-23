from shared_understanding_model import SharedUnderstandingModel, BusinessRule
from clarification_engine import ClarificationEngine


def test_empty_model_asks_about_least_covered_category():
  model = SharedUnderstandingModel()
  engine = ClarificationEngine(model)
  result = engine.next_question()

  assert result.covered is False
  assert result.category == "business_rules"
  assert result.question is not None


def test_returns_covered_when_all_thresholds_met():
  from shared_understanding_model import Actor, Entity, Constraint, Dependency, EdgeCase, Goal

  model = SharedUnderstandingModel()
  model.actors.extend([Actor(name="A", role="a"), Actor(name="B", role="b")])
  model.business_rules.extend([BusinessRule(rule=f"r{i}", source_turn=0) for i in range(3)])
  model.entities.extend([Entity(name=f"E{i}") for i in range(2)])
  model.constraints.append(Constraint(constraint="c"))
  model.dependencies.append(Dependency(system="s"))
  model.edge_cases.extend([EdgeCase(scenario=f"ec{i}") for i in range(2)])
  model.goals.append(Goal(goal="g"))

  engine = ClarificationEngine(model)
  result = engine.next_question()

  assert result.covered is True
  assert result.category is None
  assert result.question is None
