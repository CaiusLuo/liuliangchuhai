# Plan: Product Analysis Frontend

**Spec**: [spec.md](spec.md) | **Phase**: Reviewed SPEC + RED -> authorized GREEN.

## Small implementation boundary

| File under apps/web/src | Responsibility |
| --- | --- |
| `app/analysis/page.tsx` | Server page composing the workbench; no fetch or backend rules |
| `features/selection/AnalysisWorkbench.tsx` | Client component: catalog/form/submission state, accessible controls and report |
| `features/selection/analysis.module.css` | Scoped responsive form/report styles; preserve root/global styles |
| `api/selection.ts` | Two generated-type API functions, normalization, fetch and stable error translation |
| `features/selection/selection.contract.ts` | Type-only compile-time probe, never imported by the page at runtime |

Use existing React 19, Next.js App Router, native form elements and CSS Modules.
Follow the installed Next.js server/client and CSS guides required by web/AGENTS.md.
Use small local form/report subcomponents if the workbench becomes hard to read;
no shared component package or extra state/form/network/test library is needed.
The root page/layout, health API helper, backend and generated schema remain unchanged.

## Data and state ownership

`selection.ts` exports ProductListResponse, ProductAnalysisRequest and
ProductAnalysisResponse as aliases of generated `paths`. Mirror health.ts's public
API URL convention; GET with no-store and POST JSON using existing endpoint paths.
Normalize the four request fields there; reject required blanks before fetch.
Status mapping follows spec.md, ignoring raw backend error text; network/JSON errors
use the relevant fixed fallback. No retry framework, caching layer or new API proxy.

The client loads catalog on mount and explicit retry; safely ignore stale completion
after unmount. Catalog options retain backend IDs, names and order. Start with a
placeholder selection. Keep controlled field values locally; required control
attributes and trimmed-value handler checks gate submit. Disable inputs/button while
submitting and use a synchronous in-flight guard to prevent repeated requests.
Render only the returned analysis for the submitted form; clear previous results
on a new submit or edit. Never call fetch in page/components/features.

Model catalog loading/error/ready (including empty), plus idle/submitting/error/
success analysis status; do not introduce a general state-machine abstraction.
Provide retry, retained form inputs, explicit empty state, accessible labels and
announced status/errors. Render the nine result fields with readable headings,
enum-label mapping and the heuristic-score disclaimer. Do not present raw JSON.

## Minimal RED and governance

Before RED, run the existing repository gate, which invokes frontend lint,
typecheck and build without adding tooling. The sole new probe derives request/
response types directly from generated paths and constrains the future module's
two exported functions through a generic type assignment. Type-only import/query
produces no HTTP calls or runtime implementation. It is included by the existing
`src/**/*.ts` tsconfig pattern. Expected RED: only TS2307 for missing `@/api/selection`.
Do not introduce placeholder exports, suppressions, UI source-text tests or dependencies.

Amend constitution 1.4.0 -> 1.5.0 with one scoped #4 paragraph: `/analysis` consuming
existing GET `/products` and POST `/product-analysis`, generated types, and frontend
loading/error/success UI. Preserve all Core Principles and earlier increments;
exclude #5, backend/new API contracts, providers, content generation and digital
human work. AGENTS now reflects explicit GREEN approval while retaining the stop
before commit/push/PR. The approved type-only probe remains unchanged.

## GREEN verification after approval

Implement API boundary first (probe becomes GREEN), then page/workbench/scoped CSS.
Run frontend lint/typecheck/build and `make check`; do not regenerate contracts.
Per the GREEN instruction, keep manual verification light and optional: use the
existing mock-backed API to check /analysis, catalog options, valid submission,
complete result and disabled submit. If practical, use temporary deterministic
responses for error mapping/normalization without adding a framework. Capture
screenshots when available; report any unverified visual/accessibility cases.
Do not build a browser test suite or add runtime demo data for this increment.
Review scope/diff and stop before commit/push/PR unless separately authorized.
