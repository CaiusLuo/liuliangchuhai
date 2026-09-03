# liuliangchuhai

Phase 0 establishes a contract-first FastAPI/Next.js foundation with mockable provider ports. It intentionally contains no product-selection or shopping-assistant behavior.

```text
make bootstrap
make dev
make check
```

Windows uses the same Python task implementation without Make:

```text
uv run python scripts/dev.py bootstrap
uv run python scripts/dev.py dev
uv run python scripts/dev.py check
```

Architecture and scope are defined in `docs/ARCHITECTURE.md` and `specs/000-phase0-bootstrap/`.
