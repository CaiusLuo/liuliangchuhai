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
