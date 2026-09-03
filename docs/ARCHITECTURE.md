# Architecture

`liuliangchuhai` uses a small hexagonal backend and a separate Next.js frontend. The detailed decision is [ADR-0001](architecture/ADR-0001-pragmatic-hexagonal-architecture.md); Phase 0 scope is defined in [the specification](../specs/000-phase0-bootstrap/spec.md).

## Dependency Boundaries

```text
apps/api/src/liuliangchuhai/
├── domain            # imports no other internal layer
├── application       # may import domain; owns ports and use cases
├── infrastructure    # implements application ports
├── presentation      # maps HTTP to application calls
└── bootstrap         # composition root; may import every internal layer
```

`import-linter` enforces that domain imports no outer layer and application imports no infrastructure, presentation, or bootstrap. External SDKs, clients, and persistence implementations belong only in infrastructure. Concrete selection and lifecycle belong only in bootstrap.

## Runtime Flow

```text
HTTP request -> presentation router -> application use case -> application port
                                                        ^             |
                                                        |             v
                                              bootstrap wiring <- infrastructure adapter
```

Phase 0 has only health/provider-status behavior. Mock LLM and digital-human adapters are the defaults; configuration selects registered alternatives. No domain model, product behavior, prompt, database, RAG, or real provider call exists yet.

## Public Contract Flow

```text
Pydantic HTTP schemas -> FastAPI OpenAPI -> openapi.json
                                         -> openapi-typescript
                                         -> apps/web/src/api/generated/
```

Generated frontend contracts are committed and never edited manually. The quality gate regenerates into temporary locations and compares bytes to detect drift without mutating the checkout.

## Developer Workflow

`scripts/dev.py` is the source of truth for bootstrap, development, checking, tests, generation, and cleanup. `Makefile` contains aliases only. Run `make check` on macOS/Linux or `uv run python scripts/dev.py check` on any supported platform before declaring work complete.
