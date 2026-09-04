# Feature Specification: Product Analysis Frontend

**Branch**: `feat/4-product-analysis-frontend` | **Date**: 2026-09-04
**Status**: GREEN implemented and verified; awaiting review before commit.
**Authority**: [Issue #4](https://github.com/CaiusLuo/liuliangchuhai/issues/4),
verified live; existing #3 analysis and #17 product-read contracts are frozen.

## Route and operator flow

Expose only `/analysis`: load `GET /products`, select a backend product by its
`id`/`name`, enter required country and optional target audience/market notes,
submit `POST /product-analysis`, then read the structured report. Preserve catalog
order; never hardcode catalog IDs/names or analysis results. Direct navigation is
sufficient; leave the root page unchanged. `/products` and `/products/[id]` are #5.

## API boundary and request

All Issue #4 fetch calls, HTTP status handling, JSON parsing and safe error mapping
belong in `apps/web/src/api/selection.ts`. React/features call its exported functions,
never raw fetch. Use the existing `NEXT_PUBLIC_API_URL` convention and localhost
fallback from health.ts. No backend changes or regeneration are required.

Derive aliases directly from generated `paths` (never duplicate backend interfaces):

- `ProductListResponse`: GET `/products` JSON 200 response.
- `ProductAnalysisRequest`: POST `/product-analysis` JSON request body.
- `ProductAnalysisResponse`: POST `/product-analysis` JSON 200 response.

API exports: `listProducts(): Promise<ProductListResponse>` and
`analyzeProduct(request: ProductAnalysisRequest): Promise<ProductAnalysisResponse>`.
The API module resolves successful generated-type payloads and rejects failures
with only the stable user-facing messages below; never surface raw error bodies,
exceptions, stacks or provider diagnostics.

The selector's product_id must come from the loaded catalog. Trim strings before
submission: product_id and country must remain nonblank, otherwise make no POST.
Trim optional target_audience/market_notes; omitted, null, empty or whitespace-only
values normalize to null (allowed by the generated request). Send only those four
fields. No product payload, prompts, enrichment, or frontend business inference.

## Stable errors

| Failure | User-facing message |
| --- | --- |
| Catalog HTTP/network/JSON failure | Unable to load products. Please try again. |
| Analysis 422 or locally blank required input | Please check the form inputs. |
| Analysis 404 | The selected product is no longer available. |
| Analysis 502 | Analysis returned an invalid response. Please try again. |
| Analysis 503 | Analysis service is temporarily unavailable. Please try again later. |
| Other analysis HTTP/network/JSON failure | Unable to run analysis. Please try again. |

## UI states and result

Explicit states: catalog loading; catalog error with retry; form ready; analysis
submitting; analysis error with retained inputs and retry; analysis success.
An empty catalog shows "No products are available." and cannot submit; allow catalog
reload. Choose no product until the user selects one. Disable submit until required
values are valid and during submission; block duplicate in-flight requests.
Clear stale report/error on a new submission or form edit. Use associated labels,
keyboard-operable native controls and aria-live/status/alert feedback. Keep the
form and report readable at narrow and desktop widths.

Display all nine response fields: recommendation, score, summary, target_audiences,
strengths, risks, cultural_advantages, marketing_suggestions, content_directions.
Preserve section/item order; empty result arrays have a neutral "None provided"
state. Map enum labels only: strong_fit -> Strong fit, fit -> Fit, caution -> Caution,
not_recommended -> Not recommended. Show "Heuristic score: 50 / 100" using the actual
score plus "Not a forecast or probability." Do not infer recommendations or confidence.

## Phase and acceptance

Constitution 1.5.0 narrowly scopes #4; the user approved SPEC + PLAN + minimal RED
and authorized GREEN. Preserve the type-only probe unchanged; it verifies API
signatures, not UI/runtime correctness. Run typecheck, lint, build and `make check`.
The GREEN instruction allows a light manual smoke when practical and optional
screenshots before PR; do not add dependencies or spend significant time on browser
test automation. Record what was actually verified and any remaining visual checks.

Excluded: #5 UI, backend/Domain/Application changes, new public contracts,
OpenAPI/generated edits, dependencies/lockfiles, provider integrations, prompts,
content generation, digital humans, auth, persistence, and unrelated refactors.
Unexpected backend contract drift means stop and report, not regenerate. Stop for
review before commit, push, or PR.
