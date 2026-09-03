from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Product:
    """Canonical curated product value; optional prices are expressed in CNY."""

    id: str
    name: str
    category: str
    description: str
    origin: str
    cultural_background: str
    images: tuple[str, ...]
    usage: str
    ingredients: tuple[str, ...]
    price: Decimal | None = None
    purchase_url: str | None = None

    def __post_init__(self) -> None:
        for field in (
            "id",
            "name",
            "category",
            "description",
            "origin",
            "cultural_background",
            "usage",
        ):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be a nonblank string")
        if self.id != self.id.strip():
            raise ValueError("id must not contain surrounding whitespace")
        for field in ("images", "ingredients"):
            items = getattr(self, field)
            if not isinstance(items, tuple) or any(
                not isinstance(item, str) or not item.strip() for item in items
            ):
                raise ValueError(f"{field} must be a tuple of nonblank strings")
        if self.purchase_url is not None and (
            not isinstance(self.purchase_url, str) or not self.purchase_url.strip()
        ):
            raise ValueError("purchase_url must be a nonblank string or None")
        if self.price is not None:
            if not isinstance(self.price, Decimal) or not self.price.is_finite() or self.price < 0:
                raise ValueError("price must be a finite nonnegative Decimal or None")
            exponent = self.price.as_tuple().exponent
            if isinstance(exponent, int) and exponent < -2:
                raise ValueError("price must have at most two decimal places")
