# Plan: Product Analysis API

**Branch**: `feat/3-product-analysis-api` | **Spec**: [spec.md](spec.md)
**Scope**: Reviewed SPEC + RED -> GREEN for the frozen HTTP increment and generated artifacts.

## Ownership and production locations

- `application/use_cases/analyze_product_by_id.py`: the injected two-use-case
  composition; reuse GetProduct, AnalyzeProductUseCase and existing domain/errors.
- `presentation/http/schemas.py`: add ProductAnalysisRequest,
  ProductMarketAnalysisResponse and ProductAnalysisErrorResponse (Pydantic models).
  Validate strings strictly, reject a client-supplied product, and describe the
  result score/enum/arrays and stable application error body explicitly.
- `presentation/http/product_analysis_mappers.py`: `to_market_context(request)`
  and `to_analysis_response(analysis)`; map values without business decisions.
- `presentation/http/product_analysis_router.py`: factory
  `create_product_analysis_router(analyze_product_by_id)` receives only the single
  orchestration use case. Define the frozen POST and explicit response_model;
  map only the three application errors to the bodies in spec.md. Use local error
  handling, not a generic exception framework.
- `bootstrap/container.py`: compose AnalyzeProductByIdUseCase from the existing
  get_product and analyze_product instances as `container.analyze_product_by_id`.
- `bootstrap/app.py`: include the new router with that one use case; retain the
  existing health router and configuration. No new public DI API is needed.

All source paths above are beneath `apps/api/src/liuliangchuhai/`.
The domain Product and analysis contracts, repository, catalog, providers, and
frontend feature code remain unchanged.

## Test design

Under `apps/api/tests/`, add:

- `unit/test_analyze_product_by_id.py`: local GetProduct/analysis fakes with call
  recording; exact identity and failures, including no analysis after missing ID.
- `unit/test_product_analysis_mappers.py`: request/response schemas and
  mappers; strict type/blank checks, optional None, ordered JSON arrays and enum.
- `integration/test_product_analysis_api.py`: inject a local container fake at
  bootstrap's existing build_container seam. It exposes only health and the new
  orchestrator, so Presentation cannot obtain the two lower-level use cases.
  Assert success/error bodies, single invocation, input mapping, response-model
  ownership, validation short-circuit, and unchanged health.
- `contract/test_product_analysis_openapi.py`: inspect both runtime OpenAPI and
  the committed JSON, resolving references without requiring component placement.
  Compile a temporary consumer of generated TS operation/request/response/error
  types using the existing TypeScript compiler; do not match generated formatting.
  Do not duplicate or regenerate whole artifacts in tests.
- `contract/test_product_analysis_api_architecture.py`: inspect only the new
  Presentation router/mapper and shared schemas for outer/provider imports,
  including relative imports. Existing architecture rules remain authoritative.

Share only deterministic, existing-domain analysis fixtures in tests/conftest.py.
Keep HTTP response expectations and orchestration fakes in the focused test files.
During RED, missing imports stayed local to new test modules so root conftest
did not block existing suites. HTTP tests reached the existing app and exposed
missing-route failures. The same behavioral assertions are retained in GREEN.

## Workflow and gates

Constitution 1.3.0 narrowly authorizes this HTTP increment after SPEC + RED review;
existing contracts and architecture rules remain unchanged.

SPEC -> RED -> reviewed GREEN -> narrow REFACTOR -> OpenAPI regenerate
-> client regenerate -> generated-check -> architecture-check -> make check -> final diff review.
Use existing `make openapi`, `make client-gen`, and `make generated-check` tasks;
never edit generated TypeScript manually. Test composition before changing bootstrap.
Keep only spec.md, plan.md and tasks.md; no extra Spec Kit artifacts or dependencies.
