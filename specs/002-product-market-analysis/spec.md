# Feature Specification: Product-Market Analysis Core

**Feature Branch**: `feat/2-product-market-analysis`
**Created**: 2026-09-04
**Status**: Frozen V1 design; GREEN implemented and locally verified
**Input**: [Issue #2](https://github.com/CaiusLuo/liuliangchuhai/issues/2), dependent on #1, and the user's frozen V1 contract.

## User scenario and acceptance

An international student has a Guangxi product and a target ASEAN market. They
need structured AI-assisted decision support describing fit, strengths, risks,
and possible positioning.

The frozen flow is:

```text
Product + MarketContext
        -> AnalyzeProductUseCase
        -> LLMPort.analyze_product_market(...)
        -> ProductMarketAnalysis
```

Acceptance criteria:

1. A valid product/context pair yields every defined analysis field.
2. Missing optional context and empty result collections are accepted; supplied
   blank strings are rejected.
3. Unavailable LLMs and invalid structured responses remain distinct,
   application-owned failures; neither produces a success fallback.
4. Identical inputs produce equal valid results from repeated or fresh mock
   instances, without randomness.

## Frozen business contract

### RecommendationLevel

String enum with exactly these serializable values:

`strong_fit`, `fit`, `caution`, `not_recommended`.

### MarketContext

| Field | Type | Validation |
| --- | --- | --- |
| `country` | `str` | Required and nonblank |
| `target_audience` | `str \| None` | Default `None`; nonblank when present |
| `market_notes` | `str \| None` | Default `None`; nonblank when present |

### ProductMarketAnalysis

Reuse Issue #1's canonical `Product` without modification. The analysis is an
immutable value with these fields:

| Field | Type | Validation |
| --- | --- | --- |
| `recommendation` | `RecommendationLevel` | One of the four enum members |
| `score` | `int` | Inclusive range 0..100; booleans/floats rejected |
| `summary` | `str` | Required and nonblank |
| `target_audiences` | `tuple[str, ...]` | Empty allowed; items nonblank |
| `strengths` | `tuple[str, ...]` | Empty allowed; items nonblank |
| `risks` | `tuple[str, ...]` | Empty allowed; items nonblank |
| `cultural_advantages` | `tuple[str, ...]` | Empty allowed; items nonblank |
| `marketing_suggestions` | `tuple[str, ...]` | Empty allowed; items nonblank |
| `content_directions` | `tuple[str, ...]` | Empty allowed; items nonblank |

Invalid direct construction raises `ValueError`; no coercion from string
scores, floats, arbitrary enum values, or blank collection elements. Score is an
AI-assisted heuristic indicator only, not a probability, scientific prediction,
sales forecast, expected-sales metric, or ML ranking. No recommendation-to-score
threshold is defined.

### Application capability and failures

`LLMPort` retains `async status() -> ProviderStatus` and adds only:

`async analyze_product_market(product: Product, market: MarketContext) -> ProductMarketAnalysis`.

`AnalyzeProductUseCase(llm).execute(product, market)` receives an injected port,
forwards the exact supplied objects once, and returns its structured result.
Application-owned failures are:

```text
LLMError(Exception)
├── LLMUnavailable
└── InvalidLLMResponse
```

Infrastructure will map outage, timeout, and SDK failures to `LLMUnavailable`,
and malformed output or invalid fields/score/enum to `InvalidLLMResponse`.
The use case propagates either failure without retry, wrapping, ranking,
enrichment, or fallback behavior. The future mock is deterministic and key-free.

## Functional requirements

- Preserve the flow and exact port signature above; do not add generic request
  DTOs or provider controls such as model, temperature, or response format.
- Keep the architecture directional: Domain imports no outer layer;
  Application may import Domain only; Infrastructure/Presentation depend inward;
  Bootstrap is the composition root. Domain/Application remain provider-
  independent, with no SDK, HTTP, FastAPI, or JSON/filesystem mechanics.
  Application owns ports/use cases; Infrastructure owns provider mechanics.
- Every validation boundary above must have an executable test, including score
  endpoints 0 and 100, empty collections, and both failure categories.
- The caller supplies a valid `Product`; no repository lookup or catalog change
  is introduced.

## Out of scope

HTTP/OpenAPI, frontend, real
providers/SDKs, generic `LLMRequest`/`ChatCompletion` abstractions or
`messages`/`model`/`temperature`/`max_tokens`/`response_format` controls,
digital-human or content generation,
product repositories/catalog changes, persistence, enrichment, ranking, caching,
retry, orchestration, RAG, crawling, realtime data, vector DB, and ML scoring.

Constitution 1.2.0 authorizes GREEN for this frozen core. Verification requires
the focused suite, `make architecture-check`, `make check`, and `git diff --check`.
