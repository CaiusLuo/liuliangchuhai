# Agent Guide

Read `.specify/memory/constitution.md` and the active spec before changing code.

- Dependencies point inward: `domain` imports no internal outer layer; `application` may import `domain`, never `infrastructure`, `presentation`, or `bootstrap`.
- Put use cases and external-capability ports in `application`; put third-party implementations in `infrastructure`; select and wire them only in `bootstrap`.
- Keep routers to validation, mapping, use-case invocation, and response mapping. Keep React components free of backend rules and prompts.
- Define or change contracts in the spec first. Do not silently change a public contract or duplicate backend response types in TypeScript.
- Do not edit `apps/web/src/api/generated/` manually; regenerate it from FastAPI OpenAPI.
- Follow RED -> GREEN -> REFACTOR for application behavior. Every external dependency in the main path needs a deterministic mock/fake.
- Do not add Phase 1 product selection, market analysis, shopping assistant, prompts, RAG, persistence, queues, or real provider behavior during Phase 0.
- Do not create a top-level directory or dependency without current architectural justification.
- Run `make check`, or on Windows `uv run python scripts/dev.py check`, before declaring work complete.
