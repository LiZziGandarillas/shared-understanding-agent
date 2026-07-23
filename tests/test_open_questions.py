from shared_understanding_model import SharedUnderstandingModel, Actor
from open_questions import compute_open_questions, is_fully_covered


def test_empty_model_has_one_open_question_per_category():
  model = SharedUnderstandingModel()
  questions = compute_open_questions(model)
  assert len(questions) == 7
  assert not is_fully_covered(model)


def test_open_questions_shrink_as_categories_fill():
  model = SharedUnderstandingModel()
  model.actors.extend([Actor(name="A", role="a"), Actor(name="B", role="b")])
  questions = compute_open_questions(model)
  categories_still_open = {q.category for q in questions}
  assert "actors" not in categories_still_open
  assert len(questions) == 6


def test_missing_count_is_accurate():
  model = SharedUnderstandingModel()
  model.actors.append(Actor(name="A", role="a"))
  questions = compute_open_questions(model)
  actors_question = next(q for q in questions if q.category == "actors")
  assert actors_question.missing_count == 1
