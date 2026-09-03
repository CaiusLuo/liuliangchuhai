# Implementation Plan: Product Data Foundation

**Branch**: `feat/1-product-foundation` | **Spec**: [spec.md](spec.md)

## Design

Use a frozen standard-library dataclass for `domain/product.py`, an async
`application/ports/product_repository.py` protocol, and two small use cases in
`application/use_cases/`. Keep unknown-product behavior in the get use case.

Implement the snapshot repository and bundled UTF-8 `demo_products.json` in
`infrastructure/products/`. Validate external data at loading and use the canonical
domain value for all returned objects. Use Decimal for optional CNY amounts and
immutable tuples for collections. Reject ambiguous duplicate IDs at startup.
Resolve the demo resource with `importlib.resources` in bootstrap and construct one
repository shared by both use cases. No new dependencies or top-level directories.

## Constitution review

Version 1.1.0 documents the narrow transition beyond the completed Phase 0. Core
boundaries and the standard-library policy are unchanged. The only new external
dependency is a local JSON catalog behind an application port; shared tests use a
deterministic fake. No HTTP DTOs or generated client changes are needed. Existing
import checks cover the new modules without policy exceptions.

## Verification order

Write domain, application, shared repository contract, malformed-data, bootstrap,
and acceptance tests first. Record a failing focused run before source changes.
Implement, rerun to GREEN, then run `make check`. Review packaging of the JSON
resource and the final diff, preserving the pre-existing `next-env.d.ts` change.
