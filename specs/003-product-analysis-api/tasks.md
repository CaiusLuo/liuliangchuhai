# Tasks: Product Analysis API

**Input**: [spec.md](spec.md), [plan.md](plan.md)
**Scope**: SPEC + RED approved; GREEN verified. Awaiting user review; no commit, push, or PR.

## SPEC and RED

- [x] T001 Sync main with `git pull --ff-only` and create `feat/3-product-analysis-api`; read existing guidance/core/HTTP files and GitHub issue #3/comments.
- [x] T002 Freeze HTTP/application/error contracts in `spec.md`; record ownership, paths, wiring and verification in `plan.md` using existing Spec Kit templates.
- [x] T003 Update active guidance in `AGENTS.md` and the local `.specify/feature.json` pointer; keep constitution 1.2.0 and production unchanged.
- [x] T004 [US1] Add local lookup/analysis fakes and orchestration tests in `apps/api/tests/unit/test_analyze_product_by_id.py`.
- [x] T005 [US1] Add strict request and explicit response-mapper tests in `apps/api/tests/unit/test_product_analysis_mappers.py`.
- [x] T006 [US1] Add injected HTTP fake tests in `apps/api/tests/integration/test_product_analysis_api.py`; share existing-domain fixtures in `apps/api/tests/conftest.py`.
- [x] T007 [US1] Add runtime/committed OpenAPI and generated-TS expectations in `apps/api/tests/contract/test_product_analysis_openapi.py`.
- [x] T008 [US1] Add narrow Presentation leakage checks in `apps/api/tests/contract/test_product_analysis_api_architecture.py`.
- [x] T009 Run focused Ruff checks and the RED suite; record exact evidence below.

The reviewed RED phase stopped after T009 without production stubs, skips or xfails.

## GREEN and verification

- [x] T010 Align `.specify/memory/constitution.md` capability scope/version and `AGENTS.md` before production implementation.
- [x] T011 [US1] Implement `application/use_cases/analyze_product_by_id.py` and Presentation schemas/mappers/router at the paths in `plan.md`.
- [x] T012 [US1] Add a failing composition test, then wire the existing use cases in `bootstrap/container.py` and the new router in `bootstrap/app.py`.
- [x] T013 [US1] Run the focused behavioral suite to GREEN; keep generated-contract expectations RED until regeneration.
- [x] T014 REFACTOR narrowly: inspect new application/presentation/bootstrap code for duplicate rules, orchestration leakage and provider coupling.
- [x] T015 Run `make openapi` to regenerate `apps/api/openapi.json`.
- [x] T016 Run `make client-gen` to regenerate `apps/web/src/api/generated/schema.ts`.
- [x] T017 Run `make generated-check` and the full focused suite; record artifact and test results here.
- [x] T018 Run `make architecture-check` without weakening existing rules.
- [x] T019 Run `make check` and `git diff --check`; record exact results here.
- [x] T020 Review the final diff, regenerated contracts, unchanged health, and scope exclusions; no commit, push, or PR creation is authorized.

All production paths in T011-T014 are beneath `apps/api/src/liuliangchuhai/`.
Sequence: SPEC -> RED -> GREEN -> REFACTOR -> OpenAPI -> client -> generated-check
-> architecture-check -> make check -> PR verification. T004-T008 can be authored
independently after the spec, but all implementation waits for reviewed RED and
explicit GREEN authorization. US1 is the single product-analysis request scenario.

## RED evidence

Command executed from the repository root:

```sh
UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache uv run --project apps/api pytest apps/api/tests/unit/test_analyze_product_by_id.py apps/api/tests/unit/test_product_analysis_mappers.py apps/api/tests/integration/test_product_analysis_api.py apps/api/tests/contract/test_product_analysis_openapi.py apps/api/tests/contract/test_product_analysis_api_architecture.py --continue-on-collection-errors -q --tb=short
```

Exit **1**: **26 failed, 2 passed, 2 errors in 0.26s**.

- Application/mapper unit tests cannot collect because
  `application.use_cases.analyze_product_by_id` and
  `presentation.http.product_analysis_mappers` do not exist. Presentation schemas
  also remain unimplemented; no placeholder was added to bypass those imports.
- HTTP requests reach the existing app and return route-not-found 404, rather than
  the specified success/validation/application-error contracts. The unknown-product
  test correctly rejects the framework's generic 404 body.
- Runtime and committed OpenAPI lack the operation/Presentation response schema;
  generated TypeScript lacks the endpoint marker.
- Unchanged /health and the narrow Presentation import check pass.
- All six touched test files passed focused Ruff format-check and lint.
- Production, OpenAPI, generated TS, frontend, dependency files, tooling, CI and
  constitution were checked against the post-pull baseline and left unchanged.
  Only these three feature documents were created. No regeneration, skips,
  xfails, production stubs, GREEN work, commits, pushes, or PR creation occurred.

## Focused RED self-review

- Added bool to the shared four-field invalid-input matrix, alongside blank,
  whitespace, int and list cases. Optional omission/null remains accepted;
  required omission/null remains rejected with Pydantic ValidationError.
- Removed fixed component-reference and generated-format assertions. OpenAPI
  tests now inspect resolved public schemas; generated TS is checked by compiling
  a temporary API consumer with the installed compiler, without modifying artifacts.
- Moved HTTP JSON expectations out of global conftest; it shares only the domain
  analysis fixture. AGENTS changes remain limited to active-spec/RED guidance.
- Re-ran the exact RED command above: exit **1**, **26 failed, 2 passed, 2 errors
  in 0.80s**. All failures are missing Issue #3 capability; the TS compiler reports
  only TS2339 for missing `/product-analysis` on `paths`. No unrelated failure was found.
- 422 retains framework `detail` validation semantics; only 404/502/503 use the
  stable code/message body. Focused Ruff checks passed. Production/GREEN untouched.

## Initial GREEN progress and test-defect pause

Work is isolated on `feat/3-product-analysis-api` at
`/private/tmp/liuliangchuhai-issue3-green`; the original checkout is on
`feat/6-content-plan-contract` and was preserved with its unrelated work.
Only the approved Issue #3 documents/tests were copied into the isolated worktree.
Constitution 1.3.0 and active guidance narrowly authorize this HTTP increment.

Commands use the same UV cache and `uv run --project apps/api pytest` as above:

- `apps/api/tests/unit/test_analyze_product_by_id.py -q`: **4 passed in 0.01s**.
- `apps/api/tests/unit/test_product_analysis_mappers.py -q`: **29 passed in 0.90s**.
- Added composition test, before container changes:
  `apps/api/tests/unit/test_container.py -k analysis_by_id -q --tb=short`:
  **1 failed, 4 deselected in 0.08s**, missing `Container.analyze_product_by_id`.
- After implementing the router/errors and app inclusion with injected test fakes:
  `apps/api/tests/integration/test_product_analysis_api.py -q --tb=short`:
  **1 failed, 19 passed in 0.39s**. Success, 422, stable 404/502/503 bodies,
  diagnostic non-disclosure, and unchanged health all passed.

The remaining HTTP failure is a test discovery defect, not a missing endpoint:
`test_route_uses_a_presentation_response_model` scans only top-level `app.routes`
for `APIRoute`. The locked FastAPI 0.141.1 stores included routers as
`_IncludedRouter`, so that scan cannot find the route. Read-only verification
confirmed the factory's POST route uses the Presentation-owned
`ProductMarketAnalysisResponse`, and the injected app's runtime OpenAPI exposes
`analyze_product`. Do not change production routing to satisfy this internal-layout
assumption. The user subsequently authorized generic route-tree traversal in this test,
while preserving all ownership and HTTP/OpenAPI assertions.

Per the user's instruction to STOP and report a suspected test defect, no approved
RED tests were edited at that pause (all six saved SHA-256 hashes matched).
T011/T012 were then partial:
the application use case, schemas, mappers, router and app inclusion exist, while
container composition was still unimplemented. The real app was not yet ready
to start, and regeneration and final gates had not run. The resumed work below
completes those steps.
Frozen Domain/existing Application contracts, providers, frontend features and
dependency lockfiles remain unchanged. No Issue #4 work, commit, push, or PR.


## Verified GREEN after authorized test correction

- Changed only the approved HTTP test's route lookup and required imports:
  `iter_api_routes` uses FastAPI's public `iter_route_contexts` to resolve included
  routers and recursively visits nested `.routes` collections. It does not name
  private wrapper classes or assume a fixed nesting depth. The APIRoute, exact
  `/product-analysis` path, POST method, and all response-model ownership assertions
  remain unchanged. All other five approved RED files match their saved SHA-256
  hashes, and the HTTP file diff contains only this authorized correction.
- Focused HTTP command: `UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache uv run
  --project apps/api pytest apps/api/tests/integration/test_product_analysis_api.py
  -q --tb=short`: **20 passed in 0.20s**, including the previously failing model test.
- Completed container composition with its existing `get_product` and
  `analyze_product` instances. Container plus all integration tests:
  **29 passed in 0.21s**. The composition test introduced before wiring now passes.
- Real app smoke with the actual container/catalog/mock adapter: app construction
  succeeds, `/health` returns 200, a canonical catalog product analysis returns 200,
  and an unknown ID returns the exact stable 404 body.
- Full focused suite before generation: **4 failed, 57 passed in 3.91s**. Only
  committed OpenAPI and generated TS were stale; runtime contract tests passed.
- Ran `make openapi` and then `make client-gen`, both exit **0**. OpenAPI and
  TypeScript were generated exclusively through `scripts/dev.py`, not hand-edited.
- Full focused suite after generation, without collection-error tolerance:

```sh
UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache uv run --project apps/api pytest apps/api/tests/unit/test_analyze_product_by_id.py apps/api/tests/unit/test_product_analysis_mappers.py apps/api/tests/integration/test_product_analysis_api.py apps/api/tests/contract/test_product_analysis_openapi.py apps/api/tests/contract/test_product_analysis_api_architecture.py -q --tb=short
```

Exit **0**: **61 passed in 0.61s**. Includes strict input/422 behavior, exact
404/502/503 bodies, no diagnostic leakage, unchanged health, runtime/committed
OpenAPI semantics, and compilation of the generated TypeScript consumer.

All following commands used `UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache`:

- `make architecture-check`: exit **0**, **4 contracts kept, 0 broken**; core import
  policy passed. Existing import-linter and core-check rules were not changed.
- `make generated-check`: exit **0**, both regenerated candidates match.
- `make check`: exit **0**, **All checks passed**. Formatting and lint passed;
  mypy checked 36 source files; unit **153 passed**, contract **24 passed**,
  integration **24 passed**, acceptance **2 passed** (**203 total**). Frontend
  lint, TypeScript check, Next.js production build, and generated drift passed.
- `git diff --check`: exit **0**. Reviewed tracked diffs, new files, and status.

Final review: only the new orchestration use case, Presentation schemas/mappers/
router, bootstrap wiring, generated artifacts, focused tests, and phase/evidence
records changed. Existing Domain and Issue #1/#2 Application contracts, catalog/
adapter behavior, providers, frontend feature code, dependencies, architecture
rules, and tooling are unchanged. No Issue #4 work, commit, push, or PR.
