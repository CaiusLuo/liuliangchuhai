# liuliangchuhai

## Development

macOS/Linux:

```sh
make bootstrap
make dev
make check
```

Windows or without Make:

```sh
uv run python scripts/dev.py bootstrap
uv run python scripts/dev.py dev
uv run python scripts/dev.py check
```

See [AGENTS.md](AGENTS.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and
[the active product foundation specification](specs/001-product-foundation/spec.md)
for project rules and scope. The completed bootstrap is documented in
[the Phase 0 specification](specs/000-phase0-bootstrap/spec.md).

## Read-only product catalog

The application provides `ListProducts` and `GetProduct` through the bootstrap
container. Both consume the same application-owned `ProductRepository` port and
canonical domain `Product`. There are no product HTTP routes or product UI yet.

Run Python in the backend environment (`uv run --project apps/api python`):

```python
import asyncio

from liuliangchuhai.application.use_cases.get_product import ProductNotFound
from liuliangchuhai.bootstrap.container import build_container
from liuliangchuhai.bootstrap.settings import Settings


async def main():
    container = build_container(Settings())
    products = await container.list_products.execute()
    product = await container.get_product.execute(products[0].id)
    print(product.name)
    try:
        await container.get_product.execute("unknown-product")
    except ProductNotFound as error:
        print(f"Unknown product: {error.product_id}")


asyncio.run(main())
```

The default catalog is packaged in
`apps/api/src/liuliangchuhai/infrastructure/products/demo_products.json` and contains
柳州螺蛳粉、梧州六堡茶、桂林罗汉果. These are curated demonstration records, not
vendor listings. Ingredient lists are illustrative and are not complete product
labels. Images are empty, and prices and purchase URLs are unset.

The JSON adapter validates the whole catalog at construction and serves an
immutable snapshot in catalog order. Reconstruct the container to load changed
data. Duplicate IDs or invalid records fail clearly rather than being skipped.
IDs are exact and case-sensitive; an empty catalog lists as an empty tuple.
Optional prices are CNY decimal strings in JSON (for example `"12.50"`), mapped to
`Decimal` in the domain. Missing IDs return `None` at the port and raise
`ProductNotFound` at the application use case.
