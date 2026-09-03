# Architecture

## Goals

The completed Phase 0 foundation accommodates future AI and digital-human integrations while keeping implementations replaceable and the development/demo path reliable without credentials or third-party availability. The current increment adds only the read-only product foundation defined in [specs/001-product-foundation](../specs/001-product-foundation/spec.md).

## Dependency Model

```text
domain
  ↑
application
  ↑
infrastructure / presentation
  ↑
bootstrap
```

The core is `domain` plus `application`; dependencies point inward. `domain` is framework-independent and imports no outer layer. `application` may import `domain`, but not infrastructure, presentation, bootstrap, or concrete external clients. `import-linter` enforces these core boundaries.

The outer layers are replaceable. Infrastructure implements application capabilities, presentation translates HTTP requests and responses, and bootstrap is the composition root that constructs objects and selects implementations. Provider SDKs, network clients, and persistence implementations stay in infrastructure.

## Layer Responsibilities

- **domain** — canonical `Product` values and invariants, independent of frameworks and storage.
- **application** — use cases, neutral DTOs, and ports for external capabilities.
- **infrastructure** — concrete provider adapters and external-system mapping; no business decisions.
- **presentation** — FastAPI schemas and routers for validation, mapping, use-case invocation, and response mapping.
- **bootstrap** — settings, provider selection, object construction, and the FastAPI application factory.

## Ports and Adapters

`LLMPort` and `DigitalHumanPort` are small asynchronous `typing.Protocol` contracts owned by `application`. Their methods expose neutral dataclasses rather than provider types. Deterministic mock adapters implement both ports for tests and the default key-free development/demo path; future real adapters can be added in infrastructure and registered in bootstrap without changing the core or HTTP contract. Shared contract tests verify interchangeability, and unsupported provider names fail clearly during composition.

The core knows capabilities, not providers:

```text
application port ← infrastructure mock adapter
                 ← infrastructure real adapter (future)
                 ← bootstrap-selected implementation
```

`ProductRepository` is an application-owned async port returning the single
immutable domain `Product` representation. `ListProducts` and `GetProduct` depend
only on that port; `GetProduct` models missing IDs with `ProductNotFound`.
`JsonProductRepository` in `infrastructure/products/` reads and validates a UTF-8
catalog once, rejecting duplicate IDs and invalid records. It then serves a
snapshot with no further I/O. Bootstrap resolves the bundled demo resource using
`importlib.resources` and shares one adapter between both use cases. A deterministic
test fake and the JSON adapter run the same repository contract suite. There is
no product HTTP surface, so OpenAPI and TypeScript artifacts are unchanged.

## API Contract

```text
FastAPI/Pydantic schemas
          ↓
       OpenAPI
          ↓
 committed openapi.json
          ↓
 generated TypeScript contracts
```

FastAPI/Pydantic schemas and the committed OpenAPI artifact are the public-contract source of truth. `apps/web/src/api/generated/` is generated from OpenAPI, committed for review, and never edited manually. The quality gate regenerates into temporary locations and compares bytes without mutating the checkout.

## Development Workflow

```text
spec → test → implementation → make check
```

Cross-module behavior is specified before implementation. Application behavior follows RED → GREEN → REFACTOR. `scripts/dev.py` is the cross-platform source of truth for bootstrap, development, checks, tests, generation, and cleanup; `Makefile` contains aliases only. The quality gate covers formatting, linting, type safety, architecture boundaries, backend test categories, frontend checks, and generated-contract drift.

## Engineering Decisions

- **Pragmatic hexagonal architecture:** five explicit layers make provider seams visible and enforceable without speculative enterprise structure.
- **No DI framework for now:** small protocols and an explicit composition root are sufficient for Phase 0.
- **Mock-first integrations:** missing or failed third-party services must not block the supported demo path.
- **Bounded Phase 1 foundation:** only the read-only curated JSON product catalog; no database, Redis, message queue, microservices, real provider SDK, product-selection behavior, shopping assistant, prompts, or RAG.
- **Portable task runner:** Python standard-library path/process APIs provide one implementation on macOS, Linux, and Windows.
- **Executable governance:** import rules, contract tests, and generation drift checks enforce the boundaries that prose alone cannot.

## References

- [ivan-borovets/fastapi-clean-example](https://github.com/ivan-borovets/fastapi-clean-example/tree/legacy-2025)
- [vstorm-co/full-stack-ai-agent-template](https://github.com/vstorm-co/full-stack-ai-agent-template)
- [fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)
- [github/spec-kit](https://github.com/github/spec-kit)
- [zhanymkanov/fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices)

The project adopts only the relevant patterns from these references; it does not copy their CQRS, DDD, database, auth, deployment, RAG, queue, or integration complexity.
