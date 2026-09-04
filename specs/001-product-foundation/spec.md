# Product Contract

`Product` is the single immutable domain representation for a curated product.

| Field | Type | Invariant |
| --- | --- | --- |
| `id` | `str` | Nonblank, no surrounding whitespace; unique in a catalog |
| `name`, `category`, `description`, `origin`, `cultural_background`, `usage` | `str` | Nonblank |
| `images`, `ingredients` | `tuple[str, ...]` | Items are nonblank; empty allowed |
| `price` | `Decimal` or `None` | Finite, nonnegative, at most two decimal places |
| `purchase_url` | `str` or `None` | Nonblank when present |

`ProductRepository` is an application-owned async port with ordered
`list_products() -> tuple[Product, ...]` and exact, case-sensitive
`get_by_id(product_id) -> Product | None`. `ListProducts` delegates listing;
`GetProduct` raises `ProductNotFound(product_id)` when lookup returns `None`.
Application code does not depend on a concrete repository or storage format.
