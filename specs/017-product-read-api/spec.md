# Feature Specification: Read-only Product API

**Branch**: `feat/17-product-read-api` | **Date**: 2026-09-04
**Status**: Frozen contract; SPEC + RED approved, GREEN implemented and verified.
**Authority**: [Issue #17](https://github.com/CaiusLuo/liuliangchuhai/issues/17),
verified live, and the user's frozen contract. Reuse Issue #1; preserve Issue #3.

## HTTP contract

| Endpoint | Success | Application failure |
| --- | --- | --- |
| `GET /products` | 200 `ProductListResponse { items: ProductResponse[] }` | None introduced |
| `GET /products/{product_id}` | 200 `ProductResponse` | Unknown product: frozen 404 below |

The list has exactly one top-level field, `items`; no pagination, count, or page
metadata. Preserve `ListProducts.execute()` order, including an empty list.
Forward the exact detail ID to `GetProduct.execute(product_id)` using existing
Issue #1 lookup semantics. Do not introduce `/api/v1`.

Presentation owns both response models, the public error schema, and explicit
mappers. Each product response contains exactly these fields:

| Field | JSON type |
| --- | --- |
| id, name, category, description, origin, cultural_background, usage | string |
| images, ingredients | string[] |
| price, purchase_url | string or null |

Map every value without enrichment or normalization. Explicitly map domain tuples
with `list(...)`, retaining order. Map non-null price with `str(product.price)`:
`Decimal("12.50") -> "12.50"`, `Decimal("0") -> "0"`, `None -> null`.
Never pass through float/int or implicit numeric serialization. Preserve Issue #1
CNY semantics and null purchase URLs. Mapping must not mutate the domain Product.
Do not expose its dataclass as FastAPI's response model.

Unknown products return HTTP 404 with exactly:

```json
{"code": "product_not_found", "message": "Product not found"}
```

Never expose the requested ID, raw ProductNotFound text, repository details,
filesystem paths, or tracebacks. Keep `/health` and `/product-analysis` behavior.

## Ownership and acceptance

Each route invokes exactly one existing application use case once: list invokes
`ListProducts`; detail invokes `GetProduct`. Reuse `ProductNotFound`. No additional
service, wrapper, orchestrator, or repository port. Bootstrap supplies the existing
container fields; routers and mappers cannot import infrastructure or repositories.

RED tests cover all mapped fields, tuple/list conversion, exact Decimal strings,
nulls, immutability, ordered collections, real demo catalog HTTP responses, fake
use-case delegation, stable private-error translation, and explicit Presentation
response models through recursive route discovery. Runtime and committed OpenAPI
must describe both GETs, the exact product fields, string/null price and public
404. Compile a temporary generated-TypeScript consumer for both paths and models.
Use semantic assertions; no full generated snapshots or formatting checks.

## Scope and phase gate

The user approved SPEC + RED and authorized GREEN. Constitution 1.4.0 narrowly
permits this increment: implement thin Presentation and app wiring, regenerate
OpenAPI/TypeScript through the existing workflow, and pass the existing gates.
Preserve the approved RED tests. Stop before commit, push, or PR for review.

Excluded: #5/frontend catalog, pagination, search/filter/sort, localization,
recommendations, AI chat, auth, CRUD/admin/writes, databases, market pricing,
payment/orders/inventory, analysis/content-plan changes, real providers, new
dependencies, and unrelated tooling. No commits, pushes, or PRs in this turn.
