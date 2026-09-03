# Feature Specification: Product Data Foundation

**Feature Branch**: `feat/1-product-foundation`
**Created**: 2026-09-04
**Status**: Implemented and locally verified
**Source**: [GitHub issue #1](https://github.com/CaiusLuo/liuliangchuhai/issues/1)

## Scope and phase transition

This is the first bounded Phase 1 feature after the completed Phase 0 bootstrap.
It adds a shared, read-only product foundation for future operator and consumer
features. It does not implement those experiences. The Phase 0 specification
remains a historical record; this specification owns the product contracts.

Constitution amendment 1.1.0 permits only this curated JSON catalog and read-only
application capability. No database, writes, admin CRUD, authentication, inventory,
orders, scraping, recommendations, market analysis, content generation, prompts,
RAG, embeddings, queues, or real providers are included. There are no new HTTP
routes or frontend features; the existing HTTP/OpenAPI contract remains unchanged.

## Canonical domain contract

There MUST be exactly one `Product` domain representation, independent of external
libraries and filesystem concerns. Products are immutable values with these fields:

| Field | Python type | Contract |
| --- | --- | --- |
| id | str | Stable, nonblank, no surrounding whitespace; unique per catalog |
| name | str | Nonblank display name |
| category | str | Nonblank category |
| description | str | Nonblank descriptive text |
| origin | str | Nonblank Guangxi origin |
| cultural_background | str | Nonblank cultural context |
| images | tuple[str, ...] | Image references; empty when no licensed asset is supplied |
| usage | str | Nonblank usage description |
| ingredients | tuple[str, ...] | Nonblank ingredient names; may be empty |
| price | Decimal or None | Optional finite nonnegative CNY amount, at most two decimal places |
| purchase_url | str or None | Optional nonblank URL reference; not fetched or verified |

Collection fields contain only nonblank strings. Required text is preserved as
provided; only identifiers reject surrounding whitespace. No live pricing, vendor,
asset availability, or recommendation claims are made by the demo catalog.

## Application contracts

- `ProductRepository` is an application-owned async `Protocol` with
  `list_products() -> tuple[Product, ...]` and
  `get_by_id(product_id: str) -> Product | None`.
- Listing preserves curated catalog order and returns an empty tuple for an empty
  catalog. Lookup uses exact, case-sensitive IDs with no trimming or normalization.
- `ListProducts.execute()` delegates listing through the port.
- `GetProduct.execute(product_id)` returns the product or raises an explicit
  application `ProductNotFound` exception carrying `product_id` when absent.
- Application behavior imports no concrete repository, file paths, or JSON code.

## JSON adapter and composition

- A JSON-backed infrastructure adapter loads a UTF-8 JSON array at construction.
  Each object uses the domain field names; all fields except `price` and
  `purchase_url` are required. Collections are JSON arrays. Prices, when present,
  are decimal strings (for example `"12.50"`), avoiding floating-point conversion.
- Reject malformed JSON, non-array roots, invalid fields, and duplicate IDs with
  a contextual `ValueError`; missing/unreadable files raise `OSError`. Never skip
  invalid entries or silently substitute an empty catalog.
- The repository exposes an immutable in-memory snapshot. Reads perform no file
  or network I/O; reconstruct it to reload a changed file. There are no write APIs.
- Bootstrap alone chooses the adapter, resolves the bundled demo resource relative
  to the package rather than the working directory, and injects both use cases.
- Bundle at least three deterministic representative Guangxi products, with no
  external credentials required. Tests use a fake and temporary JSON fixtures.

## Acceptance scenarios

1. The same repository contract suite passes for a deterministic in-memory fake
   and the JSON adapter: ordered listing, exact lookup, absent IDs, empty catalogs,
   repeatability, and immutable results.
2. Unit tests verify domain values and invalid inputs, delegation, and explicit
   unknown-product behavior without filesystem access in application code.
3. Adapter tests reject corrupt/invalid catalogs and duplicate IDs, preserve
   Unicode and optional fields, and prove snapshot semantics.
4. Bootstrap integration and acceptance tests retrieve at least three unique
   bundled products through both use cases without API keys, including from a
   different working directory.
5. `make check` passes, including architecture checks and unchanged generated
   HTTP/OpenAPI artifacts.
