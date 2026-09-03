# Implementation Plan: Product-Market Analysis Core

**Branch**: `feat/2-product-market-analysis`
**Date**: 2026-09-04
**Spec**: [spec.md](spec.md)

## Scope and constraints

This increment freezes the design and adds RED tests only. Production remains
unchanged. Use the existing Python 3.12+ toolchain, pytest/pytest-asyncio, and
standard-library core code; add no dependencies, HTTP surface, frontend work,
provider SDK, or live API requirement.

## Layer responsibilities

| Layer | Responsibility |
| --- | --- |
| Domain | Immutable `MarketContext`, `RecommendationLevel`, and `ProductMarketAnalysis` values and validation. |
| Application | Evolve the owned `LLMPort`, define application failures, and orchestrate the one use case. |
| Infrastructure | Eventually translate provider mechanics and failures; provide the deterministic mock. |
| Bootstrap | Eventually select and wire the concrete adapter; no wiring in this RED turn. |

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
- The future `MockLLMAdapter` implements both methods deterministically and
  without keys or third-party availability.

## Planned locations

Production locations are deliberately not created in this turn:

- `apps/api/src/liuliangchuhai/domain/market_analysis.py`
- `apps/api/src/liuliangchuhai/application/ports/llm.py` and
  `apps/api/src/liuliangchuhai/application/ports/llm_errors.py`
- `apps/api/src/liuliangchuhai/application/use_cases/analyze_product.py`
- `apps/api/src/liuliangchuhai/infrastructure/llm/mock.py`
- `apps/api/src/liuliangchuhai/bootstrap/container.py`

Focused RED tests live in:

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
3. Run the recorded focused RED command and stop with the expected missing
   contract failures.
4. In a later explicitly authorized GREEN turn, align the constitution boundary,
   implement domain/application/infrastructure/bootstrap in dependency order,
   then run the focused suite, architecture check, and `make check`.

No real provider, API, frontend, or digital-human behavior is part of this plan.
