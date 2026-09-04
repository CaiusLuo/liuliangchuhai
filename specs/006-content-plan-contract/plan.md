# Implementation Plan: Content Plan Contract

**Branch**: `feat/6-content-plan-contract` | **Date**: 2026-09-04
**Spec**: [spec.md](spec.md) | **Phase**: SPEC + PLAN + RED only

## Summary and technical context

Define the frozen materials boundary using Python 3.12+, stdlib dataclasses and
Protocol, existing pytest/pytest-asyncio, and local fakes. No new dependencies,
storage, APIs, or runtime implementation this turn. US1 supplies the boundary;
US2 supplies a deterministic offline adapter later.

## Constitution check

Contract-first and RED precede implementation. Domain/Application stay inward;
Bootstrap remains the sole composition root. Existing import-linter and
scripts/check_core_imports.py already cover outer layers and third-party core
imports, so no duplicate global bans or weakened checks are needed. The port
signature test adds the narrow provider-neutral business-boundary expectation.

Constitution 1.2.0 production authorization ends at #2. Defer shared governance
changes until future GREEN/rebase; do not change the active Issue #3 pointer.
This design check permits documentation and tests only, not production GREEN.

## Placement (future production only)

All paths below are under `apps/api/src/liuliangchuhai/`:

| Path | Responsibility |
| --- | --- |
| domain/content_plan.py | Frozen Context/Plan values and ValueError validation |
| application/ports/content_planner.py | Business capability Protocol |
| application/use_cases/create_content_plan.py | Single await and exact forwarding |
| infrastructure/content/mock.py | Deterministic, clearly labeled demo materials |
| bootstrap/container.py | Later explicit adapter selection/injection if needed |

Core may use Domain and stdlib; no SDKs or concrete clients. The use case receives
only the content planner. A provider implementing multiple ports is not an
Application concern. No LLMPort/DigitalHumanPort changes or new error hierarchy.
Keep Product, MarketContext, and ProductMarketAnalysis unchanged.

## Test strategy

All test paths below are under `apps/api/tests/`:

- `unit/test_content_plan.py`: valid exact shape; invalid language, selling
  points and each scalar; immutable values. Avoid dataclass implementation trivia.
- `contract/test_content_planner_port.py`: async parameter names and resolved
  Domain annotations; no provider-shaped options or inherited LLM requirement.
- `unit/test_create_content_plan.py`: local typed spy verifies four exact inputs,
  one invocation, exact result across recommendation levels and score bounds.
- `contract/test_mock_content_planner.py`: valid demo output, equality across
  repeated/fresh instances, socket/DNS and random/clock import guards, no ranking.

Use existing Issue #1 products fixture only; keep analysis/context/result fixtures
local to new files. Do not depend on parallel Issue #3 fixtures or change shared
conftest.py. Separate imports expose missing Domain, port, use case, and adapter.

## TDD order and verification

1. SPEC: freeze values, capability, delegation and downstream boundary in spec.md.
2. PLAN: review placement here; sequence work in tasks.md.
3. RED: add focused tests, format/lint only these files, execute focused suite
   with --continue-on-collection-errors, and record exact failures in tasks.md.
   Run baseline tests separately and run make check; distinguish pre-existing #3
   RED from #6 RED. Do not alter production to make checks pass.
4. STOP this turn. No stubs, skips, xfails, implementation, commits, push, or PR.
5. Future GREEN after authorization: Domain -> port/use case -> mock; consider
   minimal bootstrap wiring after reconciling latest main and governance.
6. REFACTOR with passing focused tests; run architecture-check then make check,
   rebase latest main, rerun gates, and verify the PR scope when authorized.

Only spec.md, plan.md, tasks.md: no research.md, data-model.md, quickstart.md,
checklist, generated artifact, or shared feature-pointer update is delivered.
