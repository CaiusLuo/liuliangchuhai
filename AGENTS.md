# Agent Guide

Read `.specify/memory/constitution.md` and the active spec before changing code.

Active spec: `specs/017-product-read-api/spec.md`. Issue #17 GREEN is authorized
under constitution 1.4.0 after SPEC + RED review. Implement only the frozen
read-only product HTTP increment and regenerate OpenAPI/TypeScript contracts.
Do not start Issue #5, commit, push, or create a PR.

## Architecture

```text
domain
  ↑
application
  ↑
infrastructure / presentation
  ↑
bootstrap
```

- `domain` imports no outer layer.
- `application` may import `domain`, never `infrastructure`, `presentation`, or `bootstrap`.
- Application-owned ports and use cases go in `application`; third-party adapters go in `infrastructure`.
- Concrete dependency selection and wiring belong only in `bootstrap`.

## Development rules

- Change the spec before changing a cross-module or public contract.
- Follow RED -> GREEN -> REFACTOR for application behavior.
- Give every external dependency in the main path a deterministic mock/fake.
- Keep routers to validation, mapping, use-case invocation, and response mapping.
- Keep React components free of backend rules and provider prompts.
- Do not duplicate backend response types in TypeScript; regenerate `apps/web/src/api/generated/` from FastAPI OpenAPI and never edit it manually.
- Run `make check`, or on Windows `uv run python scripts/dev.py check`, before declaring work complete.

## Forbidden

- Provider SDK imports inside `domain` or `application`.
- Silent public-contract changes.
- Phase 1 product selection, market analysis, shopping assistance, prompts, RAG, persistence, queues, or real provider behavior during Phase 0.
- Unjustified top-level directories or dependencies.
