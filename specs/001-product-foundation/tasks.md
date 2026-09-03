# Tasks: Product Data Foundation

- [x] T001 Read issue #1 and comments, current branch, constitution, and Phase 0 specification.
- [x] T002 Specify product/domain/port/adapter contracts and the narrow phase transition.
- [x] T003 Write domain and application tests using a deterministic repository fake.
- [x] T004 Write shared repository contracts, invalid JSON tests, and composition/acceptance tests.
- [x] T005 Run focused tests and record RED before implementation.
- [x] T006 Implement canonical Product, repository port, and read-only use cases.
- [x] T007 Implement JSON snapshot adapter and at least three bundled demo products.
- [x] T008 Wire the shared repository and use cases in bootstrap; document usage.
- [x] T009 Run focused tests to GREEN and refactor as needed.
- [x] T010 Run `make check`, verify resource packaging, and inspect final diff.

## Verification evidence

- RED: focused pytest run exited 4 while loading test fixtures with
  `ModuleNotFoundError: No module named 'liuliangchuhai.application.ports.product_repository'`.
  No product implementation existed at that point.
- GREEN: the same focused pytest command passed all 52 new tests after implementation.
- Full gate: `UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache make check`
  passed formatting, backend lint/types, all four import-linter contracts and the
  core import policy, 52 unit tests, 11 contract tests, 4 integration tests,
  2 acceptance tests, frontend lint/types/build, and generated contract drift.
  Total: 69 backend tests, including the 52 new product tests.
- Packaging: `uv build --project apps/api --wheel` succeeded. The built wheel
  contains `demo_products.json`; loading the package directly from the wheel in
  a temporary working directory successfully listed and retrieved all three demo
  products. Initial sandbox DNS restrictions required a network-enabled retry to
  fetch the existing hatchling build dependency; no project dependencies changed.
- Final review: `git diff --check` passed; source search confirms one canonical
  Product class. The pre-existing `apps/web/next-env.d.ts` change is preserved;
  HTTP routes, OpenAPI, and generated TypeScript are unchanged.
