# liuliangchuhai Constitution

## Core Principles

### I. Contract First

Cross-module behavior MUST have an explicit contract before implementation. Public contract changes MUST update the owning specification and generated artifacts; they MUST NOT be introduced silently.

### II. Core Independence

`domain` and `application` form the core. `domain` MUST NOT depend on application, infrastructure, presentation, bootstrap, FastAPI, database drivers, external AI or digital-human SDKs, filesystem implementations, or concrete network clients. `application` MAY depend on domain and standard-library abstractions, but MUST NOT depend on infrastructure, presentation, bootstrap, or concrete external clients.

### III. Ports Before Adapters

Every external capability used by application behavior MUST first be expressed as an application-owned port. Concrete provider, persistence, and network implementations belong in infrastructure. Bootstrap is the only composition root that selects concrete adapters.

### IV. Test First (NON-NEGOTIABLE)

Application behavior follows RED -> GREEN -> REFACTOR. A focused failing test or executable architecture check MUST exist before its implementation. Tests MUST remain independent of live third-party systems unless explicitly marked as optional external verification.

### V. Mockable External Systems

Every external dependency in the main development/demo path MUST have a deterministic mock or fake. Development, tests, and the demo MUST remain runnable without API keys or third-party availability.

### VI. Stable API Contracts

FastAPI Pydantic HTTP schemas and their OpenAPI document are the backend public-contract source of truth. The frontend MUST consume generated TypeScript contracts/client code and MUST NOT manually redefine backend response types. Generated files MUST NOT be edited by hand.

### VII. Thin Presentation

HTTP routers MAY validate requests, map DTOs, invoke use cases, and map responses; they MUST NOT contain business rules. React components MUST NOT contain backend business logic, provider prompts, or duplicated public contracts.

### VIII. Architecture Enforcement

Dependency boundaries MUST be enforced by executable checks. A violation MUST fail `architecture-check` and the repository quality gate.

### IX. Cross-platform Development

macOS, Linux, and Windows MUST share the Python task implementation in `scripts/dev.py`. Make MAY provide aliases only and MUST NOT contain OS-dependent task logic. Task paths and file operations MUST use portable Python APIs.

### X. Demo Reliability

Mock providers are the default. Configuration MAY select a real adapter, but missing or failed third-party integration MUST NOT prevent the mock-based development/demo path from running.

## Phase Boundaries

Phase 0 is limited to architecture, contracts, dependency boundaries, development workflow, tests, provider extension points, health/status wiring, and OpenAPI-to-TypeScript generation. Product selection, market analysis, recommendations, shopping assistants, prompts, RAG, databases, scraping, payment, orders, logistics, inventory, queues, and real digital-human generation are explicitly deferred.

New top-level directories require an architectural reason. New dependencies and abstractions require a current requirement and test. Prefer the smallest design that satisfies this constitution.

Phase 0 is complete. The first Phase 1 increment is governed by
`specs/001-product-foundation/spec.md` (issue #1): a canonical Product, an
application repository port, a curated read-only JSON adapter, demo data, and
read-only application use cases. This limited local catalog is now permitted;
all other deferred capabilities remain outside this increment. The amendment
enables the requested shared product foundation without weakening dependency,
testing, mockability, or generated-contract rules.

The next Phase 1 increment, `specs/002-product-market-analysis/spec.md` (issue #2),
is authorized for implementation: validated market context and analysis values,
an application-owned LLM analysis capability and failure contracts, a thin use
case, deterministic mock behavior, and bootstrap wiring. This enables the frozen
product-market analysis core only; real providers, HTTP/frontend surfaces, and
all other deferred capabilities remain out of scope. Existing architecture and
testing rules are unchanged.

The next Phase 1 increment, `specs/003-product-analysis-api/spec.md` (issue #3),
is authorized for implementation after review of its frozen SPEC and RED tests:
compose the existing product lookup and analysis use cases, expose the frozen
POST /product-analysis request/response/error contract through thin Presentation
schemas and mappers, wire it in bootstrap, and regenerate OpenAPI/TypeScript.
This makes the existing mock analysis available over HTTP; frontend features,
real providers, Issue #4, and other deferred capabilities remain out of scope.
Existing core contracts, architecture gates, and testing rules are unchanged.

## Development Workflow and Quality Gate

Work MUST follow specification -> plan -> tasks -> RED -> GREEN -> REFACTOR -> verification. Before declaring work complete, run `make check` or, on Windows, `uv run python scripts/dev.py check`. The gate MUST check formatting without mutation, linting, type safety, architecture boundaries, unit/contract/integration/acceptance tests, frontend lint/typecheck, and generated OpenAPI/client drift.

## Governance

This constitution supersedes informal conventions. Amendments require an explicit specification change, rationale, version update, and review of affected tests, architecture rules, generated contracts, and agent guidance. Reviewers MUST reject untested boundary changes, hidden contract changes, and unjustified complexity.

**Version**: 1.3.0 | **Ratified**: 2026-09-04 | **Last Amended**: 2026-09-04
