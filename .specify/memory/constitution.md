# liuliangchuhai Constitution

## Contract discipline

Public, domain, application, and cross-module contracts must have an explicit
owner and executable coverage. Public HTTP changes originate in FastAPI/Pydantic
schemas and are reflected in OpenAPI and generated TypeScript; generated files
are never edited manually.

## Core independence

`domain` imports no outer layer. `application` may depend on `domain` and
standard-library abstractions, but not on infrastructure, presentation,
bootstrap, or concrete external clients. Application owns ports and use cases;
infrastructure owns adapters; bootstrap is the only composition root.

## Testable boundaries

Changed behavior needs focused automated coverage. Dependency boundaries must
remain executable checks. External dependencies in the main path need a
deterministic mock or fake so tests and the demo work without credentials or
third-party availability.

## Thin presentation and reliable tooling

Routers validate, map, invoke use cases, and map responses; they contain no
business rules. React components contain no backend business rules or provider
prompts. `scripts/dev.py` is the cross-platform task implementation, with Make
as aliases only; the quality gate remains non-mutating and checks architecture,
tests, frontend quality, and generated-contract drift.

## Lean governance

Documentation is proportional to implementation complexity. Ordinary work uses
GitHub Issue → implementation and tests → PR; it does not require `spec.md`,
`plan.md`, or `tasks.md`. Create a compact specification only for a durable
public, domain, application, or cross-module contract that code, tests, and
generated contracts cannot adequately express. Coding prompts are transient and
must not be committed. Git history is the archive.

This constitution changes only for durable repository-wide policy. Contributors
report checks actually run; maintainers review scope, contracts, and merge
decisions.
