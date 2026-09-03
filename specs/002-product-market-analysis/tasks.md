# Tasks: Product-Market Analysis Core

**Input**: [spec.md](spec.md) and [plan.md](plan.md)
**Scope**: Approved RED -> GREEN -> narrow REFACTOR -> full quality gate; no commit/push/PR.

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

## GREEN, REFACTOR, and verification

- [x] Align the constitution Phase 1 boundary and active guidance before GREEN.
- [x] Implement the frozen domain values and application-owned errors/port.
- [x] Implement the thin use case and deterministic mock, then wire bootstrap.
- [x] Run the focused suite to GREEN.
- [x] Review duplication and boundaries; run `make architecture-check`.
- [x] Run `make check` (or `uv run python scripts/dev.py check`).
- [x] Perform final diff review and verify no real provider/API/frontend scope was
  introduced.

GREEN is explicitly authorized. Stop after verification; do not commit, push,
open a PR, or start a later issue.

## GREEN and REFACTOR evidence

- Constitution **1.1.0 -> 1.2.0** adds only the authorized Issue #2 analysis core,
  error contracts, deterministic mock, and composition. Existing rules are intact;
  active guidance and stage wording are aligned without changing the frozen contract.
- Composition TDD: `test_analysis_reuses_the_containers_llm` first failed with
  `AttributeError: 'Container' object has no attribute 'analyze_product'`.
  It now verifies that the composed use case calls the existing LLM instance once.
- Focused GREEN command (no collection-error continuation, skips, or xfails):

  ```sh
  UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache uv run --project apps/api pytest apps/api/tests/unit/test_market_context.py apps/api/tests/unit/test_product_market_analysis.py apps/api/tests/unit/test_analyze_product.py apps/api/tests/contract/test_llm_analysis_port.py apps/api/tests/contract/test_analysis_architecture.py -q
  ```

  Exit **0**: **67 passed in 0.05s**, clean collection.
- `UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache make architecture-check`:
  exit **0**, **4 import-linter contracts kept, 0 broken**; core import policy passed.
- `UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache make check`: exit **0**,
  **All checks passed**. Formatting, lint, backend types (33 source files),
  architecture, frontend lint/types/production build, and generated OpenAPI/client
  drift passed. Tests: **115 unit + 16 contract + 4 integration + 2 acceptance = 137**.
  This includes existing Issue #1 and status behavior tests.
- Narrow REFACTOR review: one definition of each domain concept; frozen dataclasses,
  explicit validation and one local string-validation helper; one-call use case;
  no provider leakage or helper framework. Only a long mock expression needed
  formatting. Mock uses fixed `caution`/`50` demo indicators and input-derived text,
  with no randomness, time, network, or market-fit algorithm.
- Protected-file comparison confirmed Product, ProductRepository/catalog, digital
  human, HTTP/OpenAPI, frontend, dependencies, tooling and the approved RED review
  changes were preserved. `git diff --check` passed. No later-issue implementation,
  commit, push, or PR was performed. Real provider exception translation remains
  deliberately deferred; no parsing code was introduced.
