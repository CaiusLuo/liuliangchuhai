# Plan: Read-only Product API

**Spec**: [spec.md](spec.md) | **Phase**: Reviewed SPEC + RED -> authorized GREEN.

## Inspected design and GREEN locations

All production paths below are under `apps/api/src/liuliangchuhai/`.

- `presentation/http/schemas.py`: add `ProductResponse`, `ProductListResponse`,
  and a dedicated `ProductNotFoundResponse` with the frozen code/message. Preserve
  the existing analysis schemas; no general error-schema refactor.
- `presentation/http/product_mappers.py`: `to_product_response(product)` maps
  all fields, explicitly using lists and `str(price)`; `to_product_list_response`
  maps the product tuple in order through the same product mapping.
- `presentation/http/products_router.py`: factory
  `create_products_router(list_products, get_product)` receives the existing use
  cases; define the two GETs with explicit Presentation response models and a
  documented detail 404. Translate only ProductNotFound with a fixed public body.
- `bootstrap/app.py`: include the factory with `container.list_products` and
  `container.get_product`. Container already builds both; no container redesign.

Keep Domain, existing Application use cases/ports, JSON adapter/catalog and
analysis behavior unchanged. No service or orchestration abstraction is needed.

## RED design

Only add the four focused files under `apps/api/tests/`:

- `unit/test_product_mappers.py`: reuse existing Product fixtures, cover every
  field, exact decimal text, optional nulls, ordered/empty tuples and immutability.
  Import the missing mapper directly; collection error is intentional RED.
- `integration/test_product_read_api.py`: real bootstrap/demo catalog checks plus
  injected use-case mocks at the existing build_container seam, proving one call
  and no cross-use-case invocation. Include sensitive ProductNotFound diagnostics,
  two narrow existing-route regressions and Issue #3's recursive route traversal.
- `contract/test_product_read_openapi.py`: resolve local references in runtime
  and committed documents; compare semantic fields/types and list/detail shapes.
  Compile a temporary TypeScript consumer with the installed compiler, including
  exact model/path types and rejection of numeric prices. Tests do not regenerate files.
- `contract/test_product_read_api_architecture.py`: scoped AST import checks for
  router/mapper, including relative and aliased imports; forbid repositories and
  outer layers. Missing modules fail explicitly; global architecture stays intact.

Do not add production stubs, skips/xfails, dependencies, or global fixture changes.
GREEN integration note: the existing Issue #3 injected container fixture exposes
only health and analysis. When app wiring gains two read dependencies, extend that
test fixture with read-use-case fakes, preserving every Issue #3 assertion. Do not
make production dependency lookup optional to accommodate the old test fixture.

## Governance and verification order

Constitution remained 1.3.0 through RED, following Issue #3's review sequence.
After explicit GREEN approval, amendment 1.4.0 adds one Phase Boundaries paragraph
authorizing only Issue #17 / `specs/017-product-read-api` read-only product HTTP
surface and generated contracts, because callers need the existing catalog over
HTTP. Core Principles and other phase grants are preserved. The amendment excludes
#5 implementation, writes/admin, search/filter/pagination, auth, market pricing and
unrelated features; platform/tooling governance is unchanged. Agent guidance is
updated only after that amendment. Approved Issue #17 tests remain unchanged.

After SPEC + RED review and explicit GREEN approval: amendment -> schemas/mappers
-> router/app wiring -> focused tests -> narrow refactor -> `make openapi` ->
`make client-gen` -> `make generated-check` -> `make architecture-check` ->
`make check` -> final diff review. These existing tasks use `scripts/dev.py`;
generation is FastAPI -> `apps/api/openapi.json` -> openapi-typescript ->
`apps/web/src/api/generated/schema.ts`. Never manually edit generated contracts.
