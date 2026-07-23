from shared_understanding_model import (
  SharedUnderstandingModel,
  Actor,
  BusinessRule,
  Entity,
  Constraint,
  Dependency,
  EdgeCase,
  Goal,
  THRESHOLDS,
)


def test_empty_model_is_not_covered_anywhere():
  model = SharedUnderstandingModel()
  for category in THRESHOLDS:
    assert not model.is_covered(category)


def test_is_covered_true_once_threshold_reached():
  model = SharedUnderstandingModel()
  model.actors.append(Actor(name="Admin", role="administrator"))
  model.actors.append(Actor(name="Student", role="student"))
  assert model.is_covered("actors")


def test_least_covered_category_picks_largest_gap():
  model = SharedUnderstandingModel()
  model.actors.append(Actor(name="Admin", role="administrator"))
  assert model.least_covered_category() == "business_rules"


def test_least_covered_category_none_when_fully_covered():
  model = SharedUnderstandingModel()
  model.actors.extend([Actor(name="A", role="a"), Actor(name="B", role="b")])
  model.business_rules.extend([BusinessRule(rule=f"rule {i}", source_turn=0) for i in range(3)])
  model.entities.extend([Entity(name=f"E{i}") for i in range(2)])
  model.constraints.append(Constraint(constraint="c"))
  model.dependencies.append(Dependency(system="s"))
  model.edge_cases.extend([EdgeCase(scenario=f"ec{i}") for i in range(2)])
  model.goals.append(Goal(goal="g"))

  assert model.least_covered_category() is None


def test_save_and_load_roundtrip(tmp_path):
  model = SharedUnderstandingModel()
  model.actors.append(Actor(name="Admin", role="administrator", permissions=["manage"]))
  path = tmp_path / "model.json"

  model.save(path)
  loaded = SharedUnderstandingModel.load(path)

  assert loaded.actors == model.actors
