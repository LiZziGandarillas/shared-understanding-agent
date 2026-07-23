from decision_log import DecisionLog


def test_record_adds_a_decision_with_generated_id():
  log = DecisionLog()
  decision = log.record(
    category="business_rule",
    question="q",
    answer="a",
    reason="r",
    source="product_owner",
    decision_source="user_explicit",
    confidence="high",
  )
  assert len(log.decisions) == 1
  assert decision.decision_id


def test_by_category_filters_correctly():
  log = DecisionLog()
  log.record(
    category="business_rule", question="q1", answer="a1", reason="r",
    source="product_owner", decision_source="user_explicit", confidence="high",
  )
  log.record(
    category="assumption", question="q2", answer="a2", reason="r",
    source="inferred", decision_source="assumption", confidence="low",
  )
  assert len(log.by_category("business_rule")) == 1
  assert len(log.by_category("assumption")) == 1


def test_low_confidence_filters_correctly():
  log = DecisionLog()
  log.record(
    category="assumption", question="q", answer="a", reason="r",
    source="inferred", decision_source="assumption", confidence="low",
  )
  log.record(
    category="business_rule", question="q", answer="a", reason="r",
    source="product_owner", decision_source="user_explicit", confidence="high",
  )
  assert len(log.low_confidence()) == 1


def test_save_and_load_roundtrip(tmp_path):
  log = DecisionLog()
  log.record(
    category="business_rule", question="q", answer="a", reason="r",
    source="product_owner", decision_source="user_explicit", confidence="high",
  )
  path = tmp_path / "log.json"

  log.save(path)
  loaded = DecisionLog.load(path)

  assert loaded.decisions == log.decisions
