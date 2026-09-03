# Implementation Plan: Product-Market Analysis Core

**Branch**: `feat/2-product-market-analysis`
**Date**: 2026-09-04
**Spec**: [spec.md](spec.md)

## Scope and constraints

The frozen design and reviewed RED tests now proceed to GREEN under constitution
1.2.0. Use the existing Python 3.12+ toolchain, pytest/pytest-asyncio, and
standard-library core code; add no dependencies, HTTP surface, frontend work,
provider SDK, or live API requirement.

## Layer responsibilities

| Layer | Responsibility |
| --- | --- |
| Domain | Immutable `MarketContext`, `RecommendationLevel`, and `ProductMarketAnalysis` values and validation. |
| Application | Evolve the owned `LLMPort`, define application failures, and orchestrate the one use case. |
| Infrastructure | Eventually translate provider mechanics and failures; provide the deterministic mock. |
| Bootstrap | Wire the use case with the existing LLMPort instance. |

The existing `Product` is reused unchanged. Domain and Application must remain
free of SDK, HTTP, FastAPI, JSON/filesystem mechanics, and provider-specific
controls. The frozen flow and exact signatures belong in [spec.md](spec.md),
not duplicated here.

## Port and failure evolution

- Retain `LLMPort.status() -> ProviderStatus`.
- Add only `analyze_product_market(product, market)` with the business-owned
  types defined by the spec.
- Keep `LLMError`, `LLMUnavailable`, and `InvalidLLMResponse` application-owned.
- The use case forwards the exact product/context objects once and propagates
  failures unchanged; it does not retry, wrap, rank, enrich, or fall back.
- `MockLLMAdapter` implements both methods deterministically and
  without keys or third-party availability.

## Planned locations

Production locations:

- `apps/api/src/liuliangchuhai/domain/market_analysis.py`
- `apps/api/src/liuliangchuhai/application/ports/llm.py` and
  `apps/api/src/liuliangchuhai/application/ports/llm_errors.py`
- `apps/api/src/liuliangchuhai/application/use_cases/analyze_product.py`
- `apps/api/src/liuliangchuhai/infrastructure/llm/mock.py`
- `apps/api/src/liuliangchuhai/bootstrap/container.py`

The approved focused tests live under `apps/api/` in:

- `tests/unit/test_market_context.py`
- `tests/unit/test_product_market_analysis.py`
- `tests/unit/test_analyze_product.py`
- `tests/contract/test_llm_analysis_port.py`
- `tests/contract/test_analysis_architecture.py`

Tests use local fakes and exact object forwarding; they do not simulate vendor
SDK details. The existing import-policy and import-linter checks remain the
architecture evidence.

## Execution and verification order

1. Freeze the contract in `spec.md` and align the active-spec pointer.
2. Add the five focused RED test files without stubs, skips, or xfails.
3. Record the focused RED failures before production implementation (completed).
4. In the explicitly authorized GREEN turn, align the constitution boundary,
   implement domain/application/infrastructure/bootstrap in dependency order,
   verify composition with a test before wiring, then run the focused suite,
   review narrowly for refactoring, and run architecture check and `make check`.

No real provider, API, frontend, or digital-human behavior is part of this plan.
