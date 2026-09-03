# liuliangchuhai

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

See [AGENTS.md](AGENTS.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and [the Phase 0 specification](specs/000-phase0-bootstrap/spec.md) for project rules and scope.
