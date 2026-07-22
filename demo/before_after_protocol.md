# Before/After Protocol

This document captures the comparison between a specification produced
**directly by Kiro** (no clarification agent involved) and a specification
produced **after the Shared Understanding Agent's conversation** for the
same starting statement.

## Test Scenario

> Sistema para gestionar estudiantes: permite registrar estudiantes,
> inscribirlos en cursos, y ver su historial de calificaciones

## Method

1. The exact same initial statement was given directly to Kiro (Spec mode,
   Autopilot off) with no prior conversation. The resulting `requirements.md`
   is stored as [`requirements_without_agent.md`](./requirements_sin_agente.md).
2. The same statement will be run through the Shared Understanding Agent's
   Conversation + Clarification Engine first. The resulting synthesized
   understanding will feed the Requirements Generator, producing
   `requirements_with_agent.md`, which will also be handed to Kiro.
3. Counts below were obtained by manually reading each generated
   `requirements.md` and tallying items per Shared Understanding Model
   category (see `docs/shared_understanding_thresholds.md`), not by any
   automated scoring.

## Quantitative Comparison

| Metric | Without agent | With agent |
|---|---|---|
| Actors | 1 | — |
| Business Rules | 5 | — |
| Edge Cases | 4 | — |
| Constraints | 2 | — |
| Open Questions detected | 0 (Kiro does not surface gaps) | — |

## Qualitative Findings (Without Agent)

Reading `requirements_sin_agente.md` against our own thresholds surfaced
two gaps that a direct spec-generation flow did not catch:

- **Missing actor**: the spec only defines "administrador" as an actor.
  It never establishes whether the student interacts with the system
  directly (e.g. viewing their own grades, self-enrolling) — a
  significant product decision left implicit.
- **Missing dependency**: no external system or integration is
  considered at all (authentication, notifications, an existing LMS,
  etc.) — the "Dependencies" category is at 0/1.

These are exactly the kind of gaps the Clarification Engine is designed
to surface before specification, and they will be the first things we
check for in the "with agent" run.

## Next Step

Run the same scenario through the full agent pipeline
(Conversation Engine → Clarification Engine → Requirements Generator →
Kiro Integration), fill in the "With agent" column, and add the
qualitative example for the after case.
