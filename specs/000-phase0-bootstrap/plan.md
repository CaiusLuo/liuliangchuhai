# Implementation Plan: Phase 0 Repository Bootstrap

**Branch**: `000-phase0-bootstrap` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

## Summary

Bootstrap a minimal FastAPI/Next.js monorepo using a pragmatic hexagonal backend. Define application-owned provider ports, deterministic infrastructure mocks, a bootstrap composition root, a health/provider-status HTTP surface, generated TypeScript contracts, executable architecture boundaries, and one portable Python task runner.

## Technical Context

**Language/Version**: Python 3.12+; TypeScript 5; Node.js 22+

**Primary Dependencies**: FastAPI, Pydantic Settings, Uvicorn; Next.js, React, openapi-typescript

**Storage**: N/A

**Testing**: pytest, pytest-asyncio, HTTPX/ASGI transport, import-linter; frontend lint and TypeScript compiler

**Target Platform**: macOS, Linux, and Windows development; Linux GitHub Actions

**Project Type**: Full-stack web application monorepo

**Performance Goals**: N/A for Phase 0; health/status behavior must remain local and deterministic

**Constraints**: no external credentials, no database, no Phase 1 business behavior, no Unix-only task implementation, non-mutating quality gate

**Scale/Scope**: one API, one minimal web shell, two provider contracts, mock adapters only

## Constitution Check

The plan satisfies the constitution: contracts and tests precede implementation, core boundaries are linted, ports precede adapters, mocks are the default, OpenAPI owns frontend contracts, presentation stays thin, and the task runner is cross-platform. The RED-to-GREEN order is recorded in `tasks.md`.

## Project Structure

```text
apps/
├── api/
│   ├── pyproject.toml
│   ├── src/liuliangchuhai/
│   │   ├── domain/
│   │   ├── application/{ports,use_cases}/
│   │   ├── infrastructure/{llm,digital_human}/
│   │   ├── presentation/http/
│   │   └── bootstrap/
│   └── tests/{unit,contract,integration,acceptance}/
└── web/
    ├── package.json
    └── src/{app,features,components,api/generated}/
scripts/dev.py
specs/000-phase0-bootstrap/
docs/ARCHITECTURE.md
.specify/
```

**Structure Decision**: The five backend layer names directly encode allowed dependency directions. Only directories used by current Phase 0 files will be created; empty Phase 1 packages are avoided except `domain`, whose marker documents the inward boundary.

## Design Decisions

- Use `typing.Protocol` for small async ports; no DI framework or abstract base hierarchy.
- Port methods expose neutral dataclasses. Mock outputs identify provider availability but contain no prompts or business decisions.
- A single provider-status use case proves injection and delegates to both ports.
- Pydantic Settings reads prefixed environment values; bootstrap factories use explicit dictionaries/matches and reject unknown providers.
- Generate `openapi.json` by importing the app factory in a Python subprocess.
- Generate schema types with `openapi-typescript`; the task runner prepends a stable warning banner.
- Drift checks generate into a temporary directory and compare bytes, never mutate source artifacts.
- Use `mypy` for backend static types and `import-linter` for layer contracts.

## RED-to-GREEN Verification

1. Create architecture, port-contract, settings/container, app-boot, schema-generation, and acceptance tests before source modules.
2. Run each suite and record failure due to missing modules/contracts.
3. Implement the smallest source skeleton that satisfies those tests.
4. Add frontend shell/config and generation only after backend OpenAPI exists.
5. Refactor duplication, search for forbidden concepts, then run the full quality gate.

## Complexity Tracking

No constitution violations are required. The provider-status use case is retained solely to exercise the port and composition seams end to end.
