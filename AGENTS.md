# Agent Guide

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

## Engineering rules

- Preserve public, domain, and application contracts unless the Issue explicitly changes them. Update generated API contracts from FastAPI OpenAPI; never edit `apps/web/src/api/generated/` by hand.
- Keep routers to validation, mapping, use-case invocation, and response mapping. Keep React components free of backend business rules and provider prompts.
- Give every external dependency in the main path a deterministic mock or fake. Keep development, tests, and the demo runnable without third-party availability.
- Add focused automated coverage for changed behavior and retain executable architecture checks. Run `make check`, or on Windows `uv run python scripts/dev.py check`, before requesting review.
- Do not add dependencies, top-level directories, or abstractions without a current requirement.

## Documentation and contribution

- Documentation must be proportional to implementation complexity. Ordinary Issue-scoped work follows: GitHub Issue → implementation and tests → PR.
- Do not create `spec.md`, `plan.md`, or `tasks.md` by default. Create a compact specification only for a durable public, domain, application, or cross-module contract that code, tests, and generated contracts cannot adequately express.
- Coding prompts are transient and must not be committed as project documentation.
- Contributors link the Issue, report only checks actually run, and do not self-merge upstream pull requests. Maintainers make merge decisions.
