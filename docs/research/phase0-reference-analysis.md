# Phase 0 Reference Analysis

Research date: 2026-09-04. The repository was empty and not yet a Git repository, so there are no existing implementation or package-manager constraints to preserve. The detected local tools are `uv 0.11.3`, `pnpm 10.33.0`, Node.js 24, and Git; `specify` is not installed.

## `fastapi-clean-example` (`legacy-2025`)

Reference: [legacy-2025 branch](https://github.com/ivan-borovets/fastapi-clean-example/tree/legacy-2025)

- **Useful:** its domain/application core, application-owned ports, infrastructure adapters, thin presentation controllers, and setup/composition root make dependency direction visible and testable.
- **Do not copy:** CQRS, DDD building-block proliferation, a DI framework, database/auth layers, or the full production module depth.
- **Adopt:** dependencies never point outward *within the core*. Domain is framework-independent; application orchestrates through ports; adapters and HTTP are replaceable outer layers; bootstrap alone wires concrete objects.
- **Trade-off:** five named layers add navigation overhead, but keeping each layer very small makes provider replacement and architecture enforcement clearer than a flat FastAPI package.

## `full-stack-ai-agent-template`

References: [repository](https://github.com/vstorm-co/full-stack-ai-agent-template), [AGENTS.md](https://github.com/vstorm-co/full-stack-ai-agent-template/blob/main/AGENTS.md), [CI workflow](https://github.com/vstorm-co/full-stack-ai-agent-template/blob/main/.github/workflows/ci.yml)

- **Useful:** explicit agent-facing commands and ownership rules, strict frontend/backend separation, grouped lint/type/test gates, and a pattern in which provider/config choices are resolved outside feature code.
- **Do not copy:** its generator complexity, RAG/vector stores, queues, Redis, auth, billing, observability matrix, multi-agent frameworks, and large conditional integration surface.
- **Adopt:** a short root `AGENTS.md` defines placement and forbidden dependencies; one deterministic quality gate covers both applications; third-party code stays behind ports.
- **Trade-off:** fewer selectable integrations reduce template flexibility now, but keep Phase 0 understandable and make each later provider an explicit adapter change.

## `full-stack-fastapi-template`

References: [repository](https://github.com/fastapi/full-stack-fastapi-template), [OpenAPI generator configuration](https://github.com/fastapi/full-stack-fastapi-template/blob/master/frontend/openapi-ts.config.ts), [client generation script](https://github.com/fastapi/full-stack-fastapi-template/blob/master/scripts/generate-client.sh)

- **Useful:** FastAPI/Pydantic as the OpenAPI source of truth, generated TypeScript client code, pytest and browser-test organization, and CI that treats generation as a reproducible build step.
- **Do not copy:** PostgreSQL/SQLModel, auth/email, reverse proxy, deployment/CD, or the production Docker stack. Its shell generation script is not portable enough for this repository.
- **Adopt:** emit a deterministic checked-in OpenAPI document, generate the web client from it, and fail the quality gate on generated drift. Implement orchestration in Python rather than shell.
- **Trade-off:** generated code is another committed artifact, but it eliminates manually duplicated API types and allows drift to be detected offline in review and CI.

## GitHub Spec Kit

References: [repository](https://github.com/github/spec-kit), [Agentic SDD workflow](https://github.github.com/spec-kit/reference/agentic-sdd.html), [latest release](https://github.com/github/spec-kit/releases/tag/v1.0.4)

- **Useful:** constitution-first governance and the ordered `constitution -> specify -> plan -> tasks -> analyze -> implement -> converge` workflow. Project-local templates/scripts preserve the process with the codebase.
- **Do not copy:** process ceremony beyond what this small bootstrap needs, speculative feature branches, or generated artifacts unrelated to Phase 0.
- **Adopt:** pin the official `v1.0.4` CLI for initialization, create the constitution, and retain a focused `spec.md`, `plan.md`, and `tasks.md` under `specs/000-phase0-bootstrap/`.
- **Trade-off:** committing Spec Kit support files adds maintenance surface, but gives future agents a shared, auditable path from contract to implementation.

## `fastapi-best-practices`

Reference: [repository and conventions](https://github.com/zhanymkanov/fastapi-best-practices)

- **Useful:** predictable modules, Pydantic schemas at HTTP boundaries, async-aware I/O guidance, small routers, and tests that exercise application setup without unnecessary infrastructure.
- **Do not copy:** generic “best practice” modules before a real need, sync wrappers, database-centric structure, or background-worker recommendations.
- **Adopt:** keep health handling simple, keep transport validation in presentation, avoid blocking work in async paths, and add abstractions only for required provider seams.
- **Trade-off:** the initial domain package is intentionally almost empty; this is preferable to inventing business concepts before Phase 1 requirements exist.

## Proposed Architecture

Use a single Python API package and a separate Next.js web application:

```text
apps/api/src/liuliangchuhai/
├── domain/          # future business concepts; imports no outer layer
├── application/     # ports and use cases; imports domain only
├── infrastructure/  # provider adapters; implements application ports
├── presentation/    # FastAPI routers and HTTP schemas
└── bootstrap/       # settings, provider selection, composition, app factory

apps/web/            # Next.js shell; generated API client under src/api/generated
scripts/dev.py       # cross-platform source of truth for developer tasks
```

Phase 0 exposes small asynchronous `LLMPort` and `DigitalHumanPort` protocols plus deterministic mock adapters. A minimal application-level provider-status use case proves wiring and interchangeability without introducing product-selection or shopping behavior. FastAPI exposes only health/provider-status bootstrap endpoints. Configuration chooses adapters, and unsupported real providers fail clearly at startup while the default remains mock-only and key-free.

`import-linter` enforces core boundaries. Pytest is split into unit, contract, integration, and acceptance categories. Pydantic HTTP schemas generate `openapi.json`; `openapi-typescript` generates a checked-in TypeScript schema client with an explicit generated-file warning. The thin Makefile delegates every action to `uv run python scripts/dev.py`, which uses only Python standard-library path/process APIs for orchestration.
