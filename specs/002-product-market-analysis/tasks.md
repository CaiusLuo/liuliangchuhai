# Tasks: Product-Market Analysis Core

**Input**: [spec.md](spec.md) and [plan.md](plan.md)
**Scope**: Documentation cleanup plus SPEC -> RED evidence, then stop.

## Completed specification and RED work

- [x] Freeze Issue #2's user scenario, flow, contracts, validation, failures,
  architecture boundaries, acceptance criteria, and out-of-scope items in
  `spec.md`.
- [x] Record layer ownership, port evolution, deterministic mock strategy,
  failure semantics, file locations, and TDD order in `plan.md`.
- [x] Add RED tests for MarketContext, ProductMarketAnalysis, use-case
  forwarding/failures, the LLM port/mock contract, and architecture assumptions.
- [x] Run the focused RED suite and preserve the evidence below.
- [x] Consolidate the documentation into `spec.md`, `plan.md`, and `tasks.md`;
  remove redundant generated research, quickstart, data-model, and checklist
  documents. Keep the active-spec pointer unchanged.

## RED evidence

Command executed from the repository root:

```sh
UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache uv run --project apps/api pytest apps/api/tests/unit/test_market_context.py apps/api/tests/unit/test_product_market_analysis.py apps/api/tests/unit/test_analyze_product.py apps/api/tests/contract/test_llm_analysis_port.py apps/api/tests/contract/test_analysis_architecture.py --continue-on-collection-errors -q
```

Exit code **1**: **3 failed, 2 passed, 3 errors in 0.05s**.

- Collection fails because `domain.market_analysis` and
  `application.ports.llm_errors` are intentionally absent.
- The use-case module and `analyze_product_market` capability are intentionally
  unimplemented on the existing port/mock.
- Architecture assumption checks pass against the unchanged core.
- No tests were skipped or xfailed; no stubs or production implementation were
  added. Focused Ruff format/lint checks passed before the RED run.

## Future GREEN, REFACTOR, and release evidence

- [ ] Align the constitution Phase 1 boundary and active guidance before GREEN.
- [ ] Implement the frozen domain values and application-owned errors/port.
- [ ] Implement the thin use case and deterministic mock, then wire bootstrap.
- [ ] Run the focused suite to GREEN.
- [ ] Review duplication and boundaries; run `make architecture-check`.
- [ ] Run `make check` (or `uv run python scripts/dev.py check`).
- [ ] Perform final PR review and verify no real provider/API/frontend scope was
  introduced.

GREEN work is not authorized by this turn; the RED stop remains in force.
