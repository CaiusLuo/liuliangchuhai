# Architecture

```text
domain
  ↑
application
  ↑
infrastructure / presentation
  ↑
bootstrap
```

`domain` contains framework-independent values and invariants. `application`
owns use cases and ports, and depends only inward. `infrastructure` implements
external-system adapters; `presentation` maps HTTP; `bootstrap` is the sole
composition root. Executable import checks enforce these boundaries.

External capabilities are expressed as application-owned ports. Deterministic
mock adapters support tests and the default demo path without credentials or
third-party availability.

## API contracts

```text
FastAPI/Pydantic schemas → OpenAPI → committed openapi.json → generated TypeScript
```

FastAPI/Pydantic schemas are the HTTP contract source of truth. Generated files
under `apps/web/src/api/generated/` are committed for review and must be
regenerated, never hand-edited. `scripts/dev.py` is the cross-platform task
implementation; `Makefile` provides aliases. Its quality gate verifies format,
lint, types, architecture, tests, frontend checks, and generated-contract drift.
