# Tasks: Read-only Product API

**Scope**: SPEC + RED approved; GREEN verified. Awaiting review; no commit/push/PR.

## Completed SPEC + RED

- [x] T001 Read live Issue #17, AGENTS, constitution, #1/#3 specs/plans/tasks,
  existing Product/read use cases, Presentation, bootstrap and generation workflow.
- [x] T002 Verify existing branch and clean baseline; run baseline `make check`.
- [x] T003 Freeze spec and compact plan; record deferred 1.4.0 amendment and update
  active agent guidance without changing constitution or production.
- [x] T004 Add mapper, HTTP, OpenAPI/generated-TypeScript and boundary RED tests.
- [x] T005 Run focused Ruff and pytest with `--continue-on-collection-errors`;
  record command, counts and the reason for every failure/error.
- [x] T006 Inspect status, diff/check/stat and new files; confirm exclusions;
  STOP for user review without GREEN, commit, push, or PR.

## Authorized GREEN

- [x] T007 Amend constitution 1.3.0 -> 1.4.0 as narrowly specified in plan.md and
  align active guidance. Preserve all Core Principles; authorize only Issue #17's
  read-only HTTP/generated contract, no #5 implementation or admin/write APIs.
- [x] T008 Implement Presentation response/error schemas and explicit mappers.
- [x] T009 Implement the router using existing ListProducts/GetProduct once per
  endpoint; wire only bootstrap/app.py using existing container fields.
- [x] T010 Extend the existing analysis test container fixture for new app wiring
  without changing its behavior assertions; run focused tests and refactor narrowly.
- [x] T011 Run `make openapi`, `make client-gen`, and `make generated-check`.
- [x] T012 Run focused tests, `make architecture-check`, `make check`, and final
  diff review; preserve all out-of-scope production and dependency files.

## Historical RED verification evidence

Baseline before edits: `UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache make check`
exited 0, all checks passed at `d916b17`: 235 unit, 30 contract, 24 integration,
2 acceptance tests (**291 passed**); formatting, lint, mypy (41 source files),
4 import-linter contracts, core import policy, frontend lint/typecheck/build and
generated contract drift passed. Baseline generation wrote only temporary candidates.

Final focused command from repository root (exit 1):

```sh
UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache uv run --project apps/api pytest apps/api/tests/unit/test_product_mappers.py apps/api/tests/integration/test_product_read_api.py apps/api/tests/contract/test_product_read_openapi.py apps/api/tests/contract/test_product_read_api_architecture.py --continue-on-collection-errors -q --tb=short
```

**18 failed, 2 passed, 1 error in 0.60s**. Every failing/error case is explained:

| Cases | Count | RED reason |
| --- | --- | --- |
| Mapper module collection | 1 error | Missing `presentation.http.product_mappers`; seven mapper cases cannot collect, no placeholder added |
| List, empty list, detail indices 0/1, real catalog | 5 failed | Missing GET routes return framework 404 instead of 200 |
| Injected and real unknown product | 2 failed | Missing handler returns `{"detail":"Not Found"}` instead of frozen code/message |
| List/detail response-model ownership | 2 failed | Recursive traversal finds neither GET route |
| List 200, detail 200 and 404, each runtime/committed | 6 failed | Both OpenAPI documents lack the product read paths |
| Generated TypeScript consumer | 1 failed | TS2339 for both paths and both response models; consequent TS2344 exact-field checks also fail because models are missing |
| Router/mapper architecture checks | 2 failed | Both scoped Presentation files are absent |
| Health and analysis regressions | 2 passed | Existing real bootstrap/mock endpoints remain functional |

The mapper cases cover every field, tuple/list order and empty collections,
`Decimal("12.50")`, `Decimal("0")`, null price/URL, source immutability and ordered
collection mapping. HTTP fakes cover decimal and null serialization; the real
catalog currently has null prices. Architecture checks will reject absolute,
relative and aliased repository/infrastructure/bootstrap imports when modules exist.

Focused Ruff commands both exited 0 (`All checks passed`, `4 files already formatted`):

```sh
UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache uv run --project apps/api ruff check --config apps/api/pyproject.toml apps/api/tests/unit/test_product_mappers.py apps/api/tests/integration/test_product_read_api.py apps/api/tests/contract/test_product_read_openapi.py apps/api/tests/contract/test_product_read_api_architecture.py
UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache uv run --project apps/api ruff format --check --config apps/api/pyproject.toml apps/api/tests/unit/test_product_mappers.py apps/api/tests/integration/test_product_read_api.py apps/api/tests/contract/test_product_read_openapi.py apps/api/tests/contract/test_product_read_api_architecture.py
```

Post-RED `UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache make check` exits 2:
format/lint/type/architecture stages pass; unit collection stops on the same
missing mapper (1 error). Later stages are not run in that invocation. The current
tree is intentionally RED; only the pre-edit baseline has a fully passing gate.

Final scope review: `git diff --check` passes. Tracked `git diff --stat` shows
only AGENTS.md (4 insertions, 3 deletions); four new test files and three new spec
files remain untracked and were reviewed separately. The ignored local
`.specify/feature.json` points to this spec. Constitution remains 1.3.0; its narrow
1.4.0 amendment is T007, not authorization to start GREEN now. No production,
Domain/Product, ListProducts/GetProduct, repository, analysis/content-plan,
frontend/#5, dependency/lockfile, or generated-artifact changes. No commit/push/PR.

## Verified GREEN after explicit approval

Governance first: AGENTS accurately described RED under 1.3.0. Amended constitution
to 1.4.0 before production edits, then updated active guidance. Only Issue #17's
read-only HTTP/Presentation/generated contract is newly authorized. Core Principles
are byte-for-byte unchanged; no #5, writes/admin or unrelated capability grant.

Implemented ProductResponse (exactly 11 fields), ProductListResponse and a dedicated
ProductNotFoundResponse in schemas.py; explicit product/collection mappers; a thin
products router invoking each existing use case once; and one app registration
using the existing container fields. Container, Domain, Application and repositories
are unchanged. Decimal uses `str(product.price)` only when non-null, preserving
scale and zero; tuples become new lists. No enrichment or source mutation.

Incremental verification (all commands prefixed with
`UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache`):

- Mapper-only pytest: **7 passed in 0.04s**.
- Runtime mapper/HTTP/architecture/OpenAPI, excluding committed/generated cases:
  **23 passed, 4 deselected in 0.21s**.
- Existing analysis plus product-read HTTP: **31 passed in 0.20s**. Per the reviewed
  plan, only the old analysis container fixture/import was extended with two read
  substitutes that raise if invoked. Its test functions and helper classes are
  AST-identical; analysis behavior/assertions were not changed.
- `make openapi` then `make client-gen`: both exit **0**. Artifacts generated by
  existing workflow only; generated ProductResponse.price is `string | null`.

Complete focused command, without collection-error tolerance:

```sh
UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache uv run --project apps/api pytest apps/api/tests/unit/test_product_mappers.py apps/api/tests/integration/test_product_read_api.py apps/api/tests/contract/test_product_read_openapi.py apps/api/tests/contract/test_product_read_api_architecture.py -q --tb=short
```

Exit **0**, **27 passed in 0.65s**, including temporary TypeScript compilation.
All four approved Issue #17 test-file SHA-256 hashes match the pre-GREEN snapshot.

- `make architecture-check`: exit **0**, **4 contracts kept, 0 broken**; core import
  policy passes. No global architecture rule changed.
- `make generated-check`: exit **0**, both generated candidates match.
- `make check`: exit **0**, all checks passed. **242 unit + 39 contract + 35
  integration + 2 acceptance = 318 tests**; formatting/lint, mypy (43 source files),
  architecture, frontend lint/typecheck/build, generated drift all pass.
- `git diff --check`: exit **0**. Reviewed tracked diff and new modules/documents.

Final review: pre-existing OpenAPI paths and schemas are semantically identical.
Issue #1 Domain/Application, #3/#6 contracts, Container, providers/catalog and
dependency/lockfiles are unchanged. Web changes consist only of generated schema.ts;
no #5 UI or frontend product code. No extra refactor was needed. Index remains
empty; no commit, push, or PR. Stop for review.
