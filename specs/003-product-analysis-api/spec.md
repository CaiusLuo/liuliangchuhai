# Feature Specification: Product Analysis API

**Branch**: `feat/3-product-analysis-api`
**Date**: 2026-09-04
**Status**: Frozen contract; reviewed RED and verified GREEN
**Source**: [Issue #3](https://github.com/CaiusLuo/liuliangchuhai/issues/3) and the user's frozen HTTP contract; depends on merged #1 and #2.

## User scenario

A caller selects a catalog product by ID and supplies a target market to receive
structured AI-assisted analysis. The server owns the canonical Product; clients
cannot supply or replace its contents. Scores retain Issue #2's heuristic meaning,
not a probability, forecast, scientific score, or expected sales metric.

## HTTP request

Expose exactly `POST /product-analysis` with JSON:

| Field | Type | Required / validation |
| --- | --- | --- |
| product_id | string | Required, nonblank |
| country | string | Required, nonblank |
| target_audience | string or null | Optional; nonblank string when present |
| market_notes | string or null | Optional; nonblank string when present |

Omitted optional fields map to None; explicit null is accepted only for optional
fields. Reject non-string values without coercion and blank/whitespace-only strings.
Invalid JSON/schema input returns standard FastAPI/Pydantic 422. A client-supplied
Product object is rejected, including a `product` field alongside a valid ID.
Preserve valid strings as supplied; lookup semantics remain Issue #1's exact ID
contract. No /api/v1, /selection, or router namespace redesign. /health is unchanged.

## Application workflow

```text
product_id -> GetProduct -> exact canonical Product
                               + exact MarketContext
                               -> AnalyzeProductUseCase -> exact ProductMarketAnalysis
```

`AnalyzeProductByIdUseCase(get_product, analyze_product).execute(product_id, market)`
receives injected GetProduct and AnalyzeProductUseCase. Lookup and analysis are
awaited exactly once in that order. Forward exact inputs/objects and return the
exact analysis instance. Propagate ProductNotFound unchanged and do not call
analysis after lookup fails. Propagate LLMUnavailable and InvalidLLMResponse
unchanged. No retries, fallback, caching, direct repository access, enrichment,
or provider knowledge.

## HTTP success response

HTTP 200 uses a Presentation-owned `ProductMarketAnalysisResponse` model and an
explicit mapper, never the Domain dataclass as FastAPI's response_model.

| Field | JSON contract |
| --- | --- |
| recommendation | strong_fit, fit, caution, or not_recommended |
| score | Integer, inclusive 0..100 |
| summary | Nonblank string |
| target_audiences | Array of nonblank strings; empty allowed |
| strengths | Array of nonblank strings; empty allowed |
| risks | Array of nonblank strings; empty allowed |
| cultural_advantages | Array of nonblank strings; empty allowed |
| marketing_suggestions | Array of nonblank strings; empty allowed |
| content_directions | Array of nonblank strings; empty allowed |

Map all values exactly, preserving collection order; serialize the enum as its
string value and tuples as JSON arrays. Do not expose dataclass internals or any
additional result envelope.

## HTTP error contract

Application errors use exactly `{"code": "...", "message": "..."}` (no detail wrapper):

| Failure | Status | code | Public message |
| --- | --- | --- | --- |
| ProductNotFound | 404 | product_not_found | Product not found |
| LLMUnavailable | 503 | llm_unavailable | Analysis service is temporarily unavailable |
| InvalidLLMResponse | 502 | invalid_llm_response | Analysis service returned an invalid response |

Invalid HTTP input uses the framework's 422 validation body. Application error
messages above are stable and never interpolate exception details, provider names,
SDK messages, traceback text, or httpx/OpenAI details.

## Architecture and generated contracts

Presentation only validates requests, maps MarketContext, invokes the single
AnalyzeProductByIdUseCase, maps the result and the three application failures.
It must not perform GetProduct-then-AnalyzeProductUseCase orchestration itself.
Application remains inward-only; bootstrap selects and wires concrete dependencies.
Keep existing import-linter/core gates and add only Issue #3 Presentation leakage
checks. No new global stdlib bans.

Use Presentation request/response/error schemas with operation ID `analyze_product`.
Document 200/422 and explicit 404/502/503 JSON responses. OpenAPI must include the
request, response, recommendation enum, and stable error shape. In GREEN,
regenerate FastAPI -> `apps/api/openapi.json` -> openapi-typescript ->
`apps/web/src/api/generated/schema.ts`, then run generated-check. Never hand-edit
those artifacts.

## Acceptance criteria and scope

- Unit fakes verify exact input forwarding, call counts, result identity, and all
  three propagated application failures without repositories/providers.
- Mapper/schema tests cover minimal/optional/null/invalid requests and exact JSON output.
- HTTP tests cover 200, 404, 422, 503, 502; validation never invokes the use case;
  failures expose only the stable body; /health remains functional.
- Live and committed OpenAPI plus generated TypeScript expose the frozen contract.
- Reviewed RED records meaningful failures, with no skips/xfails or production stubs.
- GREEN is authorized under constitution 1.3.0; finish generation, generated-check,
  architecture-check, make check, and final diff review.

Out of scope: frontend UI, real providers,
SDKs/prompts, auth, persistence/history, streaming, content generation, digital human,
API versioning, generic exception/controller/service frameworks, repository/catalog
changes, new dependencies, and Issue #4. Do not commit, push, or create a PR.
