# ADR-0001: Pragmatic Hexagonal Architecture

- **Status:** Accepted
- **Date:** 2026-09-04

## Context

The repository must support rapidly added AI and digital-human integrations without coupling core behavior to SDKs or breaking a key-free demo. The codebase is new and the Phase 1 domain is intentionally unspecified, so a full enterprise Clean Architecture would create speculative abstractions.

## Decision

Use five explicit backend layers: `domain`, `application`, `infrastructure`, `presentation`, and `bootstrap`. The architectural rule is: dependencies never point outward within the core.

```text
presentation ─┐
infrastructure ├──> application ──> domain
bootstrap ─────┘       ↑
       └── wires concrete adapters to ports
```

### Dependency rule and responsibilities

- **Domain:** framework-independent business concepts and invariants; none are invented in Phase 0.
- **Application:** use cases, neutral DTOs, and application-owned ports. It may import domain, never outer layers.
- **Infrastructure:** concrete implementations of application ports and external-system mapping. It contains no business decisions.
- **Presentation:** FastAPI schemas/routes, validation, DTO mapping, and use-case invocation only.
- **Bootstrap:** settings, provider selection, object construction, and FastAPI application factory. As the composition root, it may depend on all layers.

External capabilities require ports before adapters. Ports use small `Protocol` contracts rather than a DI framework or inheritance hierarchy.

## Rationale

- **Ports/adapters:** provider SDK and availability changes remain outside the core; shared contract tests demonstrate interchangeability.
- **Not full enterprise Clean Architecture:** no CQRS, repositories, transactions, DI container, database, or domain hierarchy exists without a Phase 0 requirement.
- **Mock-first integrations:** deterministic mocks make development, CI, and the demo credential-free; real provider failures do not block the supported mock path.
- **OpenAPI-generated TypeScript:** Pydantic HTTP schemas remain the one public-contract source; generation removes hand-copied frontend types and enables drift checks.
- **Python task runner with thin Makefile:** `pathlib`, `shutil`, and `subprocess` provide one implementation for macOS, Linux, and Windows; Make is only an ergonomic alias.

## Consequences

- More directories exist than in a flat FastAPI app, but each boundary has an executable reason.
- Provider changes require an infrastructure adapter, bootstrap registration, and contract-test case, not core or HTTP changes.
- Public API changes require specification and regenerated OpenAPI/TypeScript artifacts.
- Architecture tooling and generated files add small maintenance cost to prevent silent dependency and contract erosion.
- The domain remains deliberately empty until Phase 1 defines real business concepts.

## Rejected Alternatives

- **Flat router/service modules:** fastest initially, but gives no enforceable seam between use cases and providers.
- **Full DDD/CQRS/repository stack:** speculative and disproportionate without domain or persistence requirements.
- **FastAPI `Depends` throughout application code:** leaks the presentation framework into the core.
- **Manual TypeScript interfaces:** creates a second public-contract source and undetectable drift.
- **Shell-based task scripts:** not equivalent on Windows and encourage OS-specific file operations.
- **Database, Redis, queues, Docker, or real provider SDKs:** not required for Phase 0 and harmful to key-free reliability.
