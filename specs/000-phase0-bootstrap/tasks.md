# Tasks: Phase 0 Repository Bootstrap

**Input**: [spec.md](spec.md) and [plan.md](plan.md)

## Phase A-B: Inspection and Research

- [x] T001 Inspect the repository recursively and record compatibility constraints.
- [x] T002 Research the five required reference repositories and record only durable findings in `docs/ARCHITECTURE.md`.

## Phase C-D: SDD and Architecture Decision

- [x] T003 Initialize official Spec Kit support with its detected Codex integration and portable Python scripts.
- [x] T004 Establish `.specify/memory/constitution.md`.
- [x] T005 Create `specs/000-phase0-bootstrap/spec.md` and `plan.md`.
- [x] T006 Document the architecture and accepted decisions in `docs/ARCHITECTURE.md`.

## Phase E: RED

- [x] T007 [P] Write import-boundary tests/config before backend layer modules exist.
- [x] T008 [P] Write shared LLM and digital-human adapter contract tests before ports/adapters exist.
- [x] T009 [P] Write provider-selection/container unit tests before bootstrap implementation exists.
- [x] T010 [P] Write FastAPI boot, health, wiring, and OpenAPI integration tests before the app exists.
- [x] T011 Write mock-only acceptance smoke test before runnable entrypoints exist.
- [x] T012 Run the new tests and record the expected missing-module/configuration failures.

## Phase F: GREEN

- [x] T013 Create backend packaging/tool configuration in `apps/api/pyproject.toml` and import-linter contracts.
- [x] T014 Implement application-owned ports and neutral DTOs under `apps/api/src/liuliangchuhai/application/ports/`.
- [x] T015 Implement the minimal provider-status use case under `application/use_cases/`.
- [x] T016 Implement deterministic mock adapters under `infrastructure/llm/` and `infrastructure/digital_human/`.
- [x] T017 Implement settings, provider selection, composition, and app factory under `bootstrap/`.
- [x] T018 Implement thin health/status HTTP schemas and router under `presentation/http/`.
- [x] T019 Run backend unit, contract, integration, and acceptance suites to GREEN.
- [x] T020 Create the minimal Next.js TypeScript shell with no Phase 1 UI.
- [x] T021 Generate deterministic `openapi.json` and TypeScript contracts under `apps/web/src/api/generated/`.
- [x] T022 Implement portable commands in `scripts/dev.py` and thin aliases in `Makefile`.
- [x] T023 Add minimal GitHub Actions CI that invokes the Python quality gate.

## Phase G: REFACTOR

- [x] T024 Remove unjustified abstractions and duplicated configuration/contract definitions.
- [x] T025 Search source and UI for forbidden Phase 1 concepts and unnecessary stack dependencies.
- [x] T026 Verify AGENTS and architecture documents match executable boundaries and commands.

## Phase H: VERIFY

- [x] T027 Run format, lint, typecheck, architecture-check, each backend test category, frontend lint/typecheck, and generation drift checks separately.
- [x] T028 Run `make check` and capture its exact output.
- [x] T029 Capture final directory tree, `git diff --stat`, remaining risks, and manually important files.

## TDD Evidence

- **RED:** `pytest apps/api/tests -q` failed during collection with seven expected errors because FastAPI and every `liuliangchuhai` target module were still absent.
- **GREEN:** after the minimal source skeleton was added, all 11 tests passed: 5 unit, 3 contract, 2 integration, and 1 acceptance.

## Dependencies

T001 -> T002 -> T003-T006 -> T007-T012 (RED) -> T013-T023 (GREEN) -> T024-T026 (REFACTOR) -> T027-T029 (VERIFY). Tests in T007-T011 target separate files and may be authored independently, but implementation MUST NOT begin until T012 records the RED result.
