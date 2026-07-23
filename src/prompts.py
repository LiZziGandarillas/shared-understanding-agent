"""
Single source of truth for the Conversation Engine's system prompt.

Both orchestrator.py (mock demo) and any real Bedrock run must use this
same prompt — otherwise the mock and the real conversation are testing
two different things, which would make the before/after comparison
meaningless the same way a mismatched test scenario would.
"""

CLARIFICATION_SYSTEM_PROMPT = (
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
