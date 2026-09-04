# liuliangchuhai

FastAPI and Next.js application with a small, layered backend and generated API contracts.

## Development

macOS/Linux:

```sh
make bootstrap
make dev
make check
```

Windows or without Make:

```sh
uv run python scripts/dev.py bootstrap
uv run python scripts/dev.py dev
uv run python scripts/dev.py check
```

FastAPI/Pydantic schemas produce the committed OpenAPI document and the generated
TypeScript client in `apps/web/src/api/generated/`; do not edit generated files by hand.
See [architecture](docs/ARCHITECTURE.md), [contributing](CONTRIBUTING.md), and
[repository guidance](AGENTS.md).

## Demo

Run `make bootstrap` once, then `make dev` (or use the equivalent Python commands
above). Open `http://localhost:3000`. Key routes: `/`, `/products`,
`/products/[productId]`, and `/analysis`.

Smoke path: Browse products → open a product → Analyze market fit → confirm the
preselected product → enter an ASEAN country → Analyze product → Generate content
plan. The completed report includes market analysis and all six content-plan fields.
Direct `/analysis` starts with an empty selector; unknown `product_id` values do too.
Deterministic mock providers are the default demo path; no third-party credentials
are required.
